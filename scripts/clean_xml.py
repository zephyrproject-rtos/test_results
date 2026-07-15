#!/usr/bin/env python3
"""Safer XML sanitizer for common ElementTree ParseError causes.

Fixes handled:
- strips characters illegal in XML 1.0
- escapes bare '&' in text and attribute values
- optional aggressive mode escapes stray '<' in text/attribute values
- preserves comments, CDATA, processing instructions, and DOCTYPE blocks
- validates the result with xml.etree.ElementTree

Usage:
  python xml_sanitizer_good.py input.xml
  python xml_sanitizer_good.py input.xml -o cleaned.xml
  python xml_sanitizer_good.py input.xml --in-place
  python xml_sanitizer_good.py input.xml --aggressive --show-context
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

INVALID_XML_10_RE = re.compile(
    "[\x00-\x08\x0B\x0C\x0E-\x1F\uD800-\uDFFF\uFFFE\uFFFF]"
)
BARE_AMP_RE = re.compile(r"&(?!#\d+;|#x[0-9A-Fa-f]+;|[A-Za-z_][A-Za-z0-9_.:-]*;)")
XML_DECL_ENCODING_RE = re.compile(
    br"<\?xml[^>]*encoding=[\"'](?P<enc>[A-Za-z0-9._-]+)[\"'][^>]*\?>",
    re.I,
)
NAME_START_RE = re.compile(r"[:A-Z_a-z]")
NAME_CHAR_RE = re.compile(r"[:A-Z_a-z0-9.\-]")


def detect_encoding(raw: bytes) -> str:
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if raw.startswith(b"\xff\xfe\x00\x00") or raw.startswith(b"\x00\x00\xfe\xff"):
        return "utf-32"
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return "utf-16"
    m = XML_DECL_ENCODING_RE.search(raw[:512])
    if m:
        try:
            return m.group("enc").decode("ascii")
        except Exception:
            pass
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            raw.decode(enc)
            return enc
        except UnicodeDecodeError:
            pass
    return "utf-8"



def decode_bytes(raw: bytes) -> tuple[str, str]:
    enc = detect_encoding(raw)
    try:
        return raw.decode(enc), enc
    except UnicodeDecodeError:
        return raw.decode(enc, errors="replace"), enc



def strip_invalid_xml_chars(text: str) -> tuple[str, int]:
    count = len(INVALID_XML_10_RE.findall(text))
    return INVALID_XML_10_RE.sub("", text), count



def find_tag_end(text: str, start: int) -> int:
    i = start
    n = len(text)
    quote = None
    while i < n:
        ch = text[i]
        if quote:
            if ch == quote:
                quote = None
        else:
            if ch in ('"', "'"):
                quote = ch
            elif ch == '>':
                return i
        i += 1
    return -1



def find_doctype_end(text: str, start: int) -> int:
    i = start
    n = len(text)
    quote = None
    bracket_depth = 0
    while i < n:
        ch = text[i]
        if quote:
            if ch == quote:
                quote = None
        else:
            if ch in ('"', "'"):
                quote = ch
            elif ch == '[':
                bracket_depth += 1
            elif ch == ']':
                if bracket_depth > 0:
                    bracket_depth -= 1
            elif ch == '>' and bracket_depth == 0:
                return i
        i += 1
    return -1



def sanitize_text_segment(segment: str, aggressive: bool, stats: dict[str, int]) -> str:
    bare = len(BARE_AMP_RE.findall(segment))
    if bare:
        stats['bare_ampersands_escaped'] += bare
        segment = BARE_AMP_RE.sub('&amp;', segment)
    if aggressive and '<' in segment:
        count = segment.count('<')
        stats['stray_lt_escaped'] += count
        segment = segment.replace('<', '&lt;')
    return segment



def sanitize_attribute_value(value: str, aggressive: bool, stats: dict[str, int]) -> str:
    bare = len(BARE_AMP_RE.findall(value))
    if bare:
        stats['bare_ampersands_escaped'] += bare
        value = BARE_AMP_RE.sub('&amp;', value)
    if '<' in value:
        count = value.count('<')
        stats['stray_lt_in_attributes_escaped'] += count
        value = value.replace('<', '&lt;')
    if aggressive and '>' in value:
        count = value.count('>')
        stats['gt_in_attributes_escaped'] += count
        value = value.replace('>', '&gt;')
    return value



def sanitize_tag(tag: str, aggressive: bool, stats: dict[str, int]) -> str:
    out: list[str] = []
    i = 0
    n = len(tag)
    while i < n:
        ch = tag[i]
        if ch in ('"', "'"):
            quote = ch
            j = i + 1
            while j < n and tag[j] != quote:
                j += 1
            if j >= n:
                value = tag[i + 1 :]
                sanitized = sanitize_attribute_value(value, aggressive, stats)
                out.append(quote + sanitized)
                i = n
                continue
            value = tag[i + 1 : j]
            sanitized = sanitize_attribute_value(value, aggressive, stats)
            out.append(quote + sanitized + quote)
            i = j + 1
        else:
            out.append(ch)
            i += 1
    return ''.join(out)



def looks_like_markup(text: str, lt_index: int) -> bool:
    if lt_index + 1 >= len(text):
        return False
    nxt = text[lt_index + 1]
    if nxt in ('/', '!', '?'):
        return True
    return bool(NAME_START_RE.match(nxt))



def sanitize_xml(text: str, aggressive: bool = False) -> tuple[str, dict[str, int]]:
    text, invalid_removed = strip_invalid_xml_chars(text)
    stats = {
        'invalid_xml_chars_removed': invalid_removed,
        'bare_ampersands_escaped': 0,
        'stray_lt_escaped': 0,
        'stray_lt_in_attributes_escaped': 0,
        'gt_in_attributes_escaped': 0,
    }

    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith('<!--', i):
            j = text.find('-->', i + 4)
            if j == -1:
                out.append(text[i:])
                break
            out.append(text[i:j + 3])
            i = j + 3
            continue

        if text.startswith('<![CDATA[', i):
            j = text.find(']]>', i + 9)
            if j == -1:
                out.append(text[i:])
                break
            out.append(text[i:j + 3])
            i = j + 3
            continue

        if text.startswith('<?', i):
            j = text.find('?>', i + 2)
            if j == -1:
                out.append(text[i:])
                break
            out.append(text[i:j + 2])
            i = j + 2
            continue

        if text.startswith('<!DOCTYPE', i) or text.startswith('<!doctype', i):
            j = find_doctype_end(text, i + 9)
            if j == -1:
                out.append(text[i:])
                break
            out.append(text[i:j + 1])
            i = j + 1
            continue

        if text[i] == '<' and looks_like_markup(text, i):
            j = find_tag_end(text, i + 1)
            if j == -1:
                out.append('&lt;')
                stats['stray_lt_escaped'] += 1
                i += 1
                continue
            tag = text[i:j + 1]
            out.append(sanitize_tag(tag, aggressive, stats))
            i = j + 1
            continue

        next_lt = text.find('<', i)
        if next_lt == -1:
            next_lt = n
        segment = text[i:next_lt]
        out.append(sanitize_text_segment(segment, aggressive, stats))
        i = next_lt

        if i < n and text[i] == '<' and not looks_like_markup(text, i):
            out.append('&lt;')
            stats['stray_lt_escaped'] += 1
            i += 1

    return ''.join(out), stats



def parse_ok(path: Path) -> tuple[bool, str | None]:
    try:
        ET.parse(path)
        return True, None
    except ET.ParseError as e:
        return False, str(e)



def show_error_context(path: Path, message: str, radius: int = 2) -> None:
    m = re.search(r'line (\d+), column (\d+)', message)
    if not m:
        print(f'Could not extract line/column from error: {message}', file=sys.stderr)
        return

    line_no = int(m.group(1))
    col_no = int(m.group(2))
    text = path.read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()
    start = max(1, line_no - radius)
    end = min(len(lines), line_no + radius)
    print('\nContext:', file=sys.stderr)
    for n in range(start, end + 1):
        prefix = '>' if n == line_no else ' '
        print(f'{prefix} {n:>6}: {lines[n - 1]}', file=sys.stderr)
        if n == line_no:
            print(' ' * 10 + ' ' * col_no + '^', file=sys.stderr)
            if col_no < len(lines[n - 1]):
                ch = lines[n - 1][col_no]
                print(f"{' ' * 10}char@col={ch!r} ord={ord(ch)}", file=sys.stderr)



def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f'{input_path.stem}.sanitized{input_path.suffix}')



def main() -> int:
    ap = argparse.ArgumentParser(description='Safer XML sanitizer for common ElementTree parse failures')
    ap.add_argument('input', type=Path, help='Input XML file')
    ap.add_argument('-o', '--output', type=Path, help='Output XML file')
    ap.add_argument('--in-place', action='store_true', help='Overwrite the input file')
    ap.add_argument('--aggressive', action='store_true', help='Also escape stray < in text and > in attribute values')
    ap.add_argument('--show-context', action='store_true', help='Show parse error context if parse still fails')
    args = ap.parse_args()

    if args.output and args.in_place:
        print('Use either --output or --in-place, not both.', file=sys.stderr)
        return 2

    input_path = args.input
    if not input_path.exists():
        print(f'Input file not found: {input_path}', file=sys.stderr)
        return 2

    out_path = input_path if args.in_place else (args.output or default_output_path(input_path))

    before_ok, before_err = parse_ok(input_path)
    if before_ok:
        print(f'Already parses cleanly: {input_path}')
        if not args.in_place and out_path != input_path:
            out_path.write_bytes(input_path.read_bytes())
            print(f'Copied unchanged to: {out_path}')
        return 0

    print(f'Original parse error: {before_err}')
    raw = input_path.read_bytes()
    text, enc = decode_bytes(raw)
    cleaned, stats = sanitize_xml(text, aggressive=args.aggressive)
    out_path.write_text(cleaned, encoding='utf-8', newline='')

    print(f'Detected encoding: {enc}')
    print(f'Wrote sanitized XML: {out_path}')
    print('Changes:')
    for k, v in stats.items():
        print(f'  - {k}: {v}')

    after_ok, after_err = parse_ok(out_path)
    if after_ok:
        print('Sanitized XML parses successfully with xml.etree.ElementTree')
        return 0

    print(f'Sanitized file still fails to parse: {after_err}', file=sys.stderr)
    if args.show_context:
        show_error_context(out_path, after_err)
    print(
        '\nLikely cause is structural XML damage (for example broken tags, mismatched nesting, or truncated content). '
        'A generic sanitizer can fix token-level problems, but not safely reconstruct missing structure.',
        file=sys.stderr,
    )
    return 1


if __name__ == '__main__':
    raise SystemExit(main())


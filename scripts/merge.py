#!/usr/bin/env python3


import os
import subprocess
import re
import argparse
import sys

CWD = os.getcwd()

def parse_args():
    parser = argparse.ArgumentParser(
                description="Merge junit files and generate report")
    parser.add_argument('-c', '--commit', default=None,
            help="Commit being reported.")
    parser.add_argument('-t', '--top', default=None,
            help="Location of junit files.")
    parser.add_argument('-o', '--output-dir', default=CWD,
            help="Output directory")

    return parser.parse_args()


def main():
    args = parse_args()

    if not args.top and not args.commit:
        sys.exit("Wrong options")

    results = {}

    for name in os.listdir(args.top):
        if not ".xml" in name:
            continue
        base, ext = os.path.splitext(name)
        idx = base.find(args.commit)
        platform = base[:idx-1]
        if results.get(platform):
            f = results[platform]
            f.append(os.path.join(args.top, name))
        else:
            results[platform] = [os.path.join(args.top, name)]


    for p in results:
        cmd = ['scripts/merge_junit.py']
        print(f"- Merging files for platform {p}...")
        files = sorted(results[p])
        cmd.extend(files)
        os.makedirs(args.output_dir, exist_ok=True)
        result_file = f"{args.output_dir}/{p}.xml"
        cmd.append(result_file)
        subprocess.run(cmd)
        content_new = None
        with open(result_file, "rt") as f:
            content = f.read()
            content_new = re.sub(r'classname="{}:'.format(p), r'classname="', content, flags = re.M)
        with open(result_file, "wt") as f:
            f.write(content_new)

if __name__ == "__main__":
    main()

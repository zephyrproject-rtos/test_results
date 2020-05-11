#!/usr/bin/env python3


import os
import re
import argparse
import sys

CWD = os.getcwd()

def parse_args():
    parser = argparse.ArgumentParser(
                description="Cleanup Junit")
    parser.add_argument('-j', '--junit-file', default=None,
            help="Location of junit file.")
    parser.add_argument('-o', '--output-dir', default=CWD,
            help="Output directory")

    return parser.parse_args()


def main():
    args = parse_args()

    if not args.junit_file or not args.output_dir:
        sys.exit(1)

    fn = os.path.basename(args.junit_file)
    platform, ext = os.path.splitext(fn)
    content_new = None
    with open(args.junit_file, "rt") as f:
        content = f.read()
        content_new = re.sub(r'classname="{}:'.format(platform), r'classname="', content, flags = re.M)
    with open(os.path.join(args.output_dir, fn), "wt") as f:
        f.write(content_new)

if __name__ == "__main__":
    main()

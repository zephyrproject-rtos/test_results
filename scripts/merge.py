#!/usr/bin/env python3


import os
import subprocess
import re

top="out"
version="zephyr-v2.2.0-2228-gfc828fde6f"
results = {}

# mps2_an385_zephyr-v2.2.0-2228-gfc828fde6f-3.xml
for root, dirs, files in os.walk(top, topdown=False):
    for name in files:
        if not ".xml" in name:
            continue
        base, ext = os.path.splitext(name)
        idx = base.find(version)
        platform = base[:idx-1]
        if results.get(platform):
            f = results[platform]
            f.append(os.path.join(root, name))
        else:
            results[platform] = [os.path.join(root, name)]


for p in results:
    cmd = ['scripts/merge_junit.py']
    print(f"Working on {p}...")
    files = sorted(results[p])
    cmd.extend(files)
    result_file = f"{p}-{version}.xml"
    cmd.append(result_file)
    subprocess.run(cmd)
    content_new = None
    with open(result_file, "rt") as f:
        content = f.read()
        content_new = re.sub(r'classname="{}:'.format(p), r'classname="', content, flags = re.M)
    with open(result_file, "wt") as f:
        f.write(content_new)



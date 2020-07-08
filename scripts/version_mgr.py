#!/usr/bin/env python3

import os
import sys
import json

from git import Repo, Git

VERSIONS_FILE = "versions.json"

repo = Repo(".")
g = Git(".")
version = g.describe("--all")

data = None
published = False
with open(VERSIONS_FILE, "r+") as versions:
    data = json.load(versions)
    if version in data:
        published = True
        print("version already published")
    else:
        print(f"New version {version}, adding to file...")

if data and published:
    with open(VERSIONS_FILE, "w") as versions:
        data.append(version)
        json.dump(data, versions)

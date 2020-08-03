#!/usr/bin/env python3

# Copyright (c) 2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    This script is used to get different tests delta between two xml files,
    ans save them into an output csv file.
    For example, sometimes we want to get the detailed tests difference
    between two xml files of same board with different commits,
    or same commit on different boards.

Example:
    ./check_delta.py -x xml_file_1 -x xml_file_2 -o test_delta.csv

Output:
    It will save the tests delta into a csv file under current work directory,
    and use flag to seperate them.
    flag 0 means this test only exists in the first xml_file_1,
    flag 1 means this test only exists in the second xml_file_2.
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET
import csv

CWD = os.getcwd()


def parse_args():
    parser = argparse.ArgumentParser(
            description="find different tests deltas with two xml files")
    parser.add_argument("-x", "--xml-file", default=None,
                        action="append", help="xml file path. This option "
                        "should be used twice.")
    parser.add_argument("-o", "--output-file",
                        default=os.path.join(CWD, "test_delta.csv"),
                        help="Output file")

    return parser.parse_args()


def get_tests_delta(xmlfiles, output):
    # get all testcases name
    tree_1 = ET.parse(xmlfiles[0])
    testsuite_1 = tree_1.getroot()[0]
    testcases_1 = testsuite_1.findall("testcase")
    testcase_names_1 = set()
    for item in testcases_1:
        testcase_names_1.add(item.attrib["name"])

    tree_2 = ET.parse(xmlfiles[1])
    testsuite_2 = tree_2.getroot()[0]
    testcases_2 = testsuite_2.findall("testcase")
    testcase_names_2 = set()
    for item in testcases_2:
        testcase_names_2.add(item.attrib["name"])

    # get addeed testcases name
    added_test_names = testcase_names_1.difference(testcase_names_2)
    # get removed testcases name
    removed_test_names = testcase_names_2.difference(testcase_names_1)

    # get tests delta
    # use flag to seperate them
    tests_delta = []
    for testcase in added_test_names:
        item = {}
        item["component"] = ".".join(testcase.split(".")[:-1])
        item["testcase"] = testcase
        item["flag"] = 0
        tests_delta.append(item)

    for testcase in removed_test_names:
        item = {}
        item["component"] = ".".join(testcase.split(".")[:-1])
        item["testcase"] = testcase
        item["flag"] = 1
        tests_delta.append(item)

    tests_delta.sort(key=lambda x: x["component"])
    fields = ["component", "testcase", "flag"]
    write_to_csv(output, fields, tests_delta)


def write_to_csv(filenames, csv_fields, csv_data):
    with open(filenames, "w+") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(csv_data)


def main():
    args = parse_args()

    if not args.xml_file or len(args.xml_file) != 2:
        print("Only support to compare two xml files")
        sys.exit(1)

    if not args.output_file:
        print("Need to set an output filename")
        sys.exit(1)

    get_tests_delta(args.xml_file, args.output_file)


if __name__ == "__main__":
    main()

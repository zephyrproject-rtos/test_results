from tables import *
import xml.etree.ElementTree as ET
from pathlib import Path
from argparse import ArgumentParser
from time import time
import os
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np


class Results(IsDescription):
    """
    This class describes the structure used to save results. Each field here
    is a column in the results table and the type of object it holds is also defined.
    """

    case_name = StringCol(50, pos=3)
    module = StringCol(50, pos=0)
    submodule = StringCol(25, pos=1)
    scenario = StringCol(25, pos=2)
    verdict = StringCol(8, pos=4)
    msg = StringCol(30, pos=6)
    execution_time = Float32Col(pos=5)


def parse_args():
    """Parse and return required limits from arguments"""
    argpar = ArgumentParser(description='Adds results from xml platform reports to HDF5 file')
    argpar.add_argument('-P', '--path', required=True, type=str, help='Path to the report which will be added')
    return argpar.parse_args()


def main(args):
    file_path = Path(args.path)
    add_results(file_path)


def add_results(file_path):
    # open h5 file in an append mode (create if needed)
    h5file = open_file("results.h5", mode="a", title="File with twister's results")

    if not file_path.exists():
        print(f"XML report not found at {file_path}")
        raise FileNotFoundError

    platform = file_path.name[:-4]

    # Load data from xml report
    try:
        testsuite = ET.parse(file_path).getroot()[0]
    except ET.ParseError:
        return "Corrupted file, skipping"


    properties = testsuite[0]
    if properties.tag != "properties":
        return  "Skipping old results without version"
    for property in properties:
        if property.attrib['name'] == "version":
            version = property.attrib['value']
            break


    # append/create a version table
    if version in h5file.root:
        print(f"Version {version} found, data will be appended")
        version_tab = h5file.root[version]
    else:
        print(f"Version {version} not found, new table will be crated")
        version_tab = h5file.create_group("/", version, f"Results for Zephyr version {version}")

    if platform in h5file.root[version]:
        print(f"Platform {platform} already exist for version {version}")
        print("Do you want to replace the existing results?")
        if input("y/n ?") == "y":
            print("Ok, results will be replaced")
            h5file.remove_node(f"/{version}/{platform}")
        else:
            print("Will break now")
            exit(1)

    start_time = time()
    # create a platform table
    platform_table = h5file.create_table(version_tab, f"{platform}", Results, f"Results from platform {platform}")

    # result will have a structure of a row from platform_table (Results class)
    result = platform_table.row
    for case in testsuite[1:]:
        name = case.attrib['name']
        test_case = name.rsplit(".", 1)[1]
        suite_name = case.attrib['classname']
        module, submodule = suite_name.split(".", 1)
        if len(module) > 50:
            print(module)
        if len(submodule) > 25:
            print(submodule)
        try:
            scenario = name.split(f"{suite_name}.")[1].rsplit(".", 1)[0]
            result['scenario'] = scenario
        except IndexError:
            # print(f"{name} has no sceario")
            result['scenario'] = "NAZ"
            pass

        result['module'] = module
        result['submodule'] = submodule
        result['case_name'] = test_case
        result['execution_time'] = case.attrib['time']
        if len(case) == 0:
            result['verdict'] = 'passed'
            result['msg'] = 'passed'
        else:
            result['verdict'] = case[0].attrib['type']
            result['msg'] = case[0].attrib['message']

        result.append()

    platform_table.flush()
    h5file.close()

if __name__ == "__main__":
    # args = parse_args()
    # main(args)
        
    dirs = [x[0] for x in os.walk("/home/maciej/zephyrproject2/test_results/results/")]
    for dir in dirs[1:]:
        files = [x[2] for x in os.walk(dir)]
        for file in files[0]:
            print(f"{dir}/{file}")
            file_path = Path(f"{dir}/{file}")
            add_results(file_path)

    # example of searching
    h5file = open_file("results.h5", mode="r", title="File with twister's results")
    verdicts = []
    durations = []
    start_time = time()
    condition = '''((module == 'kernel') & (submodule == 'memory_protection'))'''
    condition2 = '''((module == 'kernel') & (submodule == 'memory_protection') & (verdict == 'passed'))'''
    for ver in h5file.root:
        for plat in ver:
            #print(f"{ver}.{plat}")
            verdicts += [row['verdict'].decode() for row in plat.where(
                condition)]

            durations += [row['execution_time'] for row in plat.where(
                condition2)]

    print(len(durations))
    print(len(verdicts))
    print(time()-start_time)
    ver_cntr = Counter(verdicts)

    labels = []
    sizes = []

    for x, y in ver_cntr.items():
        labels.append(x)
        sizes.append(y)

    # Plot
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

    def func(pct, allvals):
        absolute = int(pct / 100. * np.sum(allvals))
        return "{:.1f}%\n{:d}".format(pct, absolute)


    wedges, texts, autotexts = ax.pie(ver_cntr.values(), autopct=lambda pct: func(pct, list(ver_cntr.values())),
                                      textprops=dict(color="w"))

    ax.legend(wedges, ver_cntr.keys(),
              title="Verdicts",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    plt.setp(autotexts, size=8, weight="bold")

    ax.set_title(f"Verdicts for {condition}")

    plt.figure()
    plt.hist(durations, bins=30)
    plt.xlabel('Time [s]')
    plt.ylabel('N')
    plt.title('Execution time for XXX')

    plt.show()
#!/usr/bin/env python3
# Copyright (c) 2021 NXP Corp.
# SPDX-License-Identifier: Apache-2.0
'''
    result parser
    command line:
        export GITHUB_ACCESS_TOKEN="<your access token>"
        python3 ./junit2issue.py -v <version_folder> -i <xml file> -r "your repo"
    e.g.
        python ./junit2issue.py -v zephyr-v2.6.0-286-g46029914a7ac -i mimxrt1015_evk.xml -r zephyrproject-rtos/test_results
    dependency:
        pip install --upgrade junitparser
        pip install PyGithub
    Note:
    1. You need create a "area: Tests" label for your report repo
    2. When the failure case name is found in open issues of your repo,
       a comment will be added to that issue, instead of reporting a new issue.
    3. When the failure case LOG is found same in open issues of your repo,
       a comment will be added to that issue, instead of reporting a new issue.

'''
import os
import sys
import logging
import argparse
import datetime

# pylint: disable=C0103,W0611

from string import Template

from junitparser import TestCase, JUnitXml, Skipped, Failure, Error, Properties

from github import Github

# Create the new element by subclassing Element or one of its child class,
# and add custom attributes to it.
class ZephyrTestCase(TestCase):
    '''
        Zephyr customized content
    '''

    GITHUB_ISSUE_COMMENTS_TEMPLETE = '''
    Also fails on ${PLATFORM} for ${ZEPHYR_VERSION}
    '''

    GITHUB_ISSUE_TITLE_TEMPLETE = '''
    tests-ci : ${MODULE}: ${SUBMODULE}: ${CASE_NAME} test ${RESULT}
    '''

    GITHUB_TEMPLETE = '''
    **Describe the bug**
    ${CASE_NAME} test is ${RESULT} on ${ZEPHYR_VERSION} on ${PLATFORM}

    see logs for details

    **To Reproduce**
    1. 
    ```
    scripts/twister --device-testing --device-serial /dev/ttyACM0 -p ${PLATFORM} \
     --sub-test ${APP_NAME}
    ```
    2. See error

    **Expected behavior**
    test pass

    **Impact**


    **Logs and console output**
    ```
    ${LOGS}
        
    ```

    **Environment (please complete the following information):**
     - OS: (e.g. Linux )
     - Toolchain (e.g Zephyr SDK)
     - Commit SHA or Version used: ${ZEPHYR_VERSION}
     '''

def parser_testsuites_for_result(xml, test_result):
    '''
        parser_testsuites_for_type
        @xml: input JUnitxml instance
        @test_result: test result type [Failure, Error, Skipped]
        return:
            a list of defined type cases info hash
    '''
    logging.info("check result with %s:", str(test_result))
    report_list = []
    version = "unknown"

    for suite in xml:
        # handle suites
        print("name = {}".format(suite.name))
        print("time = {}".format(suite.time))
        print("tests = {}".format(suite.tests))
        print("failures = {}".format(suite.failures))
        print("errors = {}".format(suite.errors))
        print("skipped = {}".format(suite.skipped))

        for prop in suite.child(Properties):
            print("{} : {}".format(prop.name, prop.value))
            version = prop.value

        for case in suite:
            # handle cases
            my_case = ZephyrTestCase.fromelem(case)
            for res in my_case.result:
                if isinstance(res, test_result):
                    print("+")
                    print("  " + my_case.classname)
                    print("  " + my_case.name)
                    print("  " + res.message)
                    info_array = my_case.name.split('.')
                    if len() > 2048:
                        _logs = ""
                        count = 0
                        nlines = len(res.text.splitlines())
                        for line in res.text:
                            if count < 1024:
                                _logs += line
                            elif count > nlines - 1024:
                                _logs += line
                            else:
                                pass
                    else:
                        _logs = res.text
                    report_case = {
                        'APP_NAME' : my_case.classname,
                        'MODULE' : info_array[0],
                        'SUBMODULE' : info_array[1],
                        'CASE_NAME' : ".".join(info_array[2:-1]),
                        'ZEPHYR_VERSION' : version,
                        'RESULT' : res.message,
                        'PLATFORM': suite.name,
                        'LOGS': _logs,
                    }
                    report_list.append(report_case)
                    # print("  " + res.text)
    return report_list

def gen_content_from_template(template, context):
    '''
        gen_content_from_template
        @template: in template string
        @context: in context
        return:
            generated issue content string
    '''
    _s = Template(template)
    content = _s.substitute(context)
    # logging.info(content)
    return content

def github_login():
    '''
        github_login
    '''

    access_token = os.getenv('GITHUB_ACCESS_TOKEN')

    if not access_token:
        print("no access token find in system environment variable\n")
        print("please set GITHUB_ACCESS_TOKEN with:\n")
        print("export GITHUB_ACCESS_TOKEN=<your github access token>\n")
        return None

    # using an access token
    return Github(access_token)

def check_issue_existing(repository, report):
    '''
        check whether the report issue exists
        @repository: in repo target
        @report: dict fo reporting content
        return:
            existing issue or None
    '''
    tod = datetime.datetime.now()
    d = datetime.timedelta(days=60)
    a = tod - d
    open_issues = repository.get_issues(state='open', since=a, labels=['bug'])
    for _issue in open_issues:
        if report['CASE_NAME'] in _issue.title:
            return _issue
        if report['LOGS'] and report['LOGS'] in _issue.body:
            return _issue

    return None

def get_desc_template():
    '''
        get_desc_template
    '''
    return ZephyrTestCase.GITHUB_TEMPLETE

def get_title_template():
    '''
        get_title_template
    '''
    return ZephyrTestCase.GITHUB_ISSUE_TITLE_TEMPLETE

def get_comments_template():
    '''
        get comments template
    '''
    return ZephyrTestCase.GITHUB_ISSUE_COMMENTS_TEMPLETE

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(filename)s:%(lineno)d] %(threadName)s %(message)s')

    auto_report = False
    parser = argparse.ArgumentParser(description='Process parameters')
    parser.add_argument('-v', '--vfolder', dest='vfolder', help='version folder')
    parser.add_argument('-i', '--pfile', dest='pfile', help='platform report file', required=True)
    parser.add_argument('-a', '--auto_report', dest='auto_report', default=False, action='store_true')
    parser.add_argument('-r', '--repo', dest='report_repo', help='report repo', required=True)
    parser.add_argument('-e', '--report', dest='report_errors', default=False, action='store_true')

    args = parser.parse_args()

    logging.info(args)
    pfile = args.pfile
    vfolder = args.vfolder
    auto_report = args.auto_report
    report_repo = args.report_repo
    report_errors = args.report_errors

    xml_file = os.path.join('..', 'results', vfolder, pfile)
    _xml = JUnitXml.fromfile(xml_file)
    reports = parser_testsuites_for_result(_xml, Failure)
    if report_errors:
        reports += parser_testsuites_for_result(_xml, Error)
    logging.info(len(reports))
    if not auto_report:
        print("Do you want to report issue?Y/N")
        _choose = input()
        if _choose not in ['y', 'Y']:
            print("Bye\n")
            sys.exit(0)

    g = github_login()
    repo = g.get_repo(report_repo)
    label1 = repo.get_label("area: Tests")
    label2 = repo.get_label("bug")
    _template = get_desc_template()
    _title_tmpl = get_title_template()
    _comment_tmpl = get_comments_template()

    for rep in reports:
        if not auto_report:
            print("\r\ndo you want to report? Y/N ", rep['CASE_NAME'])
            _choose = input()
            if _choose not in ['y', 'Y']:
                continue
        issue = check_issue_existing(repo, rep)
        if not issue:
            issue_content = gen_content_from_template(_template, rep)
            # logging.debug(issue_content)
            issue_title = gen_content_from_template(_title_tmpl, rep)
            repo.create_issue(title=issue_title, body=issue_content, labels=[label1, label2])
        else:
            logging.info(_title_tmpl)
            logging.info(rep)
            is_reported = False
            comments = issue.get_comments()
            for comment in comments:
                if rep['ZEPHYR_VERSION'] in comment.body \
                    and rep['PLATFORM'] in comment.body:
                    logging.info("already add commnets for this issue %s, %s, %s",
                                 issue.id, rep['ZEPHYR_VERSION'], rep['PLATFORM'])
                    is_reported = True
                    break
            if not is_reported:
                issue_title = gen_content_from_template(_comment_tmpl, rep)
                issue.create_comment(issue_title)

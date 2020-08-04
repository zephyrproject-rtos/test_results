#!/usr/bin/python3
import glob
import os
import argparse
import shutil
from git import Actor, Repo
import json
import sys
import logging
import configparser
import urllib.request
from github import Github

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def find_ver_json(commit_name):
    # Download versions.json and find commit name
    ver_url = 'https://testing.zephyrproject.org/daily_tests/versions.json'

    try:
        webURL = urllib.request.urlopen(ver_url)
        data = webURL.read()
        ver_data = json.loads(data)

        for ver_name in reversed(ver_data):
            if ver_name == commit_name:
                logging.info('Found existing version %s', ver_name)
                return ver_name

        # if no current version found in versions.json file after loop
        # interated all names in file -can't upload results, execution ended
        logging.critical("ERROR: Can't find %s in versions.json file "
                         "Script execution ended." % commit_name)
        sys.exit(1)
    except Exception:
        logging.critical("ERROR: Can't download versions.json file "
                         "Script execution ended.")
        sys.exit(1)


def parse_args():
    # Read arguments from the command line
    parser = argparse.ArgumentParser(description="Script to upload Test "
                                     "Results target.xml files to the "
                                     "test_results repo on Github")
    parser.add_argument('-c', "--commit_name",
                        help="Upload daily test results of that commit",
                        required=True)
    parser.add_argument('-j', '--res_dir',
                        help="Directory with all daily test result files",
                        required=True)
    parser.add_argument('-g', '--git_repo_dir',
                        help="Directory to place git repo test_results",
                        required=True)
    parser.add_argument('-t', '--title_msg', help="Title message",
                        required=True)
    parser.add_argument('-m', '--commit_msg', help="Commit message",
                        required=True)

    return parser.parse_args()


def git_repo_update(ver_folder_name, repo_dir, upstream_repo, origin_repo,
                    branch_git_title, commit_name, remote_name, origin_name):
    # Create if necessary or update test_results git repo on your computer
    if not os.path.exists(repo_dir):
        empty_repo = Repo.init(repo_dir)
        upstream = empty_repo.create_remote(remote_name, upstream_repo)

        logging.info('Creating new repository, please wait ...')
        assert upstream.exists()
        assert upstream == empty_repo.remotes.upstream == \
               empty_repo.remotes[remote_name]
        upstream.fetch()

        # Setup a local tracking branch of a remote branch

        # create local branch "master" from remote "master"
        empty_repo.create_head('master', upstream.refs.master)
        # set local "master" to track remote "master
        empty_repo.heads.master.set_tracking_branch(upstream.refs.master)
        # checkout local "master" to working tree
        empty_repo.heads.master.checkout()

        empty_repo.create_remote(origin_name, origin_repo)
        origin = Repo(os.path.join(repo_dir))
        logging.info('Push new repo updates to the origin ...')
        origin.git.push(origin_name, 'master')
    else:
        logging.info("Repository already created, let's update master...")
        # Use created repo to store results
        origin = Repo(os.path.join(repo_dir))
        upstream = Repo(os.path.join(repo_dir))
        origin.git.checkout('master')
        logging.info('Pull updates from the upstream ...')
        upstream.git.pull()
        logging.info('Push updates to the origin ...')
        origin.git.push(origin_name, 'master')

    try:
        # Create a new branch for daily master results
        new_branch_name = branch_git_title + commit_name
        origin.create_head(new_branch_name)
        logging.info('Checkout to the new branch %s', new_branch_name)
        origin.git.checkout(new_branch_name)
    except Exception:
        logging.info('Branch for the current commit exists, skip the step')

    # create full git directory path where your results will be stored
    git_dir_path = os.path.join(repo_dir, 'results', ver_folder_name)
    logging.info('Destination path to store file in Git %s', git_dir_path)

    if not os.path.exists(git_dir_path):
        os.mkdir(git_dir_path)
        logging.info('Path created %s', git_dir_path)
    else:
        logging.info('Path already existing')

    return git_dir_path, new_branch_name, origin


def add_push_to_github(git_dir_path, origin, branch_name, commit_msg,
                       title_msg, github_user, target_repo, github_token):
    # Add your test results to the repo, commit them and then push them
    # to create PR on Github
    for j in glob.glob("{}/*.xml".format(file_path)):
        file_name = os.path.basename((j))
        logging.info("File name %s", file_name)

        # Return path to its initial status
        source_file_path = argument.res_dir
        source_file_path = os.path.join(source_file_path, file_name)
        logging.info('Source directory file path %s', source_file_path)
        git_file_path = os.path.join(git_dir_path, file_name)
        logging.info('Destination path to file to commit %s', git_file_path)
        shutil.copy(source_file_path, git_file_path)
        origin.index.add(git_file_path)
    try:
        logging.info('Commit changes ...')
        author = Actor(author_name, author_email)
        full_title_msg = ver_folder_name + ": " + company_name + " " + \
            title_msg
        full_commit_msg = commit_msg + "\n\nSigned-off-by: " + author_name + \
            " " + author_email

        origin.git.commit('-m', full_title_msg + "\n\n" + full_commit_msg,
                          author=author)
        logging.info('Push commit to the origin ...')
        origin.git.push('origin', branch_name)
        logging.info('New branch pushed. Committing to Github successfully!')
        origin.git.checkout('master')

    except Exception:
        logging.critical('ERROR: Nothing to commit or " \
                         "Github repository has already the same branch')
        origin.git.checkout('master')
        sys.exit(1)

    try:
        # create PR from your Github repo to the target repo
        g = Github(github_token)
        repo = g.get_repo(target_repo)
        head = github_user + ":" + branch_name
        repo.create_pull(title=full_title_msg, body=full_commit_msg,
                         head=head, base="master")
        logging.info('Pull request created! Go to Github to view the details.')

    except Exception:
        logging.critical('ERROR: Failed to create Github PR " \
                         "to the target(upstream) repository " \
                         "from your origin repository')
        origin.git.checkout('master')
        sys.exit(1)


if __name__ == '__main__':
    # Step 1. Read setup variables from config.txt file
    config = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), 'config.txt')
    config.read_file(open(config_file))

    author_name = config.get('Credentials', 'author_name')
    author_email = config.get('Credentials', 'author_email')
    company_name = config.get('Credentials', 'company_name')
    upstream_repo = config.get('Git', 'upstream_repo')
    origin_repo = config.get('Git', 'origin_repo')
    branch_git_title = config.get('Git', 'branch_git_title')
    remote_name = config.get('Git', 'remote_name')
    origin_name = config.get('Git', 'origin_name')
    github_user = config.get('Github', 'github_user')
    target_repo = config.get('Github', 'target_repo')
    github_token = config.get('Github', 'github_token')

    # Step 2. Read passed arguments from the command line
    argument = parse_args()
    file_path = argument.res_dir
    logging.info('Initial test results path %s', file_path)
    repo_dir = argument.git_repo_dir
    # Step 2 finished

    if not os.path.exists(file_path):
        logging.critical('ERROR: File path to test results is not existing')
        sys.exit(1)

    # Step 3 Find version name in versions.json file
    ver_folder_name = find_ver_json(argument.commit_name)

    # Step 4. Create new or update test_results repository
    # and create branch for the results
    git_dir_path, branch_name, origin = git_repo_update(ver_folder_name,
                                                        repo_dir,
                                                        upstream_repo,
                                                        origin_repo,
                                                        branch_git_title,
                                                        argument.commit_name,
                                                        remote_name,
                                                        origin_name)

    # Step 5. Move files from your daily test directory to the git repository,
    # add, commit and then push them to Github
    add_push_to_github(git_dir_path, origin, branch_name, argument.commit_msg,
                       argument.title_msg, github_user, target_repo,
                       github_token)

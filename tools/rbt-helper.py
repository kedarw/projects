#!/usr/bin/env python

import subprocess
import sys
from itertools import izip as zip, count
import argparse
from argparse import RawTextHelpFormatter

# TODO:
# Add documentation
# Alias rbt-helper to "git postreview"

# define constants
R = '\033[31m'  # initialize red color
W = '\033[0m'  # no color for background
REVIEWERS_KEY = "Approved by:"
REVIEW_URL_KEY = "Reviewed at: "
WIKI_LINK_MSG = ""


# Validate
def validate_commit_message(commit, commit_description, commit_summary):
    jira_ids = ""
    error_msg = ""

    if commit_summary:
        # Validate if commit summary is as expected
        if len(commit_summary) > 0 and '[' not in commit_summary and ']' not in commit_summary:
            error_msg = error_msg + '\nGit commit summary does not contain JIRA ticket. Expected summary format: ' \
                                    '[DEVOPS-123] module: Ticket description'
        else:
            jira_ids = commit_summary[commit_summary.find("[") + len("["):commit_summary.rfind("]")]
            jira_ids = jira_ids.replace(" ", "")

    # Validate description is as expected
    reviewers = ""
    index = [i for i, j in zip(count(), commit_description) if REVIEWERS_KEY in j]
    if len(index) > 0:
        reviewers = commit_description[index[0]].split(':', 1)[1]
        reviewers = reviewers.rstrip()
        reviewers = reviewers.replace(" ", "")
    else:
        error_msg = error_msg + "\n'" + REVIEWERS_KEY + "' is missing from commit description"

    review_no = ""
    index = [i for i, j in zip(count(), commit_description) if REVIEW_URL_KEY in j]
    if len(index) > 0:
        review_url = commit_description[index[0]].split(':', 1)[1]
        review_url.replace(" ", "")
        review_no = filter(str.isdigit, review_url)
    else:
        error_msg = error_msg + "\n'" + REVIEW_URL_KEY + "' is missing from commit description"

    passed = True
    if len(error_msg) > 0 and len(reviewers) == 0:
        print ("\n" + R + "Commit: {} failed following validations:".format(commit) + error_msg + W)
        passed = False

    return (passed, jira_ids, reviewers, review_no)


def post(commit, commit_description, jira_ids, reviewers, review_no, repository, groups, skip_validations,
         publish_review):
    cmd = "git rev-list --parents -n 1 " + commit
    diff_str = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode("ascii").rstrip('\n')
    diff_str = diff_str.split(" ")

    repo = ""
    if repository is None and len(reviewers) == 0:
        cmd = "basename `git rev-parse --show-toplevel`"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        if int(retval) > 0:
            print R + "Unable to get repository name. Error: {}".formatp.stderr.read() + W
            sys.exit(int(retval))

        repo = p.stdout.read().decode("ascii").rstrip('\n')
    else:
        repo = repository

    if repository is not None and len(repository) > 0 and reviewers is not None and len(reviewers) > 0:
        publish_review = True

    if review_no is not None and len(review_no) > 0:
        print "Updating review: " + review_no
        cmd = "rbt post -r " + review_no + " --repository " + str(repo) + " -p " + diff_str[1] + ".." + diff_str[0]
    else:
        # Post review
        cmd = "rbt post -g "
        if reviewers is not None and len(reviewers) > 0:
            cmd = cmd + "--target-people {} ".format(reviewers)

        if jira_ids is not None and len(jira_ids) > 0:
            cmd = cmd + "--bugs-closed {} ".format(jira_ids)

        if groups is not None and len(groups) > 0:
            cmd = cmd + "--target-groups {}".format(groups)

        if publish_review:
            cmd = cmd + "-p "

        cmd = cmd + "--repository " + str(repo) + " " + diff_str[1] + ".." + diff_str[0]
        print cmd

    review_url = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.readlines()

    if review_no is not None and len(review_no) == 0:
        if len(review_url) >= 2:
            review_url = review_url[2]
            if publish_review:
                print "Posted new review: " + str(review_url)

                if not skip_validations:
                    cmd = 'git log -n 1 --pretty=format:"%H"'
                    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    retval = p.wait()
                    most_recent = p.stdout.read().decode("ascii").rstrip('\n')

                    if len(most_recent) > 7:
                        most_recent = most_recent[:7]

                        if commit == most_recent:
                            commit_description = [w.replace(REVIEW_URL_KEY + "\n", REVIEW_URL_KEY + " " + review_url)
                                                  for w in commit_description]
                            commit_text = "".join(commit_description)
                            cmd = "git commit --amend -m '" + commit_text + "'"
                            subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.readlines()
            else:
                print 'Posted new draft: ' + str(review_url.rstrip()) + ', please update fields appropriately and publish'


# Post commits to review board
def post_review(start_commit, end_commit, skip_validations, repository, people, groups, bugs):
    cmd = ""

    if not start_commit:
        cmd = "git log HEAD~1..HEAD~0 --oneline | cut -d ' ' -f 1"
    elif end_commit:
        cmd = "git log {}^..{} --oneline | cut -d ' ' -f 1".format(start_commit, end_commit)
    else:
        cmd = "git log {}^..{} --oneline | cut -d ' ' -f 1".format(start_commit, start_commit)

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    commit_array = []
    for line in p.stdout.readlines():
        l = line.decode('ascii')
        commit_array.append(l.rstrip('\n'))

    retval = p.wait()

    commit_array.reverse()
    for commit in commit_array:
        cmd = "git log -n 1 --pretty=format:%B " + commit
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        if int(retval) > 0:
            print R + "Unable to get commit message for commit: {}. Error: {}".format(commit, p.stderr.read()) + W
            sys.exit(int(retval))

        commit_description = p.stdout.readlines()
        commit_summary = commit_description[0].strip()

        if skip_validations:
            post(commit, None, bugs, people, None, repository, groups, skip_validations, False)
        else:
            passed = False
            passed, jira_ids, reviewers, review_no = validate_commit_message(commit, commit_description, commit_summary)
            if passed:
                post(commit, commit_description, jira_ids, reviewers, review_no, repository, groups, skip_validations,
                     True)  # post and publish
            else:
                # Post but dont publish
                post(commit, None, jira_ids, reviewers, review_no,  repository, groups, skip_validations, False)


def parse_arguments():
    example = "E.g: \n python tools/rbt-helper.py -s 90aa0ad0 -e 18834aec \
                \n python tools/rbt-helper.py -s 90aa0ad0 \
                \n python tools/rbt-helper.py -s 90aa0ad0 -f \n"
    parser = argparse.ArgumentParser(add_help=False, epilog=example, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-s', '--start', action='store', dest='start_commit', default=None,
                        help='Start or first commit which you need to include in review. If only start is\nprovided '
                             'script just posts one commit for review')
    parser.add_argument('-e', '--end', action='store', dest='end_commit', default=None,
                        help='End or last commit which you need to include in review')
    parser.add_argument('-r', '--repository', action='store', dest='repository', default=None,
                        help='Repository review is based off')
    parser.add_argument('-p', '--people', action='store', dest='people', default=None,
                        help='Reviewers you need to include in review')
    parser.add_argument('-g', '--groups', action='store', dest='groups', default=None,
                        help='Groups you need to include in review')
    parser.add_argument('-b', '--bugs', action='store', dest='bugs', default=None,
                        help='Bugs you need to include in review')
    parser.add_argument('-f', '--force', action='store_true', dest='skip_validations',
                        help='Bypass all commit message validations and just post review. Not recommended')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, dest='help',
                        help='This script posts commits as per inputs to review board.')
    args = parser.parse_args()

    return parser, args


def main():
    parser, args = parse_arguments()  # Parse arguments

    start_commit = args.start_commit
    end_commit = args.end_commit
    skip_validations = args.skip_validations
    repository = args.repository
    people = args.people
    groups = args.groups
    bugs = args.bugs

    if end_commit and not start_commit:
        print (R + "\nInvalid arguments. Please provide start commit\n" + W)
        sys.exit(1)

    post_review(start_commit, end_commit, skip_validations, repository, people, groups, bugs)


if __name__ == "__main__":

    main()

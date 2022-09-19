#!/usr/bin/env python
from datetime import datetime
from numpy import isnan
import pandas as pd
import random
import sys
import os
import subprocess

info = {}


def populate_info():
    if len(sys.argv) < 2:
        print("Usage: grade_repos basefolder [path/to/rubric.md]")
        print("Put both the blackboard spreadsheet and github csv in basefolder")
        sys.exit()

    basefolder = sys.argv[1]

    if len(sys.argv) > 2:
        rubric_f = os.path.abspath(sys.argv[2])
    else:
        rubric_f = None

    # Try to open the two csvs
    subdirs = os.listdir(basefolder)
    # find the file with the same first few characters as the classroom folder
    classroom_folder = os.path.basename(os.path.normpath(basefolder))
    gh_prefix = classroom_folder[:3]
    autogrades_f = None
    bb_grades_f = None
    print(f"Searching for {gh_prefix} in subdirs")
    for s in subdirs:
        if s[:3] == gh_prefix:
            autogrades_f = os.path.join(basefolder, s)
        if s[:2] == "gc":
            bb_grades_f = os.path.join(basefolder, s)

    if not (autogrades_f):
        print("Couldn't find github csv in", basefolder)
        sys.exit()
        
    if not (bb_grades_f):
        print("Couldn't find Blackboard spreadsheet in", basefolder)
        sys.exit()

    try:
        autogrades = pd.read_csv(autogrades_f)
        bb_grades = pd.read_csv(bb_grades_f, delimiter="\t", encoding="UTF-16")
    except Exception as e:
        print(e)
        sys.exit()

    current_user = subprocess.check_output(
        ["git", "config", "--get", "user.name"], universal_newlines=True
    ).strip()

    current_email = subprocess.check_output(
        ["git", "config", "--get", "user.email"], universal_newlines=True
    ).strip()

    cwd = os.getcwd()

    # get the lab/assignment title and deadline
    a_title = input("Enter the assignment title: ")
    deadline = input("Enter the assignment deadline as yyyy-mm-dd (if any): ")

    # get some options
    randomize = input("Do you want to randomize? Y/N: ")
    show_commits = input("Do you want to see the student" "s commits? Y/N: ")

    # update the global info
    # update the global info
    global info
    info["autogrades"] = autogrades
    info["bb_grades_f"] = bb_grades_f
    info["bb_grades"] = bb_grades
    info["basefolder"] = basefolder
    info["rubric_f"] = rubric_f
    info["current_user"] = current_user
    info["current_email"] = current_email
    info["cwd"] = cwd
    info["a_title"] = a_title
    info["deadline"] = deadline
    info["randomize"] = randomize.lower() == "y"
    info["show_commits"] = show_commits.lower() == "y"


def needs_grading(repo, autograde_row):
    if not os.path.isdir(os.path.join(info["basefolder"], repo)):
        return False

    if autograde_row.empty:
        print(repo + " not found in autograde list, must be done manually")
        return False

    grade = (
        info["bb_grades"]
        .loc[
            info["bb_grades"]["roster_name"] == autograde_row.roster_identifier,
            info["a_title"],
        ]
        .item()
    )

    if grade is not None and not isnan(grade):
        print("Already graded " + repo + ", skipping")
        return False

    return True


def get_commits():
    # check if the user made any commits
    commits = (
        subprocess.check_output(
            [
                "git",
                "rev-list",
                "--reverse",
                r"--format=%aN %aE%n%ad%n%s%n-*-*-",
                "--all",
            ],
            universal_newlines=True,
        )
        .strip()
        .split("-*-*-\n")
    )
    commits = [
        c
        for c in commits
        if info["current_user"] not in c
        and info["current_email"] not in c
        and "classroom[bot]" not in c
    ]
    return commits


def copy_rubric():
    if info["rubric_f"] is not None:
        feedback = "feedback.md"
        print(f'Copying {info["rubric_f"] } to {feedback}')
        subprocess.call(["cp", info["rubric_f"], feedback])


def strip_tokens_from_url():
    url = subprocess.check_output(
        r"git config --get remote.origin.url | sed 's/.*@/https:\/\//g'",
        shell=True,
        universal_newlines=True,
    ).strip()
    subprocess.call(["git", "remote", "set-url", "origin", url], shell=True)
    return url.replace(".git", "")


def main():
    populate_info()

    # concatenate first and last name from bb to match roster in autogrades
    info["bb_grades"]["roster_name"] = (
        info["bb_grades"]["First Name"] + " " + info["bb_grades"]["Last Name"]
    )

    if info["a_title"] not in info["bb_grades"].columns:
        info["bb_grades"][info["a_title"]] = None

    # count how many left to do
    total_grades = len(info["bb_grades"][info["a_title"]])
    completed = info["bb_grades"][info["a_title"]].count()

    # Start looping through student repos (optionally randomized)
    repos = [f for f in os.listdir(info["basefolder"])]
    if info["randomize"]:
        random.shuffle(repos)

    for repo in repos:
        autograde_row = (
            info["autogrades"]
            .loc[info["autogrades"]["github_username"] == repo]
            .squeeze()
        )
        if not needs_grading(repo, autograde_row):
            continue

        os.chdir(os.path.join(info["basefolder"], repo))

        commits = get_commits()
        if len(commits) == 0:
            print(repo + " has no commits, skipping")
            os.chdir(info["cwd"])
            continue

        copy_rubric()

        # get the base URL without the .git part
        url = strip_tokens_from_url()

        if not info["deadline"]:
            # just open the feedback pr to the files view
            subprocess.call(["start", url + "/pull/1/files"], shell=True)
        else:
            # get the hash associated with the deadline (up to midnight)
            sha_deadline = subprocess.check_output(
                [
                    "git",
                    "log",
                    '--until="' + info["deadline"] + '23:59"',
                    "--format=format:%H -1",
                ],
                universal_newlines=True,
            ).strip()

            # and the initial commit
            git_list = subprocess.Popen(
                ["git", "rev-list", "HEAD"], stdout=subprocess.PIPE
            )
            sha_init = subprocess.check_output(
                ["tail", "-n", "1"], stdin=git_list.stdout, universal_newlines=True
            ).strip()
            git_list.wait()

            # compare the code at the deadline to the initial commit
            subprocess.call(
                ["start", url + "/compare/" + sha_init + "..." + f"{sha_deadline}"],
                shell=True,
            )

        # show the first commit if requested
        if info["show_commits"]:
            for commit in commits:
                print("------------------------------")
                print(commit)

        # Run the test code
        subprocess.call(["python", "-m", "unittest"], shell=True)
        print("*** Done tests ***")

        # Show autograde points, then open up a feedback file and wait for input
        print("Autograde points for " + repo + ": " + str(autograde_row.points_awarded))

        subprocess.call(["code", "--reuse-window", "feedback.md"], shell=True)
        grade = input(
            f'Enter the grade for {repo} {info["a_title"]} ({completed}/{total_grades}): '
        )
        completed += 1

        # go back to the working directory so file paths work
        os.chdir(info["cwd"])

        # store it in the blackboard grade row and save it
        info["bb_grades"].loc[
            info["bb_grades"]["roster_name"] == autograde_row.roster_identifier,
            info["a_title"],
        ] = grade
        info["bb_grades"].to_csv(
            info["bb_grades_f"], sep="\t", encoding="UTF-16", index=False
        )

        if input("Press Q to quit, or anything else to continue: ") == "Q":
            break


if __name__ == "__main__":
    main()

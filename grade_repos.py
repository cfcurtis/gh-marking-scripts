from datetime import datetime
from numpy import isnan
import pandas as pd
import random
import sys
import os
import subprocess

if __name__ == '__main__':
    if (len(sys.argv) < 4):
        print("Usage: grade_repos basefolder autogrades.csv blackboardgrades.csv")
    
    basefolder = sys.argv[1]
    autogrades_f = sys.argv[2]
    bb_grades_f = sys.argv[3]
 
    # Try to open the two csvs
    autogrades = pd.read_csv(autogrades_f)
    bb_grades = pd.read_csv(bb_grades_f,delimiter='\t',encoding='UTF-16')

    # concatenate first and last name from bb to match roster in autogrades
    bb_grades['roster_name'] = bb_grades['First Name'] + ' ' + bb_grades['Last Name']

    # get the lab/assignment title and deadline
    a_title = input('Enter the assignment title: ')
    deadline = input('Enter the assignment deadline as yyyy-mm-dd (if any): ')

    # get some options
    randomize = input('Do you want to randomize? Y/N: ')
    first_commit = input('Do you want to see the student''s first commit? Y/N: ')

    if a_title not in bb_grades.columns:
        bb_grades[a_title] = None
 
    # count how many left to do
    total_grades = len(bb_grades[a_title])
    completed = bb_grades[a_title].count()

    # Start looping through student repos in random order
    repos = [f for f in os.listdir(basefolder)]

    if randomize.lower() == 'y':
        random.shuffle(repos)
    
    cwd = os.getcwd()

    for repo in repos:
        fullpath = os.path.join(basefolder,repo)
        if not os.path.isdir(fullpath):
            continue

        # get the corresponding username
        autograde_row = autogrades.loc[autogrades['github_username'] == repo].squeeze()
        if autograde_row.empty:
            print(repo + ' not found in autograde list, must be done manually')
            continue

        grade = bb_grades.loc[bb_grades['roster_name'] == autograde_row.roster_identifier,a_title].item()
        if grade is not None and not isnan(grade):
            print('Already graded ' + repo + ', skipping')
            continue

        os.chdir(fullpath)
        
        # get the base URL without the .git part
        url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], universal_newlines=True).strip()
        url = url.replace('.git','')

        if not deadline:
            # just open the feedback pr to the files view
            subprocess.call(['start', url + '/pull/1/files'],shell=True)
        else:
            # get the hash associated with the deadline (up to midnight)
            sha_deadline = subprocess.check_output(['git', 'log', '--until="' + 'deadline' + '23:59"', '--format=format:%H -1'], universal_newlines=True).strip()

            # and the initial commit
            git_list = subprocess.Popen(['git', 'rev-list', 'HEAD'], stdout=subprocess.PIPE)
            sha_init = subprocess.check_output(['tail', '-n', '1'], stdin=git_list.stdout, universal_newlines=True).strip()
            git_list.wait()
            
            # compare the code at the deadline to the initial commit
            subprocess.call(['start', url + '/compare/' + sha_init + '...' + 'sha_deadline'],shell=True)
        
        # show the first commit if requested
        if first_commit.lower() == 'y':
            git_log = subprocess.Popen('git rev-list --reverse --pretty --invert-grep ' +
                '--author="\(classroom\)\|\(Charlotte\)" HEAD', 
                stdout=subprocess.PIPE, shell=True)
            subprocess.call(['head','-n','5'],stdin=git_log.stdout, universal_newlines=True)

        # Show autograde points, then open up a feedback file and wait for input
        print('Autograde points for ' + repo + ': ' + str(autograde_row.points_awarded))
        subprocess.call(['code','feedback.md'],shell=True)
        grade = input(f'Enter the grade for {repo} {a_title} ({completed}/{total_grades}): ')
        completed += 1

        # go back to the working directory so file paths work
        os.chdir(cwd)

        # store it in the blackboard grade row and save it
        bb_grades.loc[bb_grades['roster_name'] == autograde_row.roster_identifier,a_title] = grade
        bb_grades.to_csv(bb_grades_f,sep='\t', encoding='UTF-16', index=False)

        input('Press any key to continue, or Ctrl+C to quit')

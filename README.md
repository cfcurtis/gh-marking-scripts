# gh-marking-scripts
Helper scripts to make marking and adding feedback a little easier. These scripts assume that you enabled the automatic pull request for feedback on assignment creation, and that you have downloaded student repos using GitHub [classroom assistant](https://classroom.github.com/assistant).

## grade_repos.sh
Usage: grade_repos.sh folder [start]

Loops through all the student repos contained in `folder`, starting at an optional `start` index. It prints out the index, the repo name (student GitHub username), and opens PR 1 in the web interface. It also opens a text file called "feedback.txt" in VS Code and waits for you to fill it in. It then prompts for the grade and adds it to a spreadsheet, then asks if you want to continue. If you stop halfway through with Ctrl+C, you can start where you left off by passing the `start` index argument.

## push_feedback.sh
Usage: push_feedback.sh folder

After writing comments in text files for each student repo, use this script to loop through and add all the comments to the feedback PR.

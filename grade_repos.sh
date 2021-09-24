#!/usr/bin/bash

cd $1
COUNTER=0
START=0

if [[ "$#" -gt 1 ]]; then
	START=$2
fi

for repo in */; do
	COUNTER=$[$COUNTER + 1]
	if [ $COUNTER -ge $START ]; then
		echo "$COUNTER: $repo"
		cd $repo

		# view the feedback pr on the web interface
		gh pr view 1 --web

		# Open the text file for feedback
		code -w feedback.txt
		
		cd ..

		# prompt for the grade and store to csv
		read -p "Enter the grade for this assignment: " grade
		echo "$repo, $grade" >> grades.csv
		
		# make sure we want to continue
		read -p "Press enter to continue"
	fi
done
	
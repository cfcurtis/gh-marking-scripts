#!/usr/bin/bash

cd $1
COUNTER=0
START=0

if [[ "$#" -gt 1 ]]; then
	START=$2
fi

read -p "What is the assignment deadline? (format yyyy-mm-dd) " deadline

for repo in */; do
	COUNTER=$[$COUNTER + 1]
	if [ $COUNTER -ge $START ]; then
		echo "$COUNTER: $repo"
		cd $repo

		# get the hash associated with the deadline (up to midnight)
		sha_deadline=`git log --until="$deadline 23:59" --format=format:%H -1`

		# and the initial commit
		sha_init=`git rev-list HEAD | tail -n 1`

		# and the base URL without the .git part
		url=`git config --get remote.origin.url`
		
		# compare the code at the deadline to the initial commit
		start "${url%.*}/compare/$sha_init...$sha_deadline"

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
	

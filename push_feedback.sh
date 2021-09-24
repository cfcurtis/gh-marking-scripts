#!/usr/bin/bash

cd $1
COUNTER=0

for repo in */; do
	COUNTER=$[$COUNTER + 1]
    echo "$COUNTER: $repo"
    cd $repo

    # comment on the feedback from the feedback file
    gh pr comment 1 -F feedback.txt
    cd ..
done
	
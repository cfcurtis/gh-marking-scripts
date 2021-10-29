#!/usr/bin/bash

# Usage: apply_patch basedir patchname

cd $1
COUNTER=0

read -p "Enter the repo prefix (org/prefix): " prefix
read -p "Enter the commit message: " message

for repo in */; do
	COUNTER=$[$COUNTER + 1]
    echo "$COUNTER: $repo"
    cd $repo

    # apply the patch file specified in $2
    git apply $2
    git add .
    git commit -m "$message"

    # update the remote with the repo name
    git remote set-url origin "https://github.com/$prefix-$repo"
    git pull
    git push
    cd ..
done
	
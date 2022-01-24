#!/usr/bin/bash

# Usage: apply_patch basedir patchname

cd $1
COUNTER=0

read -p "Do you want to commit the patch? (y/n): " commit

if [[ $commit == "y" ]]; then
    read -p "Enter the commit message: " message
fi

for repo in */; do
	COUNTER=$[$COUNTER + 1]
    echo "$COUNTER: $repo"
    cd $repo

    # apply the patch file specified in $2
    git apply --reject --whitespace=fix $2

    if [[ $commit == "y" ]]; then
        git add .
        git commit -m "$message"
        git pull
        git push
    fi
    cd ..
done
	
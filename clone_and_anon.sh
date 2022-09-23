#!/usr/bin/bash

# Usage: clone_and_anon org prefix filter1 filter2 ... filterN
# Clones all the repos from org matching the filter(s). 
# Creates folder named prefix, renames repos as prefix-number,
# then deletes .git directory to remove identifying information.
# This does not anonymize any student names/IDs on text files within the repo.

org=$1
prefix=$2
args=("${@:3}")
dryrun=0

cmd="gh repo list $org -L 2000 | grep"
for arg in "${args[@]}"; do
    if [[ $arg == "-n" ]]; then
        dryrun=1
    else
        cmd="$cmd -e $arg"
    fi
done

if [[ $dryrun == 1 ]]; then
    echo "Dry run, just listing repos"
else
    mkdir $prefix
    cd $prefix
fi

counter=0
eval $cmd | while read -r repo _; do
    if [[ $dryrun == 1 ]]; then
        echo "would clone $repo"
    else
        gh repo clone $repo "$prefix-$counter"
        rm -rf "$prefix-$counter/.git"
        counter=$[$counter + 1]
    fi
done

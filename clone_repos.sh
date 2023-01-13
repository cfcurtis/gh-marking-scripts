#!/usr/bin/bash

# Clones all the repos from org matching the filter(s)t

if [ $# -lt 3 ]; then
    echo "Usage: $0 org prefix filter1 filter2 ... filterN"
    exit 1
fi

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

eval $cmd | while read -r repo _; do
    if [[ $dryrun == 1 ]]; then
        echo "would clone $repo"
    else
        gh repo clone $repo
    fi
done

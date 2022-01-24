#!/bin/bash

cd $1

for repo in `ls -d */`; do
    cd $repo
    echo $repo
    if ls *.py 1> /dev/null 2>&1; then
        python *.py
    elif  ls *.txt 1> /dev/null 2>&1; then
        python *.txt
    else
        echo "*** Missing Python File ***"
    fi
    echo " "
    cd ..
done
    
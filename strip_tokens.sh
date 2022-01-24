#!/bin/bash

cd $1

for repo in `ls -d */`; do
    cd $repo
    url=$(git config --get remote.origin.url | sed 's/.*@/https:\/\//g')
    git remote set-url origin $url
    git pull
    cd ..
done
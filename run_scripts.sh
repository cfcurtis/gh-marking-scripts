#!/bin/bash

# usage: ./run_scripts.sh base_dir script_name [user_inputs.txt]
# where:
#   base_dir is the directory containing all student repose
#   script_name is the Python script to run (including .py)
#   user_inputs.txt is an optional file containing user inputs to the script, one per line

cd $1
SCRIPT_NAME=$2

if [[ "$#" -gt 2 ]]; then
	INPUT_FILE="`pwd`/$3"
else
    INPUT_FILE=/dev/null
fi


for repo in `ls -d */`; do
    cd $repo
    echo $repo
    if ls "$SCRIPT_NAME" 1> /dev/null 2>&1; then
        python "$SCRIPT_NAME" < "$INPUT_FILE"
    else
        echo "*** Missing Python File ***"
    fi
    echo " "
    cd ..
done
    
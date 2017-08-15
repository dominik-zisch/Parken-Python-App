#!/bin/bash

NATIVE_APP='python_test'
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

##### Main

while true; do

    echo "Checking for updates"
    sh $SCRIPT_DIR/pull_git_native.sh
    echo "Restarting native app!"
    python $ROOT_DIR/$NATIVE_APP.py
    echo "Main app ended..."
    echo "-----------------------------------"
    read -t 2 -p "Restarting the native app in 2 seconds. Press <CTRL>+c to stop."
    echo "-----------------------------------"

done 


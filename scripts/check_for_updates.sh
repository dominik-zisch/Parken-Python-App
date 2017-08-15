#!/bin/sh

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

while true; do

    echo "Checking for updates..."
    git -C $ROOT_DIR fetch

    LOCAL=$(git -C $ROOT_DIR rev-parse HEAD)
    REMOTE=$(git -C $ROOT_DIR rev-parse origin/master)

    if [ $LOCAL = $REMOTE ]; then
        echo "Up-to-date"
    else
        echo "Need to pull"
        sh $SCRIPT_DIR/kill_native.sh
    fi
    echo "-----------------------------------"
    read -t 10 -p "Restarting the update app in 10 seconds. Press <CTRL>+c to stop."
    echo "-----------------------------------"

done 














    
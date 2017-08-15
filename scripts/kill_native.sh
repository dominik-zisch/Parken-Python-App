#!/bin/sh

NATIVE_APP='python_test'

function kill_process () {
    ps axf | grep $1 | grep -v grep | awk '{print "kill -9 " $1}' | sh
}

echo "Killing native app!"

kill_process $NATIVE_APP
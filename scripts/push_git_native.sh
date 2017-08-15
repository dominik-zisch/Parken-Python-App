#!/bin/sh

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

git -C $ROOT_DIR add .
git -C $ROOT_DIR commit -m "."
git -C $ROOT_DIR push origin master
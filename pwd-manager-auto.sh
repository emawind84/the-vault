#!/bin/bash

set -e

SCRIPT_BASE_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
SCRIPT_NAME="${0##*/}"

export PATH="$SCRIPT_BASE_PATH/env/bin:$SCRIPT_BASE_PATH:$PATH"

cd $SCRIPT_BASE_PATH

python manage.py runserver 0.0.0.0:8091

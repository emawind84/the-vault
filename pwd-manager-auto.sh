#!/bin/bash

set -e

SCRIPT_BASE_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
SCRIPT_NAME="${0##*/}"

export PATH="$SCRIPT_BASE_PATH/env/bin:$SCRIPT_BASE_PATH:$PATH"

cd $SCRIPT_BASE_PATH

SERVER_ADDRPORT="${SERVER_ADDRPORT:-0.0.0.0:8091}"
python manage.py runserver $SERVER_ADDRPORT

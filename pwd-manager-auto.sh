#!/usr/bin/env bash

set -e

SCRIPT_BASE_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
SCRIPT_NAME="${0##*/}"
PYTHON_ENV="${PYTHON_ENV:-env}"

export PATH="$PYTHON_ENV/bin:$SCRIPT_BASE_PATH:$PATH"

cd $SCRIPT_BASE_PATH

source $PYTHON_ENV/bin/activate

python manage.py migrate
python manage.py collectstatic

if [ $# -eq 0 ]; then
    SERVER_ADDRPORT="${SERVER_ADDRPORT:-0.0.0.0:8091}"
    exec python manage.py runserver $SERVER_ADDRPORT
fi

exec python manage.py "$@"
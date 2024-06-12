#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
PROJ_DIR=$( cd -- "$( dirname -- "$( dirname -- "${BASH_SOURCE[0]}" )" )" &> /dev/null && pwd )
export PYTHONPATH="$PROJ_DIR:$PROJ_DIR/.venv/lib/python3.12/site-packages"
if python3 -m ats.collection.symbol_change_query >> /var/log/ats/symbol_change_schedule_log.txt 2>&1; then
    python3 -m ats.database.symbol_change_update >> /var/log/ats/symbol_change_schedule_log.txt 2>&1
# else
#     >> log.txt
#     echo "Failure" >> log.txt 
fi

exit 0

#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
PROJ_DIR=$( cd -- "$( dirname -- "$( dirname -- "${BASH_SOURCE[0]}" )" )" &> /dev/null && pwd )
export PYTHONPATH="$PROJ_DIR:$PROJ_DIR/.venv/lib/python3.12/site-packages"
python3 -m ats.collection.constituent_api_query >> /var/log/ats/constituent_schedule_log.txt 2>&1;

exit 0
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
PROJ_DIR=$( cd -- "$( dirname -- "$( dirname -- "${BASH_SOURCE[0]}" )" )" &> /dev/null && pwd )
export PYTHONPATH="$PROJ_DIR:$PROJ_DIR/.venv/lib/python3.12/site-packages"
if python3 -m ats.collection.bonds_api_query >> /var/log/ats/bonds_schedule_log.txt 2>&1; then
    # Bonds
    python3 -m ats.database.bonds_insert >> /var/log/ats/bonds_schedule_log.txt 2>&1
fi

exit 0

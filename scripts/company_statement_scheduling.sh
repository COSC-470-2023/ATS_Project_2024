#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
PROJ_DIR=$( cd -- "$( dirname -- "$( dirname -- "${BASH_SOURCE[0]}" )" )" &> /dev/null && pwd )
export PYTHONPATH="$PROJ_DIR:$PROJ_DIR/.venv/lib/python3.12/site-packages"
if python3 -m ats.collection.company_info_api_query >> /var/log/ats/company_statements_schedule_log.txt 2>&1; then
    # Insert company statements
    python3 -m ats.database.company_statements_insert >> /var/log/ats/company_statements_schedule_log.txt 2>&1
fi

exit 0

#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
export PYTHONPATH="/home/admin/Projects/ATS_Project_2024/:/home/admin/Projects/ATS_Project_2024/venv/lib/python3.12/site-packages"
if python3 -m ats.collection.company_info_api_query >> /var/log/ats/company_statements_schedule_log.txt 2>&1; then
    # Insert company statements
    python3 -m ats.database.company_statements_insert >> /var/log/ats/company_statements_schedule_log.txt 2>&1
fi

exit 0

#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
export PYTHONPATH="/home/admin/Projects/ATS_Project_2024/:/home/admin/Projects/ATS_Project_2024/venv/lib/python3.12/site-packages"
if python3 -m ats.collection.symbol_change_query >> /var/log/ats/symbol_change_schedule_log.txt 2>&1; then
    python3 -m ats.database.symbol_change_update >> /var/log/ats/symbol_change_schedule_log.txt 2>&1
# else
#     >> log.txt
#     echo "Failure" >> log.txt 
fi

exit 0

#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
export PYTHONPATH="/home/admin/Projects/ATS_Project_2024/:/home/admin/Projects/ATS_Project_2024/venv/lib/python3.12/site-packages"
if python3 -m ats.database.log_insert >> /var/log/ats/logs_scheduling_log.txt 2>&1; then
    echo "log_insert.py ran successfully" >> /var/log/ats/logs_scheduling_log.txt
else
  echo "log_insert.py failed" >> /var/log/ats/logs_scheduling_log.txt
fi

exit 0
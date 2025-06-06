#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
export PYTHONPATH="/home/admin/Projects/ATS_Project_2024/:/home/admin/Projects/ATS_Project_2024/venv/lib/python3.12/site-packages"
python3 -m ats.database.obsolete_data_deletion >> /var/log/ats/data_deletion_schedule_log.txt 2>&1;

exit 0
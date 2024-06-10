#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
PROJ_DIR=$( cd -- "$( dirname -- "$( dirname -- "${BASH_SOURCE[0]}" )" )" &> /dev/null && pwd )
export PYTHONPATH="$PROJ_DIR:$PROJ_DIR/.venv/lib/python3.12/site-packages"
if python3 -m ats.collection.historical_api_query >> /var/log/ats/historical_schedule_log.txt 2>&1; then
    # Stocks
    python3 -m ats.database.historical_stock_insert >> /var/log/ats/historical_schedule_log.txt 2>&1
    # Indexes
    python3 -m ats.database.historical_index_insert >> /var/log/ats/historical_schedule_log.txt 2>&1
    # Commodities
    python3 -m ats.database.historical_commodity_insert >> /var/log/ats/historical_schedule_log.txt 2>&1
fi

exit 0

#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
if python3 -m ats.collection.historical_api_query >> /var/log/ats/historical_schedule_log.txt 2>&1; then
    # Stocks
    python3 -m ats.database.historical_stock_insert >> /var/log/ats/historical_schedule_log.txt 2>&1
    # Indexes
    python3 -m ats.database.historical_index_insert >> /var/log/ats/historical_schedule_log.txt 2>&1
    # Commodities
    python3 -m ats.database.historical_commodities_insert >> /var/log/ats/historical_schedule_log.txt 2>&1
fi

exit 0

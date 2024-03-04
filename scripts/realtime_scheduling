#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

mkdir -p /var/log/ats
if python3 -m ats.collection.realtime_api_query >> /var/log/ats/realtime_schedule_log.txt 2>&1; then
    # Stocks
    python3 -m ats.database.realtime_stock_insert >> /var/log/ats/realtime_schedule_log.txt 2>&1;
    # Indexes
    python3 -m ats.database.realtime_index_insert >> /var/log/ats/realtime_schedule_log.txt 2>&1;
    # Commodities
    python3 -m ats.database.realtime_commodity_insert >> /var/log/ats/realtime_schedule_log.txt 2>&1;
fi

exit 0

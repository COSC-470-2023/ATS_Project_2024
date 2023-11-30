if python ./SMF_Project_2023/data_collection/collection/historical_api_query.py >> ~/ATSLogs/historical_schedule_log.txt 2>&1; then
    # Stocks
    python database/processing/historical_stock_insert.py >> ~/ATSLogs/historical_schedule_log.txt 2>&1
    # Indexes
    python ./SMF_Project_2023/database/processing/historical_index_insert.py >> ~/ATSLogs/historical_schedule_log.txt 2>&1
    # Commodities
    python ./SMF_Project_2023/database/processing/historical_commodities_insert.py >> ~/ATSLogs/historical_schedule_log.txt 2>&1
# else
#     >> log.txt
#     echo "Failure" >> log.txt 
fi


if python data_collection/collection/historical_api_query.py >> ./logs/historical_schedule_log.txt 2>&1; then
    # Stocks
    #python database/processing/historical_stock_insert.py
    # Indexes
    python database/processing/historical_index_insert.py >> ./logs/historical_schedule_log.txt 2>&1
    # Commodities
    python database/processing/historical_commodities_insert.py >> ./logs/historical_schedule_log.txt 2>&1
# else
#     >> log.txt
#     echo "Failure" >> log.txt 
fi


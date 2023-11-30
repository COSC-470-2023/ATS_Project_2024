# python data_collection/collection/realtime_api_query.py
# if [[ $? != 0 ]];
# then

#     # Stocks
#     python ./database/processing/realtime_stock_insert.py
#     # Indexes
#     python ./database/processing/realtime_index_insert.py
#     # Commodities
#     python ./database/processing/realtime_commodity_insert.py
# else
#     echo "Script failed!" >> log.txt 
#     echo "Failure: $?"
# fi

if python ./SMF_Project_2023/data_collection/collection/realtime_api_query.py >> ~/ATSLogs/realtime_schedule_log.txt 2>&1; then
    # Stocks
    python ./SMF_Project_2023/database/processing/realtime_stock_insert.py >> ~/ATSLogs/realtime_schedule_log.txt 2>&1;
    # Indexes
    python ./SMF_Project_2023/database/processing/realtime_index_insert.py >> ~/ATSLogs/realtime_schedule_log.txt 2>&1;
    # Commodities
    python ./SMF_Project_2023/database/processing/realtime_commodity_insert.py >> ~/ATSLogs/realtime_schedule_log.txt 2>&1;
# else
#     >> log.txt
#     echo "Failure" >> log.txt 
fi


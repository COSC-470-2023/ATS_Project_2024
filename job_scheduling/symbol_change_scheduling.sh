if python ./SMF_Project_2023/data_collection/collection/symbol_change_query.py >> ~/ATSLogs/symbol_change_schedule_log.txt 2>&1; then
    python ./SMF_Project_2023/database/processing/symbol_change_update.py >> ~/ATSLogs/symbol_change_schedule_log.txt 2>&1
# else
#     >> log.txt
#     echo "Failure" >> log.txt 
fi


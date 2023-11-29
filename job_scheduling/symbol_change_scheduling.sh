if python data_collection/collection/symbol_change_query.py >> ./logs/symbol_change_schedule_log.txt 2>&1; then
    # Bonds
    python database/processing/symbol_change_update.py >> ./logs/symbol_change_schedule_log.txt 2>&1
# else
#     >> log.txt
#     echo "Failure" >> log.txt 
fi


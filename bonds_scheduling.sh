if python data_collection/collection/bonds_api_query.py >> ./logs/schedule_log.txt 2>&1; then
    # Bonds
    python database/processing/bonds_insert.py >> ./logs/bonds_schedule_log.txt 2>&1

# else
#     >> log.txt
#     echo "Failure" >> log.txt 
fi


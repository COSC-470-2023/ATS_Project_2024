if python ./SMF_Project_2023/data_collection/collection/bonds_api_query.py >> ~/ATSLogs/bonds_schedule_log.txt 2>&1; then
    # Bonds
    python ./SMF_Project_2023/database/processing/bonds_insert.py >> ~/ATSLogs/bonds_schedule_log.txt 2>&1

# else
#     >> log.txt
#     echo "Failure" >> log.txt 
fi


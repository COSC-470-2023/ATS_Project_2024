if python ./SMF_Project_2023/data_collection/collection/company_info_api_query.py >> ~/ATSLogs/company_statements_schedule_log.txt 2>&1; then
    # Insert company statements
    python ./SMF_Project_2023/database/processing/bonds_insert.py >> ~/ATSLogs/company_statements_schedule_log.txt 2>&1
fi
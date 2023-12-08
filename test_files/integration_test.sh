#!/bin/bash
echo $(date) >> ~/ATSLogs/integration_test_logs.txt
echo "----------------------------" >> ~/ATSLogs/integration_test_logs.txt

# Create DB
mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116  < ~/integration_SMF_Project_2023/test_files/test_ddl/create_integration_db.sql

mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116  < ~/integration_SMF_Project_2023/test_files/test_ddl/create_integration_triggers.sql


# historical_stock_insert
python ~/integration_SMF_Project_2023/database/processing/historical_stock_insert.py

historical_stock_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_historical_stock_values;')

if [[ $historical_stock_count -eq 1250 ]] 
then
    echo "Historical stock insertion successful!" >> ~/ATSLogs/integration_test_logs.txt
else
    echo "Historical stock insertion failed. Number of rows does not match output" >> ~/ATSLogs/integration_test_logs.txt
fi


#historical_index_insert
python ~/integration_SMF_Project_2023/database/processing/historical_index_insert.py

historical_index_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_historical_index_values;')

if [[ $historical_index_count -eq 116 ]] 
then
    echo "Historical index insertion successful!" >> ~/ATSLogs/integration_test_logs.txt
else
    echo "Historical index insertion failed. Number of rows does not match output" >> ~/ATSLogs/integration_test_logs.txt
fi


#historical_commodity_insert
python ~/integration_SMF_Project_2023/database/processing/historical_commodity_insert.py

historical_commodity_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_historical_commodity_values;')

if [[ $historical_commodity_count -eq 140 ]] 
then
    echo "Historical commodity insertion successful!" >> ~/ATSLogs/integration_test_logs.txt
else
    echo "Historical commodity failed. Number of rows does not match output" >> ~/ATSLogs/integration_test_logs.txt
fi


# realtime_stock_insert
python ~/integration_SMF_Project_2023/database/processing/realtime_stock_insert.py

realtime_stock_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_realtime_stock_values;')

if [[ $realtime_stock_count -eq 20 ]] 
then
    echo "Realtime stock insertion successful!" >> ~/ATSLogs/integration_test_logs.txt
else
    echo "Realtime stock insertion failed. Number of rows does not match output" >> ~/ATSLogs/integration_test_logs.txt
fi


#realtime_index_insert
python ~/integration_SMF_Project_2023/database/processing/realtime_index_insert.py

realtime_index_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_realtime_index_values;')

if [[ $realtime_index_count -eq 5 ]] 
then
    echo "Realtime index insertion successful!" >> ~/ATSLogs/integration_test_logs.txt
else
    echo "Realtime index insertion failed. Number of rows does not match output" >> ~/ATSLogs/integration_test_logs.txt
fi

#realtime_commodity_insert
python ~/integration_SMF_Project_2023/database/processing/realtime_commodity_insert.py

realtime_commodity_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_realtime_commodity_values;')

if [[ $realtime_commodity_count -eq 5 ]] 
then
    echo "Realtime commodity insertion successful!" >> ~/ATSLogs/integration_test_logs.txt
else
    echo "Realtime commodity insertion failed. Number of rows does not match output." >> ~/ATSLogs/integration_test_logs.txt
fi


# company statements
python ~/integration_SMF_Project_2023/database/processing/company_statements_insert.py

company_statements_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_company_statements;')

if [[ $company_statements_count -eq 5 ]] 
then
    echo "Company Statements insertion successful!" >> ~/ATSLogs/integration_test_logs.txt
else
    echo "Company Statements insertion failed. Number of rows does not match output." >> ~/ATSLogs/integration_test_logs.txt
fi


 # bonds
python ~/integration_SMF_Project_2023/database/processing/bonds_insert.py

bonds_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_bond_values;')

if [[ $bonds_count -eq 24 ]] 
then
    echo "Bonds Values insertion successful!" >> ~/ATSLogs/integration_test_logs.txt
else
    echo "Bonds Values insertion failed. Number of rows does not match output" >> ~/ATSLogs/integration_test_logs.txt
fi


# symbol changes 
python ~/intergration_SMF_Project_2023/database/processing/symbol_change_update.py

symbol_change_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_company_changelogs;')

if [[ $symbol_change_count -eq 5 ]] 
then
    echo "Symbol Change insertion successful!" >> ~/ATSLogs/integration_test_logs.txt
else
    echo "Symbol Change insertion failed. Number of rows does not match output" >> ~/ATSLogs/integration_test_logs.txt
fi

echo >> ~/ATSLogs/integration_test_logs.txt

# Drop tables and triggers
mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'DROP TABLE `integration_bonds`, `integration_bond_values`, `integration_commodities`, `integration_companies`, `integration_company_changelogs`, `integration_company_statements`, `integration_historical_commodity_values`, `integration_historical_index_values`, `integration_historical_stock_values`, `integration_indexes`, `integration_realtime_commodity_values`, `integration_realtime_index_values`, `integration_realtime_stock_values`;'


    


    

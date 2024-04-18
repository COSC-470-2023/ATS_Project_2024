#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

echo $(date) >> /var/logs/ats/integration_test_logs.txt
echo "----------------------------" >> /var/logs/ats/integration_test_logs.txt

# Create DB
mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116  < tests/integration/test_ddl/create_integration_db.sql

mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116  < tests/integration/test_ddl/create_integration_triggers.sql


# historical_stock_insert
python3 -m ats.database.historical_stock_insert

historical_stock_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_historical_stock_values;')

if [[ $historical_stock_count -eq 1250 ]] 
then
    echo "Historical stock insertion successful!" >> /var/logs/ats/integration_test_logs.txt
else
    echo "Historical stock insertion failed. Number of rows does not match output" >> /var/logs/ats/integration_test_logs.txt
fi


#historical_index_insert
python3 -m ats.database.historical_index_insert

historical_index_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_historical_index_values;')

if [[ $historical_index_count -eq 116 ]] 
then
    echo "Historical index insertion successful!" >> /var/logs/ats/integration_test_logs.txt
else
    echo "Historical index insertion failed. Number of rows does not match output" >> /var/logs/ats/integration_test_logs.txt
fi


#historical_commodity_insert
python3 -m ats.database.historical_commodity_insert

historical_commodity_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_historical_commodity_values;')

if [[ $historical_commodity_count -eq 140 ]] 
then
    echo "Historical commodity insertion successful!" >> /var/logs/ats/integration_test_logs.txt
else
    echo "Historical commodity failed. Number of rows does not match output" >> /var/logs/ats/integration_test_logs.txt
fi


# realtime_stock_insert
python3 -m ats.database.realtime_stock_insert

realtime_stock_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_realtime_stock_values;')

if [[ $realtime_stock_count -eq 20 ]] 
then
    echo "Realtime stock insertion successful!" >> /var/logs/ats/integration_test_logs.txt
else
    echo "Realtime stock insertion failed. Number of rows does not match output" >> /var/logs/ats/integration_test_logs.txt
fi


#realtime_index_insert
python3 -m ats.database.realtime_index_insert

realtime_index_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_realtime_index_values;')

if [[ $realtime_index_count -eq 5 ]] 
then
    echo "Realtime index insertion successful!" >> /var/logs/ats/integration_test_logs.txt
else
    echo "Realtime index insertion failed. Number of rows does not match output" >> /var/logs/ats/integration_test_logs.txt
fi

#realtime_commodity_insert
python3 -m ats.database.realtime_commodity_insert

realtime_commodity_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_realtime_commodity_values;')

if [[ $realtime_commodity_count -eq 5 ]] 
then
    echo "Realtime commodity insertion successful!" >> /var/logs/ats/integration_test_logs.txt
else
    echo "Realtime commodity insertion failed. Number of rows does not match output." >> /var/logs/ats/integration_test_logs.txt
fi


# company statements
python3 -m ats.database.company_statements_insert

company_statements_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_company_statements;')

if [[ $company_statements_count -eq 5 ]] 
then
    echo "Company Statements insertion successful!" >> /var/logs/ats/integration_test_logs.txt
else
    echo "Company Statements insertion failed. Number of rows does not match output." >> /var/logs/ats/integration_test_logs.txt
fi


 # bonds
python3 -m ats.database.bonds_insert

bonds_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_bond_values;')

if [[ $bonds_count -eq 24 ]] 
then
    echo "Bonds Values insertion successful!" >> /var/logs/ats/integration_test_logs.txt
else
    echo "Bonds Values insertion failed. Number of rows does not match output" >> /var/logs/ats/integration_test_logs.txt
fi


# symbol changes 
python3 -m ats.database.symbol_change_update

symbol_change_count=$(mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'SELECT COUNT(*) FROM integration_company_changelogs;')

if [[ $symbol_change_count -eq 5 ]] 
then
    echo "Symbol Change insertion successful!" >> /var/logs/ats/integration_test_logs.txt
else
    echo "Symbol Change insertion failed. Number of rows does not match output" >> /var/logs/ats/integration_test_logs.txt
fi

echo >> /var/logs/ats/integration_test_logs.txt

# Drop tables and triggers
mysql -h db5014801950.hosting-data.io -u dbu1163716 -'paewL7!D%&xy6' dbs12298116 -se 'DROP TABLE `integration_bonds`, `integration_bond_values`, `integration_commodities`, `integration_companies`, `integration_company_changelogs`, `integration_company_statements`, `integration_historical_commodity_values`, `integration_historical_index_values`, `integration_historical_stock_values`, `integration_indexes`, `integration_realtime_commodity_values`, `integration_realtime_index_values`, `integration_realtime_stock_values`;'

exit 0

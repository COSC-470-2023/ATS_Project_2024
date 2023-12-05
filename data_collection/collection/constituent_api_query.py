# This script will be used in order to automatically populate config files with specific index constituents
# Available constituents per API are: sp500_constituent, nasdaq_constituent, dowjones_constituent

import requests
from datetime import timedelta, date
from JsonHandler import JsonHandler

# Globals
CFG_DIRECTORY = "../data_collection/configuration"
REALTIME_CFG_PATH = "../configuration/realtime_query_cfg.json"
HISTORICAL_CFG_PATH = "../configuration/historical_query_cfg.json"
COMPANY_INFO_CFG_PATH = "../configuration/company_info_query_cfg.json"
INDEX_CONSTITUENT_CFG_PATH = "../data_collection/configuration/index_constituent_cfg.json"
OUTPUT_FILENAME_REALTIME = "realtime_query_cfg.json"
OUTPUT_FILENAME_HISTORICAL = "historical_query_cfg.json"
OUTPUT_FILENAME_COMPANY = "company_info_query_cfg.json"


def make_queries():
    symbol_list = []
    config = JsonHandler.load_config(INDEX_CONSTITUENT_CFG_PATH)
    key = config[0]['api_key']
    constituent = config[0]['constituent']
    url = config[0]['url']
    query = url.replace("{QUERY_PARAMS}", constituent).replace("{API_KEY}", key)
    response = requests.get(query)
    # Convert api response to json
    data = response.json()
    symbol_list = data
    return symbol_list


def update_cfg(system_config, symbol_list):
    # Boolean to check if query is historical (needs start/end date)
    is_historical = system_config == JsonHandler.load_config(HISTORICAL_CFG_PATH)

    modified_system_config = system_config
    # For each dictionary in list
    for entry in modified_system_config:
        # For each key in dictionary
        for key, value in entry.items():
            # If the key matches the specified condition, enter and assess if the symbol value is in the changelog
            if key == 'stocks':
                value.clear()
                for stock in symbol_list:
                    stock.pop('sector')
                    stock.pop('subSector')
                    stock.pop('headQuarter')
                    stock.pop('dateFirstAdded')
                    stock.pop('cik')
                    stock.pop('founded')
                    if is_historical:
                        # Config start/end date for 3 year historical queries
                        end = date.today()
                        start = end - timedelta(days=1095)
                        stock['start_date'] = start.strftime('%Y-%m-%d')
                        stock['end_date'] = end.strftime('%Y-%m-%d')
                    value.append(stock)
            else:
                continue

    return modified_system_config


def main():
    # Pretty ratchet should be reworked so that we aren't constantly calling make_queries() to repopulate symbol list
    symbol_list = make_queries()
    # Load in config files
    realtime_cfg = JsonHandler.load_config(REALTIME_CFG_PATH)
    historical_cfg = JsonHandler.load_config(HISTORICAL_CFG_PATH)
    company_info_cfg = JsonHandler.load_config(COMPANY_INFO_CFG_PATH)
    # Update config files
    new_rt_config = update_cfg(realtime_cfg, symbol_list)
    symbol_list = make_queries()
    new_hist_config = update_cfg(historical_cfg, symbol_list)
    symbol_list = make_queries()
    new_comp_config = update_cfg(company_info_cfg, symbol_list)
    # Write new config files with updated stocks
    JsonHandler.write_files(new_rt_config, CFG_DIRECTORY, OUTPUT_FILENAME_REALTIME)
    JsonHandler.write_files(new_hist_config, CFG_DIRECTORY, OUTPUT_FILENAME_HISTORICAL)
    JsonHandler.write_files(new_comp_config, CFG_DIRECTORY, OUTPUT_FILENAME_COMPANY)


if __name__ == "__main__":
    main()

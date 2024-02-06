import requests
from datetime import timedelta, date
from data_collection.collection.yaml_handler import YamlHandler

# Globals
CFG_DIRECTORY = "C:/Users/BCarr/Documents/GitHub/ATS_Project_2024/data_collection/configuration"
REALTIME_CFG_PATH = "C:/Users/BCarr/Documents/GitHub/ATS_Project_2024/data_collection/configuration/realtime_config.yaml"
HISTORICAL_CFG_PATH = "C:/Users/BCarr/Documents/GitHub/ATS_Project_2024/data_collection/configuration/historical_config.yaml"
COMPANY_INFO_CFG_PATH = "C:/Users/BCarr/Documents/GitHub/ATS_Project_2024/data_collection/configuration/company_info_config.yaml"
INDEX_CONSTITUENT_CFG_PATH = "C:/Users/BCarr/Documents/GitHub/ATS_Project_2024/data_collection/configuration/index_config.yaml"
OUTPUT_FILENAME_REALTIME = "realtime_config.yaml"
OUTPUT_FILENAME_HISTORICAL = "historical_config.yaml"
OUTPUT_FILENAME_COMPANY = "company_info_config.yaml"


def make_queries():
    symbol_list = []
    config = YamlHandler.load_config(INDEX_CONSTITUENT_CFG_PATH)
    key = config['api_key']
    constituent = config['constituent']
    url = config['url']
    query = url.replace("{QUERY_PARAMS}", constituent).replace("{API_KEY}", key)
    response = requests.get(query)
    # Convert api response to json
    data = response.json()
    symbol_list = data
    return symbol_list


def update_cfg(system_config, symbol_list):
    # Boolean to check if query is historical (needs start/end date appended)
    is_historical = system_config == YamlHandler.load_config(HISTORICAL_CFG_PATH)
    modified_system_config = system_config
    for key in modified_system_config:
        constituent_list = []
        hist_constituent_list = []
        if key == 'stocks':
            # Remove unused keys from query
            for stock in symbol_list:
                del stock['sector']
                del stock['subSector']
                del stock['headQuarter']
                del stock['dateFirstAdded']
                del stock['cik']
                del stock['founded']
                constituent_list.append(stock)
                if is_historical:
                    # 1095 days is 3 years from today
                    end = date.today()
                    start = end - timedelta(days=1095)
                    # Append start and end dates to config for query
                    stock['start_date'] = start.strftime('%Y-%m-%d')
                    stock['end_date'] = end.strftime('%Y-%m-%d')
                    hist_constituent_list.append(stock)
                    # Add stocks to historical config
                    modified_system_config[key] = hist_constituent_list
                else:
                    # Add stocks to realtime/company_info configs
                    modified_system_config[key] = constituent_list
        else:
            continue


#    for key in modified_system_config:
#        # For each key in dictionary
#       for value in key:
#           print(key)
#           print(value)
#           # If the key matches the specified condition, enter and assess if the symbol value is in the changelog
#           if key == 'stocks':
#               value.clear()
#               for stock in symbol_list:
#                   stock.pop('sector')
#                   stock.pop('subSector')
#                   stock.pop('headQuarter')
#                   stock.pop('dateFirstAdded')
#                   stock.pop('cik')
#                   stock.pop('founded')
#                   if is_historical:
#                       # Config start/end date for 3 year historical queries
#                       end = date.today()
#                       start = end - timedelta(days=1095)
#                       stock['start_date'] = start.strftime('%Y-%m-%d')
#                       stock['end_date'] = end.strftime('%Y-%m-%d')
#                   value.append(stock)
#               else:
#                   continue

    return modified_system_config


def main():
    # Load in config files
    realtime_cfg = YamlHandler.load_config(REALTIME_CFG_PATH)
    historical_cfg = YamlHandler.load_config(HISTORICAL_CFG_PATH)
    company_info_cfg = YamlHandler.load_config(COMPANY_INFO_CFG_PATH)
    # Update config files
    # Pretty ratchet should be reworked so that we aren't constantly calling make_queries() to repopulate symbol list
    symbol_list = make_queries()
    new_rt_config = update_cfg(realtime_cfg, symbol_list)
    symbol_list = make_queries()
    new_hist_config = update_cfg(historical_cfg, symbol_list)
    symbol_list = make_queries()
    new_comp_config = update_cfg(company_info_cfg, symbol_list)
    # Write new config files with updated stocks
    YamlHandler.write_files(new_rt_config, CFG_DIRECTORY, OUTPUT_FILENAME_REALTIME)
    YamlHandler.write_files(new_hist_config, CFG_DIRECTORY, OUTPUT_FILENAME_HISTORICAL)
    YamlHandler.write_files(new_comp_config, CFG_DIRECTORY, OUTPUT_FILENAME_COMPANY)


if __name__ == "__main__":
    main()

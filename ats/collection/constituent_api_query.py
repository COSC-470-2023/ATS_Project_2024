import datetime
import os
import requests

from ats.globals import DIR_CONFIG, CONFIG_COMPANY_INFO, CONFIG_HISTORICAL, CONFIG_INDEX, CONFIG_REALTIME
from ats.util import yaml_handler



def make_queries(api_key, config):
    constituent = config['constituent']
    url = config['url']
    query = url.replace("{QUERY_PARAMS}", constituent).replace("{API_KEY}", api_key)
    response = requests.get(query)
    # Convert api response to json
    data = response.json()
    return data


def update_cfg(system_config, symbol_list):
    # Boolean to check if query is historical (needs start/end date appended)
    is_historical = system_config == yaml_handler.load_config(DIR_CONFIG + CONFIG_HISTORICAL)
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
                    end = datetime.date.today()
                    start = end - datetime.timedelta(days=1095)
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

    return modified_system_config


def main():
    api_key = os.getenv('ATS_API_KEY')
    config = yaml_handler.load_config(DIR_CONFIG + CONFIG_INDEX)
    # Load in config files
    realtime_cfg = yaml_handler.load_config(DIR_CONFIG + CONFIG_REALTIME)
    historical_cfg = yaml_handler.load_config(DIR_CONFIG + CONFIG_HISTORICAL)
    company_info_cfg = yaml_handler.load_config(DIR_CONFIG + CONFIG_COMPANY_INFO)
    # Update config files
    # Pretty ratchet should be reworked so that we aren't constantly calling make_queries() to repopulate symbol list
    symbol_list = make_queries(api_key, config)
    new_rt_config = update_cfg(realtime_cfg, symbol_list)
    symbol_list = make_queries(api_key, config)
    new_hist_config = update_cfg(historical_cfg, symbol_list)
    symbol_list = make_queries(api_key, config)
    new_comp_config = update_cfg(company_info_cfg, symbol_list)
    # Write new config files with updated stocks
    yaml_handler.write_files(new_rt_config, DIR_CONFIG, CONFIG_REALTIME)
    yaml_handler.write_files(new_hist_config, DIR_CONFIG, CONFIG_HISTORICAL)
    yaml_handler.write_files(new_comp_config, DIR_CONFIG, CONFIG_COMPANY_INFO)


if __name__ == "__main__":
    main()

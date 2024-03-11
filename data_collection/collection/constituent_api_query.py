import requests
import sys

from datetime import timedelta, date
from data_collection.collection.yaml_handler import yaml_load_config, yaml_write_config
from dev_tools import loguru_init

# Globals
CFG_DIRECTORY = "./ATS_Project_2024/data_collection/configuration"
REALTIME_CFG_PATH = "./ATS_Project_2024/data_collection/configuration/realtime_config.yaml"
HISTORICAL_CFG_PATH = "./ATS_Project_2024/data_collection/configuration/historical_config.yaml"
COMPANY_INFO_CFG_PATH = "./ATS_Project_2024/data_collection/configuration/company_info_config.yaml"
INDEX_CONSTITUENT_CFG_PATH = "./ATS_Project_2024/data_collection/configuration/index_config.yaml"
OUTPUT_FILENAME_REALTIME = "realtime_config.yaml"
OUTPUT_FILENAME_HISTORICAL = "historical_config.yaml"
OUTPUT_FILENAME_COMPANY = "company_info_config.yaml"

# Loguru init
logger = loguru_init.initialize()


def make_queries():
    logger.info("Constituent Query starting")
    symbol_list = []
    try:
        logger.debug("Executing API call.")
        config = yaml_load_config(INDEX_CONSTITUENT_CFG_PATH)
        key = config['api_key']
        constituent = config['constituent']
        url = config['url']
        query = url.replace("{QUERY_PARAMS}", constituent).replace("{API_KEY}", key)
        response = requests.get(query)
        # Convert api response to json
        logger.debug("Converting API response to JSON")
        data = response.json()
        symbol_list = data
    # TODO: Discuss proper exception handling (custom exception handler?)
    except Exception as e:
        logger.error(e)
    logger.info("Constituent Query complete")
    return symbol_list


def update_cfg(system_config, symbol_list):
    logger.info("Constituent configuration update starting")
    modified_system_config = system_config
    try:
        # Boolean to check if query is historical (needs start/end date appended)
        is_historical = system_config == yaml_load_config(HISTORICAL_CFG_PATH)
        for key in modified_system_config:
            constituent_list = []
            hist_constituent_list = []
            if key == 'stocks':
                logger.debug("Updating stock list in configuration file: ", system_config)
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
                        # 1095 days is 3 years from today, should probably be a parameter in config file
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
            logger.info("Constituent configuration update complete")
    # TODO: Discuss proper exception handling (custom exception handler?)
    except Exception as e:
        logger.error(e)
    return modified_system_config


def main():
    try:
        # Load config files
        realtime_cfg = yaml_load_config(REALTIME_CFG_PATH)
        historical_cfg = yaml_load_config(HISTORICAL_CFG_PATH)
        company_info_cfg = yaml_load_config(COMPANY_INFO_CFG_PATH)

        # Update config files
        symbol_list = make_queries()
        new_rt_config = update_cfg(realtime_cfg, symbol_list)
        symbol_list = make_queries()
        new_hist_config = update_cfg(historical_cfg, symbol_list)
        symbol_list = make_queries()
        new_comp_config = update_cfg(company_info_cfg, symbol_list)

        # Write new config files with updated stocks
        yaml_write_config(new_rt_config, CFG_DIRECTORY, OUTPUT_FILENAME_REALTIME)
        yaml_write_config(new_hist_config, CFG_DIRECTORY, OUTPUT_FILENAME_HISTORICAL)
        yaml_write_config(new_comp_config, CFG_DIRECTORY, OUTPUT_FILENAME_COMPANY)
    except Exception as e:
        logger.error(e)
    logger.success("constituent_api_query.py completed successfully.")


if __name__ == "__main__":
    main()

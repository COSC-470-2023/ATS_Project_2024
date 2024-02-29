import time
import requests
import sys

from loguru import logger

from data_collection.collection.JsonHandler import json_write_files

from data_collection.collection.yaml_handler import YamlHandler


# Globals
HISTORICAL_CFG_PATH = "./ATS_Project_2024/data_collection/configuration/historical_config.yaml"
OUTPUT_FOLDER = "./ATS_Project_2024/data_collection/output/"
OUTPUT_FILENAME_STOCKS = "historical_stocks_output.json"
OUTPUT_FILENAME_INDEX = "historical_index_output.json"
OUTPUT_FILENAME_COMMODITIES = "historical_commodity_output.json"

# Loguru init
logger.remove()
log_format = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | <level>{level: <8}</level> | <yellow>Line {line: >4} "
              "({file}):</yellow> <b>{message}</b>")
logger.add(sys.stderr, level="DEBUG", format=log_format, colorize=True, backtrace=True, diagnose=True)
# TODO add retention parameter to loggers when client has specified length
logger.add("log_file.log", rotation='00:00', level="DEBUG", format=log_format, colorize=False, backtrace=True,
           diagnose=True, backup=5)
logger.add("log_file.log", rotation='00:00', level="INFO", format=log_format, colorize=False, backtrace=True,
           diagnose=True, backup=5)


def make_queries(parsed_api_url, parsed_api_key, query_list, api_rate_limit, api_fields, non_api_fields):
    logger.info("Historical Query starting")
    try:
        output = []
        # Iterate through each stock and make an API call
        for query_itr in range(len(query_list)):
            query_item = query_list[query_itr]
            # Replace the URL parameters with our current API configs
            query = (parsed_api_url.replace("{QUERY_PARAMS}", query_item['symbol'])
                     .replace("{API_KEY}", parsed_api_key)
                     .replace("{START_DATE}", query_item['start_date'])
                     .replace("{END_DATE}", query_item['end_date']))
            response = requests.get(query)
            # convert the response to json and append to list
            data = response.json()
            output.append({})
            output[-1] = remap_entries(data, query_item, api_fields, non_api_fields)
    except Exception as e:
        logger.debug(e)
    logger.info("Historical Query complete")
    return output


def remap_entries(response_data, query_item, api_fields, non_api_fields):
    logger.info("Historical Remap starting")
    entries = response_data['historical']
    remapped_entry = {}
    for entry in entries:
        if non_api_fields != {}:  # There is a manually added field in the cfg.
            for non_api_field in non_api_fields:
                # Compare the manually added field to where it should get its data from
                # in the normal fields
                try:
                    src = non_api_fields[non_api_field]['src']
                    map_to = non_api_fields[non_api_field]['mapping']
                    input_type = non_api_fields[non_api_field]['input_type']
                    output_type = non_api_fields[non_api_field]['output_type']
                    # Handler for "unix_time" conversion to date time
                    # print(f"src: {src}, map_to: {map_to}, input_type: {input_type}, output_type: {output_type}")
                    if input_type == "_string":
                        if output_type == "_string" and src == "_config_name":
                            # Handler for grabbing string name from the configuration file
                            try:
                                entry[map_to] = query_item['name']
                            except TypeError as e:
                                logger.debug(e)
                                continue
                except KeyError as e:
                    logger.debug(f"Key Error on {query_item}:\n{e}")
                    continue
        try:
            remapped_entry = entry.copy()  # Cant iterate over a dict that is changing in size.
            # Iterate over the fields and then rename them, by reinserting and deleting the old.
            for field in api_fields:
                if api_fields[field] is not None:  # API field mapping was set to null
                    if field in entry:
                        remapped_entry[api_fields[field]] = entry[field]
                    elif field in response_data:
                        remapped_entry[api_fields[field]] = response_data[field]
                    try:
                        del remapped_entry[field]  # API field has a mapping value, rename it.
                    except KeyError as e:
                        logger.debug(f"KeyError, {field} does not exist in remapped_entry\n{e}")
                        pass
                else:
                    del remapped_entry[field]
                    # dump it as cfg doesn't care to keep.
        except AttributeError as e:
            logger.debug(f"Attribute Error on {entry}:\n{e}")
            pass  # The copy failed of the dict because it was probably an error message.
    logger.info("Historical Remap complete")
    return remapped_entry


def main():
    try:
        # Load config
        historical_config = YamlHandler.load_config(HISTORICAL_CFG_PATH)
        api_url = historical_config['url']
        api_key = historical_config['api_key']
        api_rate_limit = historical_config['rate_limit']
        api_fields = historical_config['api_fields']
        non_api_fields = historical_config['non_api_fields']
        stock_list = historical_config['stocks']
        index_list = historical_config['index_composites']
        commodity_list = historical_config['commodities']
        logger.info("creating Historical Stock output")
        stock_output = make_queries(api_url, api_key, stock_list, api_rate_limit, api_fields, non_api_fields)
        logger.info("Historical Stock output created successfully")
        logger.info("creating Historical Index output")
        index_output = make_queries(api_url, api_key, index_list, api_rate_limit, api_fields, non_api_fields)
        logger.info("Historical Index output created successfully")
        logger.info("creating Historical Commodity output")
        commodity_output = make_queries(api_url, api_key, commodity_list, api_rate_limit, api_fields, non_api_fields)
        logger.info("Historical Commodity output created successfully")
        logger.info("writing Historical Stock output file")
        json_write_files(stock_output, OUTPUT_FOLDER, OUTPUT_FILENAME_STOCKS)
        logger.info("Historical Stock file write complete")
        logger.info("writing Historical Index output file")
        json_write_files(index_output, OUTPUT_FOLDER, OUTPUT_FILENAME_INDEX)
        logger.info("Historical Index file write complete")
        logger.info("writing Historical Commodity output file")
        json_write_files(commodity_output, OUTPUT_FOLDER, OUTPUT_FILENAME_COMMODITIES)
        logger.info("Historical Commodity file write complete")
    except Exception as e:
        logger.debug(e)


if __name__ == "__main__":
    main()

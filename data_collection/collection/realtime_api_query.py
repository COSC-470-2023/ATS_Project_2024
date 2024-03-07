import time
import requests
import sys

from datetime import datetime

from data_collection.collection.json_handler import json_write_files
from data_collection.collection.yaml_handler import yaml_load_config
from dev_tools import loguru_init

# Globals
REALTIME_CFG_PATH = "./ATS_Project_2024/data_collection/configuration/realtime_config.yaml"
OUTPUT_FOLDER = "./ATS_Project_2024/data_collection/output/"
OUTPUT_FILENAME_STOCKS = "realtime_stocks_output.json"
OUTPUT_FILENAME_INDEX = "realtime_index_output.json"
OUTPUT_FILENAME_COMMODITIES = "realtime_commodity_output.json"

# Loguru init
logger = loguru_init.initialize()


def make_queries(parsed_api_url, parsed_api_key, query_list, api_rate_limit, api_fields, non_api_fields):
    logger.info("Realtime Query starting")
    try:
        output = []
        # Iterate through each stock and make an API call
        for query_itr in range(len(query_list)):
            query_item = query_list[query_itr]
            # Replace the URL parameters with our current API configs
            query = parsed_api_url.replace("{QUERY_PARAMS}", query_item['symbol']).replace("{API_KEY}", parsed_api_key)
            response = requests.get(query)
            # convert the response to json and append to list
            data = response.json()
            output.append({})
            output[-1] = remap_entries(data, non_api_fields, api_fields)
            print("we're looping")
    except Exception as e:
        logger.debug(e)
        print("we're buggin")
    logger.info("Realtime Query complete")
    return output


def remap_entries(response_data, non_api_fields, api_fields):
    remapped_entry = {}

    for entry in response_data:
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
                    # TODO add more cases later, for the first API this is all we need.
                    if input_type == "_unix_time":
                        if output_type == "_date_time":
                            try:
                                entry[map_to] = str(datetime.fromtimestamp(entry[src]))
                            except TypeError as e:
                                logger.debug(e)
                                continue
                except KeyError as e:
                    logger.debug(e)
                    continue
        try:
            remapped_entry = entry.copy()  # Cant iterate over a dict that is changing in size.
            # Iterate over the fields and then rename them, by reinserting and deleting the old.
            for field in api_fields:
                if api_fields[field] is not None:
                    remapped_entry[api_fields[field]] = remapped_entry[field]
                    del remapped_entry[field]  # API field has a mapping value, rename it.
                else:
                    del remapped_entry[
                        field]  # API field mapping was set to null, dump it as cfg doesn't care to keep.
        except AttributeError:
            continue  # The copy failed of the dict because it was probably an error message.

    return remapped_entry


def main():
    try:
        realtime_config = yaml_load_config(REALTIME_CFG_PATH)
        stock_output = []
        index_output = []
        commodity_output = []

        # Iterate through each API in the list
        api_url = realtime_config['url']
        api_key = realtime_config['api_key']
        api_rate_limit = realtime_config['rate_limit_per_min']
        api_fields = realtime_config['api_fields']
        non_api_fields = realtime_config['non_api_fields']
        stock_list = realtime_config['stocks']
        index_list = realtime_config['index_composites']
        commodity_list = realtime_config['commodities']

        # Attempt to populate output
        stock_output += make_queries(api_url, api_key, stock_list, api_rate_limit, api_fields, non_api_fields)
        index_output += make_queries(api_url, api_key, index_list, api_rate_limit, api_fields, non_api_fields)
        commodity_output += make_queries(api_url, api_key, commodity_list, api_rate_limit, api_fields, non_api_fields)

        # Write output files
        json_write_files(stock_output, OUTPUT_FOLDER, OUTPUT_FILENAME_STOCKS)
        json_write_files(index_output, OUTPUT_FOLDER, OUTPUT_FILENAME_INDEX)
        json_write_files(commodity_output, OUTPUT_FOLDER, OUTPUT_FILENAME_COMMODITIES)
    except Exception as e:
        logger.error(e)

    logger.success("realtime_api_query.py ran successfully.")


# Code to only be executed if ran as script
if __name__ == "__main__":
    main()

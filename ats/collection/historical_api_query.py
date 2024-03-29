import os
import requests

from ats import loguru_init
from ats.globals import (DIR_CONFIG, DIR_OUTPUT, CONFIG_HISTORICAL, OUTPUT_HISTORICAL_COMMODITY,
                         OUTPUT_HISTORICAL_INDEX, OUTPUT_HISTORICAL_STOCKS)
from ats.util import json_handler
from ats.util import yaml_handler

# Loguru init
logger = loguru_init.initialize()


def make_queries(parsed_api_url, api_key, query_list, api_fields, non_api_fields):
    logger.info("Historical Collection Query starting")
    output = []
    try:
        # Iterate through each stock and make an API call
        for query_itr in range(len(query_list)):
            query_item = query_list[query_itr]
            # Replace the URL parameters with our current API configs

            query = (parsed_api_url.replace("{QUERY_PARAMS}", query_item['symbol'])
                     .replace("{API_KEY}", api_key)
                     .replace("{START_DATE}", query_item['start_date'])
                     .replace("{END_DATE}", query_item['end_date']))

            response = requests.get(query)
            # convert the response to json and append to list
            data = response.json()

            output.append({})
            output[-1] = remap_entries(data, query_item, api_fields, non_api_fields)
    except Exception as e:
        logger.error(e)
    logger.info("Historical Query complete")
    return output


def remap_entries(response_data, query_item, api_fields, non_api_fields):
    logger.info("Historical field remapping: Starting")
    entries = response_data['historical']
    remapped_entry = {}

    for entry in entries:
        # TODO: This is repeated logic in other files -> refactor.
        if non_api_fields != {}:  # There is a manually added field in the cfg.
            logger.debug("Manually added field(s) detected: Mapping data")
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
                                logger.error(e)
                except KeyError as e:
                    logger.error(f"Key Error on {query_item}:\n{e}")
            logger.debug("Manual field mapping complete")
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
                        logger.warning(f"KeyError, {field} does not exist in remapped_entry\n{e}")
                else:
                    del remapped_entry[field]
                    # dump it as cfg doesn't care to keep.
        except AttributeError as e:
            logger.error(f"Attribute Error on {entry}:\n{e}")
    logger.info("Historical field remapping: Complete")
    return remapped_entry


def main():
    try:
        historical_config = yaml_handler.load_config(DIR_CONFIG + CONFIG_HISTORICAL)
        # Iterate through each API in the list
        api_url = historical_config['url']
        api_key = os.getenv('ATS_API_KEY')
        api_fields = historical_config['api_fields']
        non_api_fields = historical_config['non_api_fields']
        stock_list = historical_config['stocks']
        index_list = historical_config['index_composites']
        commodity_list = historical_config['commodities']
        logger.info("creating Historical Stock output")
        stock_output = make_queries(api_url, api_key, stock_list, api_fields, non_api_fields)
        logger.info("Historical Stock output created successfully")
        logger.info("creating Historical Index output")
        index_output = make_queries(api_url, api_key, index_list, api_fields, non_api_fields)
        logger.info("Historical Index output created successfully")
        logger.info("creating Historical Commodity output")
        commodity_output = make_queries(api_url, api_key, commodity_list, api_fields, non_api_fields)
        logger.info("Historical Commodity output created successfully")
        logger.info("writing Historical Stock output file")
        json_handler.write_files(stock_output, DIR_OUTPUT, OUTPUT_HISTORICAL_STOCKS)
        logger.info("Historical Stock file write complete")
        logger.info("writing Historical Index output file")
        json_handler.write_files(index_output, DIR_OUTPUT, OUTPUT_HISTORICAL_INDEX)
        logger.info("Historical Index file write complete")
        logger.info("writing Historical Commodity output file")
        json_handler.write_files(commodity_output, DIR_OUTPUT, OUTPUT_HISTORICAL_COMMODITY)
        logger.info("Historical Commodity file write complete")
    except Exception as e:
        logger.error(e)

    logger.success("historical_api_query.py ran successfully.")


if __name__ == "__main__":
    main()

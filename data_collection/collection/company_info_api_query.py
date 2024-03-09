import time
import requests
import sys

from datetime import datetime

from data_collection.collection.json_handler import json_write_files
from data_collection.collection.yaml_handler import yaml_load_config
from dev_tools import loguru_init


# Globals
COMPANY_INFO_CFG_PATH = "./ATS_Project_2024/data_collection/configuration/company_info_config.yaml"
OUTPUT_FOLDER = "./ATS_Project_2024/data_collection/output"
OUTPUT_FILENAME = "company_info_output.json"

# Loguru init
logger = loguru_init.initialize()


# TODO: refactor remapping logic into its own method (similar to realtime_api_query
def make_queries(parsed_api_url, parsed_api_key, query_list, api_fields, non_api_fields):
    logger.info("Company Info Collection Query starting")
    output = []
    try:
        # Iterate through each stock and make an API call
        for query_itr in range(len(query_list)):
            query_item = query_list[query_itr]
            # Replace the URL parameters with our current API configs
            query = parsed_api_url.replace("{QUERY_PARAMS}", query_item['symbol']).replace("{API_KEY}", parsed_api_key)
            response = requests.get(query)
            # Convert the response to json and append to list
            data = response.json()
            remapped_entry = {}
        for entry in data:
            try:
                src = non_api_fields['src']
                map_to = non_api_fields['mapping']
                input_type = non_api_fields['input_type']
                output_type = non_api_fields['output_type']
                # Handler for "unix_time" conversion to date time
                if input_type is None:
                    if output_type == "_date_time":
                        try:
                            entry[map_to] = str(datetime.now())
                        except TypeError as e:
                            logger.error(f"Type Error on {entry}:\n{e}")
                            continue
            except KeyError as e:
                logger.error(f"Key Error on {entry}:\n{e}")
                continue
            try:
                remapped_entry = entry.copy()  # Cant iterate over a dict that is changing in size.
                # Iterate over the fields and then rename them, by reinserting and deleting the old.
                for field in api_fields:
                    if api_fields[field] is not None:
                        remapped_entry[api_fields[field]] = remapped_entry[field]
                        del remapped_entry[field]  # API field has a mapping value, rename it.
                    else:
                        del remapped_entry[field]  # API field mapping was set to null,
                        # dump it as cfg doesn't care to keep.
            except AttributeError as e:
                logger.error(f"Attribute Error on {entry}:\n{e}")
                continue  # The copy failed of the dict because it was probably an error message.
        output.append({})
        output[-1] = remapped_entry
    except Exception as e:
        logger.error(e)
    logger.info("Company Info Query complete")
    return output


def main():
    try:
        company_config = yaml_load_config(COMPANY_INFO_CFG_PATH)
        company_output = []
        # Load variables from the configuration files
        url = company_config['url']
        key = company_config['api_key']
        rate_limit = company_config['rate_limit_per_min']
        fields = company_config['api_fields']
        non_api_fields = company_config['non_api_fields']
        company_list = company_config['stocks']
        # Generate output
        logger.info("creating Company Info output")
        company_output = make_queries(url, key, company_list, rate_limit, fields, non_api_fields)
        logger.info("Company Info output created successfully")
        # Write file
        logger.info("writing Company Info output file")
        json_write_files(company_output, OUTPUT_FOLDER, OUTPUT_FILENAME)
        logger.info("Company Info output file write complete")
    except Exception as e:
        logger.error(e)

    logger.success("company_info_api_query.py ran successfully.")


if __name__ == "__main__":
    main()

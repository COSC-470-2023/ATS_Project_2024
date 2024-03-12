import datetime
import os
import requests

from ats import loguru_init
from ats.globals import DIR_CONFIG, DIR_OUTPUT, CONFIG_COMPANY_INFO, OUTPUT_COMPANY_INFO
from ats.util import json_handler
from ats.util import yaml_handler

# Loguru init
logger = loguru_init.initialize()


# TODO: refactor remapping logic into its own method (similar to realtime_api_query
def make_queries(parsed_api_url, api_key, query_list, api_fields, non_api_fields):
    logger.info("Company Info Collection Query starting")
    output = []
    try:
        # Iterate through each stock and make an API call
        for query_itr in range(len(query_list)):
            query_item = query_list[query_itr]

            # Replace the URL parameters with our current API configs
            query = parsed_api_url.replace("{QUERY_PARAMS}", query_item['symbol']).replace("{API_KEY}", api_key)
            data = []
            try:
                response = requests.get(query)
                # Convert the response to json and append to list
                data = response.json()
                remapped_entry = {}
            except requests.RequestException as e:
                logger.debug(f"api_error {e}")
            for entry in data:
                try:
                    map_to = non_api_fields['mapping']
                    input_type = non_api_fields['input_type']
                    output_type = non_api_fields['output_type']
                    # Handler for "unix_time" conversion to date time
                    if input_type is None:
                        if output_type == "_date_time":
                            try:
                                entry[map_to] = str(datetime.datetime.now())
                            except TypeError as e:
                                logger.error(f"Type Error on {entry}:\n{e}")
                except KeyError as e:
                    logger.error(f"Key Error on {entry}:\n{e}")
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

            output.append({})
            output[-1] = remapped_entry
    except Exception as e:
        logger.error(e)

    logger.info("Company Info Query complete")
    return output


def main():
    try:
        company_config = yaml_handler.load_config(DIR_CONFIG + CONFIG_COMPANY_INFO)
        # Load variables from the configuration files
        url = company_config['url']
        api_key = os.getenv('ATS_API_KEY')
        fields = company_config['api_fields']
        non_api_fields = company_config['non_api_fields']
        company_list = company_config['stocks']
        # Generate output
        logger.info("creating Company Info output")
        company_output = make_queries(url, api_key, company_list, fields, non_api_fields)
        logger.info("Company Info output created successfully")
        # Write file
        logger.info("writing Company Info output file")
        json_handler.write_files(company_output, DIR_OUTPUT, OUTPUT_COMPANY_INFO)
        logger.info("Company Info output file write complete")
    except Exception as e:
        logger.error(e)

    logger.success("company_info_api_query.py ran successfully.")


if __name__ == "__main__":
    main()

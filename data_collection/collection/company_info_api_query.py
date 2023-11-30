# Get data from company info API list file

import time
import requests
from datetime import datetime
from JsonHandler import JsonHandler

# Globals
COMPANY_INFO_CFG_PATH = "./SMF_Project_2023/data_collection/configuration/company_info_query_cfg.json"
OUTPUT_FOLDER = "./SMF_Project_2023/data_collection/output/"
OUTPUT_FILENAME = "company_info_output.json"


def make_queries(parsed_api_url, parsed_api_key, query_list, api_rate_limit, api_fields, non_api_fields):
    output = []
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
                        if input_type is None:
                            if output_type == "_date_time":
                                try:
                                    entry[map_to] = str(datetime.now())
                                except TypeError:
                                    continue
                    except KeyError:
                        continue  # TODO make log files entry
            try:
                remapped_entry = entry.copy()  # Cant iterate over a dict that is changing in size.
                # Iterate over the fields and then rename them, by reinserting and deleting the old.
                for field in api_fields:
                    if api_fields[field] is not None:
                        remapped_entry[api_fields[field]] = remapped_entry[field]
                        del remapped_entry[field]  # API field has a mapping value, rename it.
                    else:
                        del remapped_entry[field]  # API field mapping was set to null,
                        # dump it as cfg doesnt care to keep.

            except AttributeError:
                continue  # The copy failed of the dict because it was probably an error message.

        output.append({})
        output[-1] = remapped_entry

        if api_rate_limit is not None:
            time.sleep(60 / api_rate_limit)

    return output


def main():
    json_config = JsonHandler.load_config(COMPANY_INFO_CFG_PATH)
    company_output = []

    # Iterate through each API in the list
    for api in range(len(json_config)):
        api_url = json_config[api]['url']
        api_key = json_config[api]['api_key']
        api_rate_limit = json_config[api]['rate_limit_per_min']
        api_fields = json_config[api]['api_fields']
        non_api_fields = json_config[api]['non_api_fields']

        company_list = json_config[api]['companies']

        company_output += make_queries(api_url, api_key, company_list, api_rate_limit, api_fields, non_api_fields)

    JsonHandler.write_files(company_output, OUTPUT_FOLDER, OUTPUT_FILENAME)


if __name__ == "__main__":
    main()

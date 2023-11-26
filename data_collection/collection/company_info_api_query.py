# Get data from company info API list file
import json
import time
import os
import errno
import requests
from datetime import datetime


# Load config file
def load_config():
    config_path = "../configuration/company_info_query_cfg.json"
    try:
        config_file = open(config_path, "r")
        config = json.load(config_file)
        return config
    except IOError:
        print(f"IOError while accessing stock/index/commodity query config at path: {config_path}")
        exit(-1001)  # Exit program with code -1001 (Invalid config path)
    except json.JSONDecodeError as e:
        print(f"JSON decoding encountered an error while decoding {config_path}:\n{e}")
        exit(-1002)  # Exit program with code -1002 (Invalid config structure)


# Create API queries
def make_queries(parsed_api_url, parsed_api_key, query_list, api_rate_limit, api_fields, non_api_fields):
    output = []
    # Iterate through each stock and make an API call
    for query_itr in range(len(query_list)):
        query = query_list[query_itr]['symbol']

        # Replace the URL parameters with our current API configs
        query = parsed_api_url.replace("{QUERY_PARAMS}", query).replace("{API_KEY}", parsed_api_key)
        response = requests.get(query)
        # Convert the response to json and append to list
        data = response.json()

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
                        # print(f"src: {src}, map_to: {map_to}, input_type: {input_type}, output_type: {output_type}")
                        if input_type is None:
                            if output_type == "_date_time":
                                # print(True)
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
                        del remapped_entry[field]  # API field mapping was set to null, dump it as cfg doesnt care to keep.
                data[0] = remapped_entry
            except AttributeError:
                continue  # The copy failed of the dict because it was probably an error message.

        output += data

        if api_rate_limit is not None:
            time.sleep(60 / api_rate_limit)

    print(output)
    return output


# Write output file
def write_files(company_json):
    output_dir = "../output/"
    if not os.path.exists(os.path.dirname(output_dir)):
        try:
            os.makedirs(os.path.dirname(output_dir))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open("../output/company_info_output.json", "w") as outfile:
        json.dump(company_json, outfile, indent=2)


def main():
    json_config = load_config()
    company_output = []

    # Iterate through each API in the list
    for api in range(len(json_config)):
        api_url = json_config[api]['url']
        api_key = json_config[api]['api_key']
        api_rate_limit = json_config[api]['rate_limit_per_min']
        api_fields = json_config[api]['api_fields']
        non_api_fields = json_config[api]['non_api_fields']

        # Get a list of the company symbols we need to query
        company_list = json_config[api]['companies']

        company_output = make_queries(api_url, api_key, company_list, api_rate_limit, api_fields, non_api_fields)

    write_files(company_output)


# Code to only be executed if ran as script
if __name__ == "__main__":
    main()

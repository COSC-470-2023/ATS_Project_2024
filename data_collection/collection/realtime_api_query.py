# Get data from the bonds API list file
# Parse the json so we know what our URL and keys are
# Iterate through the stocks using the key and url, then move onto the next API
# TODO make the directories for file read and out absolute ie not relative locations to the script

import time
import requests
from datetime import datetime
from JsonModifier import JsonModifier

# Globals
REALTIME_CFG_PATH = "../configuration/realtime_query_cfg.json"
OUTPUT_FOLDER = "../output/"
OUTPUT_FILENAME_STOCKS = "realtime_stocks_output.json"
OUTPUT_FILENAME_INDEX = "realtime_index_output.json"
OUTPUT_FILENAME_COMMODITIES = "realtime_commodity_output.json"


def make_queries(parsed_api_url, parsed_api_key, query_list, api_rate_limit, api_fields, non_api_fields):
    output = []

    # Iterate through each stocks and make a API call
    # TODO make it query with 5 items at a time ("APPL, TSLA, %5EGSPC")
    for query_itr in range(len(query_list)):
        query_item = query_list[query_itr]
        # Replace the URL parameters with our current API configs
        query = parsed_api_url.replace("{QUERY_PARAMS}", query_item['symbol']).replace("{API_KEY}", parsed_api_key)
        response = requests.get(query)
        # convert the response to json and append to list
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
                        if input_type == "_unix_time":
                            if output_type == "_date_time":
                                try:
                                    entry[map_to] = str(datetime.fromtimestamp(entry[src]))
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
                        del remapped_entry[
                            field]  # API field mapping was set to null, dump it as cfg doesnt care to keep.
            except AttributeError:
                continue  # The copy failed of the dict because it was probably an error message.

        output.append({})
        output[-1] = remapped_entry

        # Rate limit the query speed based on the rate limit
        # From inside the JSON. Check that the key wasnt valued at null, signifying no rate limit.
        if api_rate_limit is not None:
            time.sleep(60 / api_rate_limit)

    return output


# def write_files(stock_json, index_json, commodity_json):
#     output_dir = "../output/"
#     if not os.path.exists(os.path.dirname(output_dir)):
#         try:
#             os.makedirs(os.path.dirname(output_dir))
#         except OSError as exc:  # Guard against race condition
#             if exc.errno != errno.EEXIST:
#                 raise
#
#     with open("../output/stocks_output.json", "w") as outfile:
#         json.dump(stock_json, outfile, indent=2)
#
#     with open("../output/index_output.json", "w") as outfile:
#         json.dump(index_json, outfile, indent=2)
#
#     with open("../output/commodity_output.json", "w") as outfile:
#         json.dump(commodity_json, outfile, indent=2)

# Loads the configuration file.
# def load_config():
#     config_path = "../configuration/realtime_query_cfg.json"
#     try:
#         config_file = open(config_path, "r")
#         config = json.load(config_file)
#         return config
#     except IOError:
#         print(f"IOError while accessing stock/index/commodity query config at path: {config_path}")
#         exit(-1001)  # Exit program with code -1001 (Invalid config path)
#     except json.JSONDecodeError as e:
#         print(f"JSON decoding encountered an error while decoding {config_path}:\n{e}")
#         exit(-1002)  # Exit program with code -1002 (Invalid config structure)


def main():
    json_config = JsonModifier.load_config(REALTIME_CFG_PATH)
    stock_output = []
    index_output = []
    commodity_output = []

    # Iterate through each API in the list
    for api in range(len(json_config)):
        api_url = json_config[api]['url']
        api_key = json_config[api]['api_key']
        api_rate_limit = json_config[api]['rate_limit_per_min']
        api_fields = json_config[api]['api_fields']
        non_api_fields = json_config[api]['non_api_fields']
        stock_list = json_config[api]['stocks']
        index_list = json_config[api]['index_composites']
        commodity_list = json_config[api]['commodities']

        stock_output = make_queries(api_url, api_key, stock_list, api_rate_limit, api_fields, non_api_fields)
        index_output = make_queries(api_url, api_key, index_list, api_rate_limit, api_fields, non_api_fields)
        commodity_output = make_queries(api_url, api_key, commodity_list, api_rate_limit, api_fields, non_api_fields)

    JsonModifier.write_files(stock_output, OUTPUT_FOLDER, OUTPUT_FILENAME_STOCKS)
    JsonModifier.write_files(index_output, OUTPUT_FOLDER, OUTPUT_FILENAME_INDEX)
    JsonModifier.write_files(commodity_output, OUTPUT_FOLDER, OUTPUT_FILENAME_COMMODITIES)


# code to only be executed if ran as script
if __name__ == "__main__":
    main()

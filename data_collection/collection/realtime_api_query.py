import time
import requests
from datetime import datetime
from data_collection.collection.JsonHandler import JsonHandler
from data_collection.collection.yaml_handler import YamlHandler


# Globals
REALTIME_CFG_PATH = "C:/Users/BCarr/Documents/GitHub/ATS_Project_2024/data_collection/configuration/realtime_config.yaml"
OUTPUT_FOLDER = "C:/Users/BCarr/Documents/GitHub/ATS_Project_2024/data_collection/output/"
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

        output.append({})
        output[-1] = remap_entries(data, non_api_fields, api_fields)

        # Rate limit the query speed based on the rate limit
        # From inside the JSON. Check that the key wasn't valued at null, signifying no rate limit.
        if api_rate_limit is not None:
            time.sleep(60 / api_rate_limit)

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
                        field]  # API field mapping was set to null, dump it as cfg doesn't care to keep.
        except AttributeError:
            continue  # The copy failed of the dict because it was probably an error message.
    
    return remapped_entry


def main():
    realtime_config = YamlHandler.load_config(REALTIME_CFG_PATH)
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
    stock_output += make_queries(api_url, api_key, stock_list, api_rate_limit, api_fields, non_api_fields)
    index_output += make_queries(api_url, api_key, index_list, api_rate_limit, api_fields, non_api_fields)
    commodity_output += make_queries(api_url, api_key, commodity_list, api_rate_limit, api_fields, non_api_fields)

    JsonHandler.write_files(stock_output, OUTPUT_FOLDER, OUTPUT_FILENAME_STOCKS)
    JsonHandler.write_files(index_output, OUTPUT_FOLDER, OUTPUT_FILENAME_INDEX)
    JsonHandler.write_files(commodity_output, OUTPUT_FOLDER, OUTPUT_FILENAME_COMMODITIES)


# Code to only be executed if ran as script
if __name__ == "__main__":
    main()

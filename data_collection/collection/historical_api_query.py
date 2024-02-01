import time
import requests
from data_collection.collection.JsonHandler import JsonHandler
from data_collection.collection.yaml_handler import YamlHandler


# Globals
HISTORICAL_CFG_PATH = "./ATS_Project_2024/data_collection/configuration/historical_config.yaml"
OUTPUT_FOLDER = "./ATS_Project_2024/data_collection/output/"
OUTPUT_FILENAME_STOCKS = "historical_stocks_output.json"
OUTPUT_FILENAME_INDEX = "historical_index_output.json"
OUTPUT_FILENAME_COMMODITIES = "historical_commodity_output.json"


def make_queries(parsed_api_url, parsed_api_key, query_list, api_rate_limit, api_fields, non_api_fields):
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

        # Rate limit the query speed based on the rate limit
        # From inside the JSON. Check that the key wasn't valued at null, signifying no rate limit.
        if api_rate_limit is not None:
            time.sleep(60 / api_rate_limit)

    return output


def remap_entries(response_data, query_item, api_fields, non_api_fields):
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
                    # TODO add more cases later, for the first API this is all we need.
                    # print(f"src: {src}, map_to: {map_to}, input_type: {input_type}, output_type: {output_type}")
                    if input_type == "_string":
                        if output_type == "_string" and src == "_config_name":
                            # Handler for grabbing string name from the configuration file
                            try:
                                entry[map_to] = query_item['name']
                            except TypeError:
                                pass
                except KeyError as e:
                    print(f"Key Error on {query_item}:\n{e}")
                    pass  # TODO make log files entry
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
                        # print(f"KeyError, {field} does not exist in remapped_entry\n{e}")
                        pass
                else:
                    del remapped_entry[field]
                    # dump it as cfg doesn't care to keep.
        except AttributeError as e:
            print(f"Attribute Error on {entry}:\n{e}")
            pass  # The copy failed of the dict because it was probably an error message.
    
    return remapped_entry

def main():
    historical_config = YamlHandler.load_config(HISTORICAL_CFG_PATH)
    stock_output = []
    index_output = []
    commodity_output = []

    # Iterate through each API in the list
    api_url = historical_config['url']
    api_key = historical_config['api_key']
    api_rate_limit = historical_config['rate_limit_per_min']
    api_fields = historical_config['api_fields']
    non_api_fields = historical_config['non_api_fields']
    stock_list = historical_config['stocks']
    index_list = historical_config['index_composites']
    commodity_list = historical_config['commodities']
    stock_output += make_queries(api_url, api_key, stock_list, api_rate_limit, api_fields, non_api_fields)
    index_output += make_queries(api_url, api_key, index_list, api_rate_limit, api_fields, non_api_fields)
    commodity_output += make_queries(api_url, api_key, commodity_list, api_rate_limit, api_fields, non_api_fields)

    JsonHandler.write_files(stock_output, OUTPUT_FOLDER, OUTPUT_FILENAME_STOCKS)
    JsonHandler.write_files(index_output, OUTPUT_FOLDER, OUTPUT_FILENAME_INDEX)
    JsonHandler.write_files(commodity_output, OUTPUT_FOLDER, OUTPUT_FILENAME_COMMODITIES)


if __name__ == "__main__":
    main()

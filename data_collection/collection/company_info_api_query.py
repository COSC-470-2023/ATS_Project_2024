import time
import requests
from datetime import datetime
from data_collection.collection.JsonHandler import JsonHandler
from data_collection.collection.yaml_handler import YamlHandler

# Globals
COMPANY_INFO_CFG_PATH = "./ATS_Project_2024/data_collection/configuration/company_info_config.yaml"
OUTPUT_FOLDER = "./ATS_Project_2024/data_collection/output"
OUTPUT_FILENAME = "company_info_output.json"


def make_queries(parsed_api_url, parsed_api_key, query_list, api_rate_limit, api_fields, non_api_fields):
    output = []
    # Iterate through each stock and make an API call
    for query_itr in range(len(query_list)):
        query_item = query_list[query_itr]

        # Replace the URL parameters with our current API configs
        query = parsed_api_url.replace("{QUERY_PARAMS}", query_item['symbol']).replace("{API_KEY}", parsed_api_key)
        try:
            response = requests.get(query)
            # Convert the response to json and append to list
            data = response.json()
            remapped_entry = {}
        except requests.RequestException as e:
            print(f"api_error {e}")
            continue

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
                        except TypeError:
                            continue
            except KeyError:
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

            except AttributeError:
                continue  # The copy failed of the dict because it was probably an error message.

        output.append({})
        output[-1] = remapped_entry

    return output


def main():
    company_config = YamlHandler.load_config(COMPANY_INFO_CFG_PATH)
    company_output = []
    # TODO make try except
    # Load variables from the configuration files
    url = company_config['url']
    key = company_config['api_key']
    rate_limit = company_config['rate_limit_per_min']
    fields = company_config['api_fields']
    non_api_fields = company_config['non_api_fields']
    company_list = company_config['stocks']
    # Generate output
    company_output = make_queries(url, key, company_list, rate_limit, fields, non_api_fields)
    # Write file
    JsonHandler.write_files(company_output, OUTPUT_FOLDER, OUTPUT_FILENAME)


if __name__ == "__main__":
    main()

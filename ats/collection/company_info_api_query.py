import datetime
import os
import requests

from ats.globals import DIR_CONFIG, DIR_OUTPUT, CONFIG_COMPANY_INFO, OUTPUT_COMPANY_INFO
from ats.util import json_handler
from ats.util import yaml_handler


def make_queries(parsed_api_url, api_key, query_list, api_fields, non_api_fields):
    output = []
    # Iterate through each stock and make an API call
    for query_itr in range(len(query_list)):
        query_item = query_list[query_itr]

        # Replace the URL parameters with our current API configs
        query = parsed_api_url.replace("{QUERY_PARAMS}", query_item['symbol']).replace("{API_KEY}", api_key)
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
                map_to = non_api_fields['mapping']
                input_type = non_api_fields['input_type']
                output_type = non_api_fields['output_type']
                # Handler for "unix_time" conversion to date time
                if input_type is None:
                    if output_type == "_date_time":
                        try:
                            entry[map_to] = str(datetime.datetime.now())
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
    company_config = yaml_handler.load_config(DIR_CONFIG + CONFIG_COMPANY_INFO)
    # TODO make try except
    # Load variables from the configuration files
    url = company_config['url']
    api_key = os.getenv('ATS_API_KEY')
    fields = company_config['api_fields']
    non_api_fields = company_config['non_api_fields']
    company_list = company_config['stocks']
    # Generate output
    company_output = make_queries(url, api_key, company_list, fields, non_api_fields)
    # Write file
    json_handler.write_files(company_output, DIR_OUTPUT, OUTPUT_COMPANY_INFO)


if __name__ == "__main__":
    main()

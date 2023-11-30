import json

import requests
from datetime import date, timedelta
from JsonHandler import JsonHandler

# Globals
BONDS_CFG_PATH = "C:/Users/Jacob/PycharmProjects/SMF_Project_2023/data_collection/configuration/bonds_query_cfg.json"
OUTPUT_FOLDER = "C:/Users/Jacob/PycharmProjects/SMF_Project_2023/data_collection/output"
OUTPUT_FILENAME_BONDS = "bonds_output.json"


def create_date_window(days_queried):
    """
    Takes the inputted number of days and returns a window of dates
    segmented by 90-day intervals for iteration.
    :param days_queried: Number of days to observe from current date
    :return: datetime object containing a list of segmented dates
    """
    total_days = int(days_queried)
    date_windows = []
    num_chunks = total_days // 90  # Give the number of 90-day chunks plus the remainder
    rem = total_days % 90  # Calculate the remaining days that weren't in the 90-day chunks
    end = date.today()
    # For each 90-day chunk run the query
    for chunk in range(num_chunks):
        start = end - timedelta(days=90)
        window = {start: end}
        date_windows.append(window)
        end = start - timedelta(days=1)
    # Handle remainder (days_queried not divisible by 90)
    if rem > 0:
        start = end - timedelta(days=rem)
        window = {start: end}
        date_windows.append(window)
        
    return date_windows


def make_queries(api_url, api_key, api_fields, treasuries, non_api_fields, days_queried):
    bonds_data = []
    windows = create_date_window(days_queried)
    # TODO MAKE TRY EXCEPT BLOCK
    # For each date_window, execute query
    for date_window in windows:
        # Retrieve key value pair from date_window
        start_date_key = list(date_window.keys())
        end_date_value = list(date_window.values())
        start_date = start_date_key[0]
        end_date = end_date_value[0]
        # Replace the URL parameters with our current API configs
        query = (api_url.replace("{START_DATE}", str(start_date))
                 .replace("{END_DATE}", str(end_date))
                 .replace("{API_KEY}", api_key))

        response = requests.get(query)
        # convert the response to json and append to list
        bonds_output = json.loads(response.text)

        for data in bonds_output:
            # Remap the field names to the config, using the values from API fields,
            # as the key, and the values of entry as the values of the new entry.
            entry = dict((zip(api_fields.values(), list(data.values()))))

            # Get name from the config
            # Compare the manually added field to where it should get its data from
            # in the normal fields
            try:
                src = non_api_fields['name']['src']
                map_to = non_api_fields['name']['mapping']
                input_type = non_api_fields['name']['input_type']
                output_type = non_api_fields['name']['output_type']
                # Handler for grabbing the name of treasury from config.
                # This also can handler conversion, so It's needed to not just doa  static mapping in the future.
                if input_type == "_string" and output_type == "_string":
                    if src == "_config_name":
                        entry[map_to] = treasuries[0]['name']
            except KeyError as e:
                print(f"Key Error on api {iter(entry)}:\n{e}")
                pass  # TODO make log files entry

            # Append the modified entry to the output
            bonds_data.append(entry)
    return bonds_data


def main():
    bond_config = JsonHandler.load_config(BONDS_CFG_PATH)
    output = []
    # TODO make try except
    for api in range(len(bond_config)):
        # Load variables from the configuration
        url = bond_config[api]['url']
        key = bond_config[api]['api_key']
        api_fields = bond_config[api]['api_fields']
        non_api_fields = bond_config[api]['non_api_fields']
        days_queried = bond_config[api]['days_queried']

        # TODO Handle adding name via a data field or something so its not hanging out.
        #   Should be done in a way that an API that doesnt only return one treasury can use it.
        treasuries = bond_config[api]['treasuries']

        output = make_queries(url, key, api_fields, treasuries, non_api_fields, days_queried)

    JsonHandler.write_files(output, OUTPUT_FOLDER, OUTPUT_FILENAME_BONDS)


if __name__ == "__main__":
    main()

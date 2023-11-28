import json
import os
import errno
import requests
from datetime import date
from datetime import timedelta


# Loads the configuration file.
def load_config():
    config_path = "../configuration/bonds_query_cfg.json"
    with open(config_path, 'r') as file:
        try:
            config = json.load(file)
            return config
        except IOError:
            print(f"IOError while accessing bonds query config file at path: {config_path}")
            exit(-1001)  # Exit program with code -1001 (Invalid config path)
        except json.JSONDecodeError as e:
            print(f"JSON decoding encountered an error while decoding {config_path}:\n{e}")
            exit(-1002)  # Exit program with code -1002 (Invalid config structure)


def create_date_window(days_queried):
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
        end = start
    # Handle remainder (days_queried not divisible by 90)
    if rem > 0:
        start = end - timedelta(days=rem)
        window = {start: end}
        date_windows.append(window)
    return date_windows


def make_queries(api_url, api_key, api_fields, non_api_fields, days_queried):
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
        query = api_url.replace("{START_DATE}", str(start_date)).replace("{END_DATE}", str(end_date)).replace("{API_KEY}", api_key)
        response = requests.get(query)
        # Convert the response to json
        bonds_output = json.loads(response.text)
        for data in bonds_output:
            # Get name and mapping from config
            map_to = non_api_fields['name']['mapping']
            name = non_api_fields['name']['src']
            bonds_dict = {map_to: name}
            # Format output
            bonds_dict.update(zip(api_fields.values(), list(data.values())))
            # Add non_api_fields field to output
            bonds_data.append(bonds_dict)
    return bonds_data


def write_file(bond_output):
    output_dir = "../output/"
    if not os.path.exists(os.path.dirname(output_dir)):
        try:
            os.makedirs(os.path.dirname(output_dir))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open("../output/bonds_output.json", "w") as outfile:
        json.dump(bond_output, outfile, indent=2)


def main():
    bond_config = load_config()
    output = []
    # TODO make try except
    for entry in range(len(bond_config)):
        # Load variables from the configuration
        url = bond_config[entry]['url']
        key = bond_config[entry]['api_key']
        api_fields = bond_config[entry]['api_fields']
        non_api_fields = bond_config[entry]['non_api_fields']
        days_queried = bond_config[entry]['days_queried']
        output = make_queries(url, key, api_fields, non_api_fields, days_queried)
    write_file(output)


# Code to only be executed if ran as script
if __name__ == "__main__":
    main()

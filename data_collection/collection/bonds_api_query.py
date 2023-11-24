# Get data from the bonds API list file
# Parse the json so we know what our URL and keys are
# Iterate through the stocks using the key and url, then move onto the next API
# TODO make the directories for file read and out absolute ie not relative locations to the script
import json
import os
import errno
import requests
from datetime import datetime
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


def make_queries(api_url, api_key, api_fields, non_api_fields):
    bonds_config = load_config() # init as dict
    bonds_dict = {}

    # Iterate through each API in the list
    for api_config in bonds_config:
        # Get the parameters for the query, including the list of start end dates
        api_url = api_config['url']
        api_key = api_config['api_key']

        # Iterate through each start-end date pair and make an API call
        # date range yesterday - today
        today = datetime.today()
        yesterday = today - timedelta(days=1)

        start_date = yesterday.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        # Replace the URL parameters with our current API configs
        query = api_url.replace("{START_DATE}", start_date).replace("{END_DATE}", end_date).replace("{API_KEY}", api_key)

        response = requests.get(query)
        # convert the response to json
        bonds_data = json.loads(response.text)
        print(bonds_data)
        config_fields_dict = bonds_config[0].get('api_fields')
        print(config_fields_dict)

        name = bonds_config[0].get('name')
        print(name)
        # convert bonds list to dictionary
        bonds_dict = dict(zip(config_fields_dict.values(), list(bonds_data[0].values())))
        print("bonds dictionary: ", bonds_dict)
        #bonds_dict.update(name)

    return bonds_dict


def reformat(config, data):
    new_key_list = []

    for entry in data:
        formatted_data = {
            "_bond_name": config['name'],
        }
        for api_field, non_api_field in config['api_fields'].items():
            formatted_data[api_field] = entry.get(non_api_field, None)

        new_key_list.append(formatted_data)

    return new_key_list

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

    for entry in range(len(bond_config)):
        # Load variables from the configuration
        url = bond_config[entry]['url']
        key = bond_config[entry]['api_key']
        api_fields = bond_config[entry]['api_fields']
        non_api_fields = bond_config[entry]['non_api_fields']

    # call make queries
    output = make_queries(url, key, api_fields, non_api_fields)
    write_file(output)

# code to only be executed if ran as script
if __name__ == "__main__":
    main()

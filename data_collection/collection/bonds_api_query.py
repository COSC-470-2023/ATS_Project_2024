# Get data from the bonds API list file
# Parse the json so we know what our URL and keys are
# Iterate through the stocks using the key and url, then move onto the next API
# TODO make the directories for file read and out absolute ie not relative locations to the script
import json
import os
import errno
import requests
from datetime import datetime, date
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
    bonds_config = load_config()  # init as dict
    bonds_dict = {}

    # TODO MAKE TRY EXCEPT BLOCK
    # Iterate through each API in the list
    for api_config in bonds_config:
        # Get the parameters for the query, including the day range to be queried
        api_url = api_config['url']
        api_key = api_config['api_key']
        # pull date window - defaulted to 7 (hard requirement). Can be configured between 2-90
        days_queried = int(api_config['date_windows']['days_queried'])
        if days_queried < 2 or days_queried > 90:
            print("Days queried cannot be less than 2 or greater than 90.")
            exit(-1003)  # Exit with code -1003 (Invalid input)

        # make an API call for the last week of bonds data
        # date range days_queried (configuration) - today
        end_date = date.today()
        start_date = end_date - timedelta(days=days_queried)
        print("start: ", start_date, " end: ", end_date)
        # add to date windows

        # Replace the URL parameters with our current API configs
        query = api_url.replace("{START_DATE}", str(start_date)).replace("{END_DATE}", str(end_date)).replace("{API_KEY}", api_key)
        response = requests.get(query)

        # convert the response to json
        bonds_data = json.loads(response.text)
        # read in common list of keys
        config_fields_dict = bonds_config[0].get('api_fields')
        # create new key value pair '_bond_name: name'
        map_to = bonds_config[0].get('non_api_fields').get('name').get('mapping')
        name = bonds_config[0].get('name')
        new_kv_pair = {map_to : name}

        for i in range(len(bonds_data)):
            # format output
            bonds_dict = dict(zip(config_fields_dict.values(), list(bonds_data[i].values())))
            # add new key value pair
            bonds_dict = {**new_kv_pair, **bonds_dict}
            bonds_data[i] = bonds_dict

    return bonds_data


#def make_historical_query(url, key):
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
        # call make queries
        output = make_queries(url, key, api_fields, non_api_fields)
    write_file(output)

# code to only be executed if ran as script
if __name__ == "__main__":
    main()

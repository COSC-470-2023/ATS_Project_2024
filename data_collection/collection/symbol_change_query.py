# Get data from the symbol change API list file
# Parse the json so we know what our URL and keys are
# Iterate through the stocks using the key and url, then move onto the next API
# TODO make the directories for file read and out absolute ie not relative locations to the script

import json
import time
import os
import errno
import requests
from datetime import date

# Loads the configuration file.
def load_config():
    config_file = open("Config/Symbol_Change.json", "r")
    config = json.load(config_file)
    return config


def make_queries(parsed_api_url, parsed_api_key):
    output = []
    
    query = parsed_api_url.replace("{API_KEY}", parsed_api_key)
    response = requests.get(query)

    # convert the response to json and append to list
    data = response.json()

    output += data
    return output

def get_symbol_change(symbol_change_data):
    symbol_change_list = []
    today_date = date.today()
    #convert date to string
    today = today_date.strftime('%Y-%m-%d')
    
    for item in range(len(symbol_change_query)):
        item_date = JSON_config[item]['date']
        try: 
            if item_date == today:
                symbol_change_list.append(JSON_config[item])
                print(JSON_config[item])
        except (ValueError, TypeError) as e:
            print(f"Error processing date: {e}")
    
    return symbol_change_list

def write_files(symbol_json):

    output_dir = "Output/"
    if not os.path.exists(os.path.dirname(output_dir)):
        try:
            os.makedirs(os.path.dirname(output_dir))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open("Output/Symbol_Change_List.json", "w") as outfile:
        json.dump(symbol_json, outfile, indent=4)


# code to only be executed if ran as script
if __name__ == "__main__":
    JSON_config = load_config()
    symbol_change_output = []
    symbol_change = []
    # Iterate through each API in the list
    for api in range(len(JSON_config)):
        api_url = JSON_config[api]['url']
        api_key = JSON_config[api]['api_key']

    symbol_change_output = make_queries(api_url, api_key)
   
    get_symbol_change(symbol_change_output)
    
    write_files(symbol_change)
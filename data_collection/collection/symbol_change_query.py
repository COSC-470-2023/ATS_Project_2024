# Get data from the symbol change API list file
# Parse the json so we know what our URL and keys are
# Iterate through the stocks using the key and url, then move onto the next API
# TODO Add a function to make a backup of the system configuration before writing changes

import json
import time
import os
import errno
import requests
from datetime import date

# Variable to track symbols that are changed for global usage
# A dict of OLD_SYMBOL:NEW_SYMBOL key, value pairs
symbol_changelog = {}
# Global flag for symbol changes
symbol_changed = False

# Loads the system configuration file specifying all symbols the system is tracking
def load_system_config():
    # TODO Define explicit file paths instead of relative file paths
    config_path = "../configuration/stock_index_comp_comm_list.json"
    try:
        config_file = open(config_path, "r")
        config = json.load(config_file)
        return config
    # TODO Implement system logging when defined to log/flag a failure in this component
    except IOError:
        print(f"IOError while accessing configuration file at path: {config_path}")
        exit(1)   

# Loads the system query configuration file
def load_query_config():
    # TODO Define explicit file paths instead of relative file paths
    query_config_path = "../configuration/symbol_change.json"
    try:
        query_config_file = open(query_config_path, "r")
        query_config = json.load(query_config_file)
        return query_config
    # TODO Implement system logging when defined to log/flag a failure in this component
    except IOError:
        print(f"IOError while accessing configuration file at path: {query_config_path}")
        exit(1)

# Using provided API URL and Key, queries and appends results to an unmodified raw output
def make_queries(parsed_api_url, parsed_api_key):
    output = []
    query = parsed_api_url.replace("{API_KEY}", parsed_api_key)
    response = requests.get(query)
    # Convert the response to json and append to list
    data = response.json()
    output += data
    return output

# Trim the raw output to remove changes that are not from the current date
def trim_query_output(raw_API_output):
    modified_API_output = []
    today_date = date.today()
    #Convert date to string format
    today = today_date.strftime('%Y-%m-%d')
    for item in range(len(raw_API_output)):
        item_date = raw_API_output[item]['date']
        try: 
            if item_date == today:
                modified_API_output.append(raw_API_output[item])
                # Log the symbol as changed for use later
                global symbol_changed 
                symbol_changed = True
                global symbol_changelog
                symbol_changelog |= {modified_API_output[item]['oldSymbol']:modified_API_output[item]['newSymbol']}
                # print(raw_API_output[item])
        # TODO Implement system logging when defined to log/flag a failure in this component
        except (ValueError, TypeError) as e:
            print(f"Error processing date: {e}")
            exit(1)
    return modified_API_output

# Modify the structure of the symbol change list to include oldName as a field and maps field names to expected output names
# TODO Pull oldName from system_config
# NOTE Consider how multiple API sources are handled in this process
def modify_output_list(symbol_change_list, system_config):
    modified_symbols_list = []
    for entry in symbol_change_list:
        date = entry['date']
        newName = entry['name']
        oldSymbol = entry['oldSymbol']
        newSymbol = entry['newSymbol']
        # Currently only works with one API in the configuration list
        oldName = ""
        modified_symbols_list.append({"_change_date": date, "_change_newName": newName, "_change_oldName": oldName, "_change_newSymbol": newSymbol, "_change_oldSymbol": oldSymbol})
    return modified_symbols_list

def write_output_file(symbol_change_json):
    # TODO Define explicit file paths instead of relative file paths
    output_dir = "../output/"
    if not os.path.exists(os.path.dirname(output_dir)):
        try:
            os.makedirs(os.path.dirname(output_dir))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open("../output/Symbol_Change_List.json", "w") as outfile:
        json.dump(symbol_change_json, outfile, indent=2)

# Modifies the symbols that have been changed in the system configuration file and returns the modified list to be written
# NOTE Currently assumes only one API configuration exists in the system
def modify_system_config(system_config_json):
    modified_system_config = system_config_json
    # For each dictionary in list
    for entry in modified_system_config:
        # For each key in dictionary
        for key, value in entry.items():
            # If the key matches the specified condition, enter and assess if the symbol value is in the changelog
            if key == 'index_composites':
                for index in value:
                    if index['symbol'] in symbol_changelog:
                        index['symbol'] = symbol_changelog[index['symbol']]
            elif key == 'stocks':
                for stock in value:
                    if stock['symbol'] in symbol_changelog:
                        stock['symbol'] = symbol_changelog[stock['symbol']]
            elif key == 'commodities':
                for commodity in value:
                    if commodity['symbol'] in symbol_changelog:
                        commodity['symbol'] = symbol_changelog[commodity['symbol']]
            else:
                continue
    return modified_system_config

def write_system_config_changes(modified_system_config):
    # TODO Define explicit file paths instead of relative file paths
    output_dir = "../configuration/"
    if not os.path.exists(os.path.dirname(output_dir)):
        try:
            os.makedirs(os.path.dirname(output_dir))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open("../configuration/stock_index_comp_comm_list.json", "w") as outfile:
        json.dump(modified_system_config, outfile, indent=2)


def main():
    symbol_query_config = load_query_config()
    raw_API_query_output = []
    symbol_change_output = []
    # Iterate through each API in the list
    for api in range(len(symbol_query_config)):
        api_url = symbol_query_config[api]['url']
        api_key = symbol_query_config[api]['api_key']
        # Run queries for each API and append to raw output
        raw_API_query_output += make_queries(api_url, api_key)
    modified_API_output = trim_query_output(raw_API_query_output)
    # If symbols for current day have changed, perform the expected component tasks
    # If no symbols have changed, proceed to final activities
    if symbol_changed:
        print('Symbols changed. Performing system change tasks.')
        system_config = load_system_config()
        # Write modified output to symbol_change file
        symbol_change_output = modify_output_list(modified_API_output, system_config)
        # Modify changed symbols in system config file
        modified_system_config = modify_system_config(system_config)
        # Write changes to system config file
        write_system_config_changes(modified_system_config)
    # Write empty list, or changedlist to output file, exit with success code
    print('Task complete.')
    write_output_file(symbol_change_output)
    exit(0)

# Code to be executed when ran as script
if __name__ == "__main__":
    main()
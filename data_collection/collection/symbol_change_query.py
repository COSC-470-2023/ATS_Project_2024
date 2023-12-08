# Get data from the symbol change API list file
# Parse the json so we know what our URL and keys are
# Iterate through the stocks using the key and url, then move onto the next API
# Backup and modify config files
# Write an output file in the expected system format from the API queries

import requests
from datetime import date
from JsonHandler import JsonHandler

# GLOBALS
# Variable to track symbols that are changed for global usage
# A dict of OLD_SYMBOL:NEW_SYMBOL key, value pairs
symbol_changelog = {}
# Global flag for symbol changes
symbol_changed = False
##########################################################################
# FILE/PATH VARIABLES
SYSTEM_CONFIG_PATH_LIST = ["./SMF_Project_2023/data_collection/configuration/realtime_query_cfg.json", 
                            "./SMF_Project_2023/data_collection/configuration/company_info_query_cfg.json",
                            "./SMF_Project_2023/data_collection/configuration/historical_query_cfg.json"]
CONFIG_PATH = "./SMF_Project_2023/data_collection/configuration/"
CONFIG_BACKUP_PATH = "./SMF_Project_2023/data_collection/configuration/backup/"
QUERY_CONFIG_PATH = "./SMF_Project_2023/data_collection/configuration/symbol_change_query_cfg.json"
OUTPUT_PATH = "./SMF_Project_2023/data_collection/output/"
OUTPUT_FILE_NAME = "symbol_change_list.json"
##########################################################################

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
    # Convert date to string format
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
                symbol_changelog |= {modified_API_output[item]['oldSymbol']: modified_API_output[item]['newSymbol']}
                # print(raw_API_output[item])
        # TODO Implement system logging when defined to log/flag a failure in this component
        except (ValueError, TypeError) as e:
            print(f"Error processing date: {e}")
            exit(1)
    return modified_API_output


# Function to pull old name from system config files
def get_old_name(system_config_json, old_symbol):
    # Iterate over each config entry in the system config
    for config_entry in system_config_json:
        # Iterate over the keys in the config
        for key in ['index_composites', 'stocks', 'commodities', 'companies']:
            # If the current key is present in the config entry, check if the old_symbol matches the symbol in the index
            if key in config_entry:
                for index in config_entry[key]:
                    if old_symbol == index['symbol']:
                        # Return the name if a match is found
                        return index['name']
    # Return an empty string if no match is found
    return ""


# Modify the structure of the symbol change list to include oldName as a field and maps field names to expected output names
# TODO Pull oldName from system_config
# NOTE Consider how multiple API sources are handled in this process
def modify_output_list(symbol_change_list, system_config_json):
    modified_symbols_list = []
    oldName = ""
    
    for entry in symbol_change_list:
        date = entry['date']
        newName = entry['name']
        oldSymbol = entry['oldSymbol']
        newSymbol = entry['newSymbol']
        
        # Currently only works with one API in the configuration list
        oldName = get_old_name(system_config_json, oldSymbol)
        modified_symbols_list.append({"_change_date": date, "_change_newName": newName, "_change_oldName": oldName,
                                      "_change_newSymbol": newSymbol, "_change_oldSymbol": oldSymbol})
    return modified_symbols_list


# Modifies the symbols that have been changed in the system configuration file and returns the modified list to be written
# NOTE Currently assumes only one API configuration exists in the system
def modify_system_config(system_config_json):
    modified_system_config = system_config_json
    # For each dictionary in list
    for entry in modified_system_config:
        # For each key in dictionary
        for key, value in entry.items():
            # If the key matches the specified condition, enter and assess if the symbol value is in the changelog
            if key in ['index_composites', 'stocks', 'commodities', 'companies']:
                for index in value:
                    symbol = index['symbol']
                    if symbol in symbol_changelog:
                        index['symbol'] = symbol_changelog[symbol]
            else:
                continue
    
    return modified_system_config


def main():
    # Load the symbol change query config
    symbol_query_config = JsonHandler.load_config(QUERY_CONFIG_PATH)
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
        
        for path in SYSTEM_CONFIG_PATH_LIST:
            system_config = JsonHandler.load_config(path)
            symbol_change_output = modify_output_list(modified_API_output, system_config)

        for system_config_path in SYSTEM_CONFIG_PATH_LIST:
            system_config = JsonHandler.load_config(system_config_path)
            # Pull config file name from path
            system_config_name = system_config_path.split("/")[-1]
            # Write a backup config file to the backup directory
            system_config_name_backup = system_config_name + "_" + str(date.today()) + "~"
            JsonHandler.write_files(system_config, CONFIG_BACKUP_PATH, system_config_name_backup)
            # Modify changed symbols in system config file
            modified_system_config = modify_system_config(system_config)
            # Write changes to system config file
            JsonHandler.write_files(modified_system_config, CONFIG_PATH, system_config_name)
    
    # Write empty list, or changedlist to output file, exit with success code 
    JsonHandler.write_files(symbol_change_output, OUTPUT_PATH, OUTPUT_FILE_NAME)
    print(f'Task complete. Symbols changed for ' + str(date.today()) + ': ' + str(symbol_changed))
    exit(0)


# Code to be executed when ran as script
if __name__ == "__main__":
    main()

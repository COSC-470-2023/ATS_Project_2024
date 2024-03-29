import datetime
import json
import os
import requests

from ats import loguru_init
from ats.globals import DIR_CONFIG, DIR_OUTPUT, CONFIG_BONDS, OUTPUT_BONDS
from ats.util import json_handler
from ats.util import yaml_handler

# Loguru init
logger = loguru_init.initialize()

def create_date_window(days_queried):
    """
    Takes the inputted number of days and returns a window of dates
    segmented by 90-day intervals for iteration.
    :param days_queried: Number of days to observe from current date
    :return: datetime object containing a list of segmented dates
    """
    date_windows = []
    logger.info("creating Bonds Date Windows")
    try:
        total_days = int(days_queried)
        num_chunks = total_days // 90  # Give the number of 90-day chunks plus the remainder
        rem = total_days % 90  # Calculate the remaining days that weren't in the 90-day chunks
        end = datetime.date.today()
        # For each 90-day chunk run the query
        for chunk in range(num_chunks):
            start = end - datetime.timedelta(days=90)
            window = {start: end}
            date_windows.append(window)
            end = start - datetime.timedelta(days=1)
        # Handle remainder (days_queried not divisible by 90)
        if rem > 0:
            start = end - datetime.timedelta(days=rem)
            window = {start: end}
            date_windows.append(window)
    except Exception as e:
        logger.error(e)
    logger.info("Bonds Date Windows creation complete")
    return date_windows


def make_queries(api_url, api_key, api_fields, treasuries, non_api_fields, days_queried):
    bonds_data = []
    logger.info("Bonds Query starting")
    try:
        windows = create_date_window(days_queried)
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
            bonds_output = []
            try:
                response = requests.get(query)
                # convert the response to json and append to list
                bonds_output = json.loads(response.text)
            except requests.RequestException as e:
                logger.debug(f"api_error {e}")

            for data in bonds_output:
                # Remap the field names to the config, using the values from API fields,
                # as the key, and the values of entry as the values of the new entry.
                entry = dict((zip(api_fields.values(), list(data.values()))))

                try:
                    # Get name from the config
                    # Compare the manually added field to where it should get its data from
                    # in the normal fields
                    src = non_api_fields['name']['src']
                    map_to = non_api_fields['name']['mapping']
                    input_type = non_api_fields['name']['input_type']
                    output_type = non_api_fields['name']['output_type']
                    # Handler for grabbing the name of treasury from config.
                    # This also can handler conversion, so It's needed to not just do a static mapping in the future.
                    if input_type == "_string" and output_type == "_string":
                        if src == "_config_name":
                            entry[map_to] = treasuries['name']
                except KeyError as e:
                    logger.error(f"Key Error on api {iter(entry)}:\n{e}")

                # Append the modified entry to the output
                bonds_data.append(entry)
    except Exception as e:
        logger.error(e)

    logger.info("Bonds Query complete")
    return bonds_data


def main():
    try:
        bond_config = yaml_handler.load_config(DIR_CONFIG + CONFIG_BONDS)
        #  Load variables from the configuration
        url = bond_config['url']
        api_key = os.getenv('ATS_API_KEY')
        api_fields = bond_config['api_fields']
        non_api_fields = bond_config['non_api_fields']
        days_queried = bond_config['days_queried']
        treasuries = bond_config['treasuries']

        logger.info("creating Bonds Output")
        output = make_queries(url, api_key, api_fields, treasuries, non_api_fields, days_queried)
        logger.info("Bonds Output created successfully")

        logger.info("writing Bonds Query output file")
        json_handler.write_files(output, DIR_OUTPUT, OUTPUT_BONDS)
        logger.info("Bonds Query output file write complete")
    except Exception as e:
        logger.debug(e)


if __name__ == "__main__":
    main()

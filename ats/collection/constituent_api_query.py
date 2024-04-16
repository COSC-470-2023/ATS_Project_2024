import os

from ats import globals
from ats.logger import Logger
from ats.util import api_handler, file_handler, data_handler

logger = Logger.instance()

# Constants
CONSTITUENT = 'constituent'
STOCKS = 'stocks'


def main():
    """
    Queries the API for the most current list of companies on the specified constituent.
    Reads in all data collection configuration files, then updates them with the current company list.
    This function sets up logging, reads configuration, fetches and processes data based on
    parameters in index_config.yaml.
    :Success: Updates YAML files.
    :Failure: Raise exception and log error.
    """
    try:
        logger.info('Starting constituent collection')
        constituent_config = file_handler.read_yaml(globals.FN_CFG_CONSTITUENT)

        logger.debug('Fetching raw data from API')
        endpoint = constituent_config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        constituent = constituent_config[CONSTITUENT]
        fetcher = api_handler.Fetcher(endpoint, api_key)
        raw_data = fetcher.fetch(constituent)

        logger.debug('Processing raw data')
        api_fields = constituent_config[globals.FIELD_CFG_API]
        data = data_handler.process_raw_data(raw_data, api_fields)

        config_filenames = [
            globals.FN_CFG_COMPANIES,
            globals.FN_CFG_REALTIME,
            globals.FN_CFG_HISTORICAL
        ]
        logger.debug(f'Writing processed data to config files: {config_filenames}')
        for config_filename in config_filenames:
            config = file_handler.read_yaml(config_filename)
            config[STOCKS] = data
            file_handler.write_yaml(config, config_filename)
        logger.success('Constituent collection complete')
    except Exception as e:
        logger.error(f"Error when gathering constituent values: {e}")
        raise


if __name__ == "__main__":
    main()

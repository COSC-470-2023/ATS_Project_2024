import os

from ats import globals
from ats.logger import Logger
from ats.util import api_handler, file_handler, data_handler

logger = Logger.instance()

# Constants
CONSTITUENT = 'constituent'
STOCKS = 'stocks'


def main():
    try:
        logger.info('Starting constituent collection')
        constituent_config = file_handler.read_yaml(globals.FN_CFG_CONSTITUENT)

        logger.info('Fetching raw data from API')
        endpoint = constituent_config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        constituent = constituent_config[CONSTITUENT]
        fetcher = api_handler.Fetcher(endpoint, api_key)
        raw_data = fetcher.fetch(constituent)

        logger.info('Processing raw data')
        api_fields = constituent_config[globals.FIELD_CFG_API]
        data = data_handler.process_raw_data(raw_data, api_fields)

        logger.inf('Writing processed data to output')
        config_filenames = [
            globals.FN_CFG_COMPANIES,
            globals.FN_CFG_REALTIME,
            globals.FN_CFG_HISTORICAL
        ]
        for config_filename in config_filenames:
            config = file_handler.read_yaml(config_filename)
            config[STOCKS] = data
            file_handler.write_yaml(config, config_filename)
        logger.info('Constituent collection complete')
    except Exception as e:
        logger.debug(e)
        raise


if __name__ == "__main__":
    main()

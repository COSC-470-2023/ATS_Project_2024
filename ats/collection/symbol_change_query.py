import os

from ats import globals
from ats.logger import Logger
from ats.util import api_handler, data_handler, file_handler

logger = Logger.instance()


def main():
    try:
        logger.info('Starting symbol change collection')
        config = file_handler.read_yaml(globals.FN_CFG_SYMBOL_CHANGE)

        logger.info('Fetching raw data from API')
        endpoint = config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        fetcher = api_handler.Fetcher(endpoint, api_key)
        raw_data = fetcher.fetch()

        logger.info('Processing raw data')
        api_fields = config[globals.FIELD_CFG_API]
        data = data_handler.process_raw_data(raw_data,
                                             api_fields)

        logger.info('Writing processed data to output')
        file_handler.write_json(data, globals.FN_OUT_SYMBOL_CHANGE)
        logger.info('Symbol change collection complete')
    except Exception as e:
        logger.error(e)
        raise

if __name__ == "__main__":
    main()

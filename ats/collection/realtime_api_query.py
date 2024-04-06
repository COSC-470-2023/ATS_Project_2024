import datetime
import os

from ats import globals
from ats.logger import Logger
from ats.util import api_handler, data_handler, file_handler

logger = Logger.instance()

# Constants
COMMODITIES = 'commodities'
INDEXES = 'index_composites'
STOCKS = 'stocks'
SYMBOL = 'symbol'
TIMESTAMP = 'timestamp'
REALTIME_DATE = '_realtime_date'


@api_handler.query_builder
def build_queries(query_manager: api_handler.QueryManager,
                  config_data: list[dict]):
    # TODO: write docstring
    for entry in config_data:
        query_manager.add(entry[SYMBOL])

  
def make_mapping() -> data_handler.Mapping:
    # TODO: write docstring

    @data_handler.mapping_callback
    def realtime_date(kwargs: data_handler.Kwargs) -> str:
        timestamp = kwargs[data_handler.ENTRY][TIMESTAMP]
        date_time = datetime.datetime.fromtimestamp(timestamp)
        return str(date_time)

    mapping = data_handler.Mapping()
    mapping.add(REALTIME_DATE, realtime_date)
    return mapping


def main():
    try:
        logger.info('Starting realtime collection')
        realtime_config = file_handler.read_yaml(globals.FN_CFG_REALTIME)

        logger.info('Fetching raw data from API')
        endpoint = realtime_config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        fetcher = api_handler.Fetcher(endpoint, api_key, build_queries)
        commodities = realtime_config[COMMODITIES]
        indexes = realtime_config[INDEXES]
        stocks = realtime_config[STOCKS]
        raw_commodities_data = fetcher.fetch(commodities)
        raw_indexes_data = fetcher.fetch(indexes)
        raw_stocks_data = fetcher.fetch(stocks)

        logger.info('Processing raw data')
        api_fields = realtime_config[globals.FIELD_CFG_API]
        non_api_fields = realtime_config[globals.FIELD_CFG_NON_API]
        mapping = make_mapping()

        commodities_data = data_handler.process_raw_data(raw_commodities_data,
                                                         api_fields,
                                                         non_api_fields,
                                                         mapping)
        indexes_data = data_handler.process_raw_data(raw_indexes_data,
                                                     api_fields,
                                                     non_api_fields,
                                                     mapping)
        stocks_data = data_handler.process_raw_data(raw_stocks_data,
                                                    api_fields,
                                                    non_api_fields,
                                                    mapping)

        logger.info('Writing processed data to output')
        file_handler.write_json(commodities_data,
                                globals.FN_OUT_REALTIME_COMMODITIES)
        file_handler.write_json(indexes_data,
                                globals.FN_OUT_REALTIME_INDEX)
        file_handler.write_json(stocks_data,
                                globals.FN_OUT_REALTIME_STOCKS)
        logger.info('Realtime collection complete')
    except Exception as e:
        logger.error(e)
        raise


if __name__ == "__main__":
    main()

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
    """
    Builds queries for fetching realtime data based on provided symbols for the current market day. Will return no data
    on non market days.
    :param query_manager: The query manager object to which queries will be added.
    :param config_data: A list of dictionaries, each containing the symbol for a particular commodity, index, or stock.
    """
    for entry in config_data:
        query_manager.add(entry[SYMBOL])

  
def make_mapping() -> data_handler.Mapping:
    """
    Creates a mapping for converting raw API data timestamps into human-readable dates.
    :return: A mapping object configured to transform timestamp data into datetime strings.
    """
    @data_handler.mapping_callback
    def realtime_date(kwargs: data_handler.Kwargs) -> str:
        """
        Converts a timestamp from the raw data into a datetime string.
        :param kwargs: Contextual keyword arguments containing the entry data.
        :return: The converted datetime string if timestamp is found, otherwise returns 'KEY_NOT_FOUND'.
        """
        if TIMESTAMP in kwargs[data_handler.ENTRY]:
            timestamp = kwargs[data_handler.ENTRY][TIMESTAMP]
            date_time = datetime.datetime.fromtimestamp(timestamp)
            return str(date_time)
        else:
            return data_handler.KEY_NOT_FOUND

    mapping = data_handler.Mapping()
    mapping.add(REALTIME_DATE, realtime_date)
    return mapping


def main():
    """
    Executes data collection for realtime stock, commodity, and index data, processes the raw data,
    and stores the results in JSON format. This function sets up logging, reads configuration,
    fetches and processes data based on parameters in realtime_config.yaml.
    """
    try:
        logger.info('Starting realtime collection')
        realtime_config = file_handler.read_yaml(globals.FN_CFG_REALTIME)

        logger.debug('Fetching raw data from API')
        endpoint = realtime_config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        fetcher = api_handler.Fetcher(endpoint, api_key, build_queries)
        commodities = realtime_config[COMMODITIES]
        indexes = realtime_config[INDEXES]
        stocks = realtime_config[STOCKS]
        raw_commodities_data = fetcher.fetch(commodities)
        raw_indexes_data = fetcher.fetch(indexes)
        raw_stocks_data = fetcher.fetch(stocks)

        logger.debug('Processing raw data')
        api_fields = realtime_config[globals.FIELD_CFG_API]
        non_api_fields = realtime_config[globals.FIELD_CFG_NON_API]
        mapping = make_mapping()

        logger.debug('Processing commodities')
        commodities_data = data_handler.process_raw_data(raw_commodities_data,
                                                         api_fields,
                                                         non_api_fields,
                                                         mapping)

        logger.debug('Processing indexes')
        indexes_data = data_handler.process_raw_data(raw_indexes_data,
                                                     api_fields,
                                                     non_api_fields,
                                                     mapping)

        logger.debug('Processing stocks')
        stocks_data = data_handler.process_raw_data(raw_stocks_data,
                                                    api_fields,
                                                    non_api_fields,
                                                    mapping)

        logger.debug(f'Writing processed data to files: {globals.FN_OUT_REALTIME_COMMODITIES} '
                     f'{globals.FN_OUT_REALTIME_INDEX} {globals.FN_OUT_REALTIME_STOCKS}')
        file_handler.write_json(commodities_data,
                                globals.FN_OUT_REALTIME_COMMODITIES)
        file_handler.write_json(indexes_data,
                                globals.FN_OUT_REALTIME_INDEX)
        file_handler.write_json(stocks_data,
                                globals.FN_OUT_REALTIME_STOCKS)
        logger.success('Realtime collection complete')
    except Exception as e:
        logger.error(e)
        raise


if __name__ == "__main__":
    main()

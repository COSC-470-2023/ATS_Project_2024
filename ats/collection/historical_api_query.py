import os
import datetime

from ats import globals
from ats.logger import Logger
from ats.util import api_handler, data_handler, file_handler

logger = Logger.instance()

# Constants
COMMODITIES = 'commodities'
INDEXES = 'index_composites'
STOCKS = 'stocks'
HISTORICAL = 'historical'
HISTORICAL_NAME = '_historical_name'
NAME = 'name'
SYMBOL = 'symbol'


@api_handler.query_builder
def build_queries(query_manager: api_handler.QueryManager,
                  config_data: list[dict],
                  days: int,
                  date: datetime.date):
    """
    Builds queries for fetching historical data based on provided symbols over a specified time period.
    :param query_manager: Utility class. Builds API query URI.
    :param config_data: List of dictionaries containing the SYMBOL and NAME of entities.
    :param days: Number of days in the past to collect data for, from today. (Default: 1095)
    :param date: Current date. Used to specify date ranges.
    """
    start_date = date - datetime.timedelta(days=days)
    end_date = date
    for entry in config_data:
        query_manager.add(entry[SYMBOL], str(start_date), str(end_date))


def make_mapping(config_data: list[dict]) -> data_handler.Mapping:
    """
    Creates a mapping from API data fields to internal non-api-fields using the config data.

    :param config_data: List of dictionaries containing the SYMBOL and NAME for mapping.
    :return: A Mapping object.
    """
    symbol_name_mapping = {}
    for entry in config_data:
        symbol_name_mapping[entry[SYMBOL]] = entry[NAME]

    @data_handler.mapping_callback
    def historical_name(kwargs: data_handler.Kwargs) -> str:
        # Fetches historical name based on symbol if present, else returns a not found key.
        if SYMBOL in kwargs[data_handler.ENTRY]:
            symbol = kwargs[data_handler.ENTRY][SYMBOL]
            return symbol_name_mapping[symbol]
        else:
            return data_handler.KEY_NOT_FOUND

    mapping = data_handler.Mapping()
    mapping.add(HISTORICAL_NAME, historical_name)
    return mapping


def main():
    """
    Executes data collection for historical stock, commodity, and index data, processes the raw data,
    and stores the results in JSON format. This function sets up logging, reads configuration,
    fetches and processes data based on parameters in historical_config.yaml.
    """
    try:
        logger.info('Starting historical collection')
        historical_config = file_handler.read_yaml(globals.FN_CFG_HISTORICAL)

        logger.info('Fetching raw data from API')
        endpoint = historical_config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        fetcher = api_handler.Fetcher(endpoint, api_key, build_queries)
        commodities = historical_config[COMMODITIES]
        indexes = historical_config[INDEXES]
        stocks = historical_config[STOCKS]
        days = os.getenv(globals.ENV_DAYS_QUERIED)
        days = int(days)
        date = datetime.date.today()
        logger.debug(f'Creating historical query for {days} days.')
        raw_commodities_data = fetcher.fetch(commodities, days, date)
        raw_indexes_data = fetcher.fetch(indexes, days, date)
        raw_stocks_data = fetcher.fetch(stocks, days, date)

        logger.info('Processing raw data')
        api_fields = historical_config[globals.FIELD_CFG_API]
        non_api_fields = historical_config[globals.FIELD_CFG_NON_API]
        commodities_mapping = make_mapping(commodities)
        indexes_mapping = make_mapping(indexes)
        stocks_mapping = make_mapping(stocks)

        logger.debug('Processing commodities')
        commodities_data = data_handler.process_raw_data(raw_commodities_data,
                                                         api_fields,
                                                         non_api_fields,
                                                         commodities_mapping,
                                                         HISTORICAL)

        logger.debug('Processing indexes')
        indexes_data = data_handler.process_raw_data(raw_indexes_data,
                                                     api_fields,
                                                     non_api_fields,
                                                     indexes_mapping,
                                                     HISTORICAL)

        logger.debug('Processing stocks')
        stocks_data = data_handler.process_raw_data(raw_stocks_data,
                                                    api_fields,
                                                    non_api_fields,
                                                    stocks_mapping,
                                                    HISTORICAL)

        logger.debug(f'Writing processed data to files: {globals.FN_OUT_HISTORICAL_COMMODITY} '
                     f'{globals.FN_OUT_HISTORICAL_INDEX} {globals.FN_OUT_HISTORICAL_STOCKS}')
        file_handler.write_json(commodities_data,
                                globals.FN_OUT_HISTORICAL_COMMODITY)
        file_handler.write_json(indexes_data,
                                globals.FN_OUT_HISTORICAL_INDEX)
        file_handler.write_json(stocks_data,
                                globals.FN_OUT_HISTORICAL_STOCKS)
        logger.success('Historical collection complete')
    except Exception as e:
        logger.error(e)
        raise


if __name__ == "__main__":
    main()

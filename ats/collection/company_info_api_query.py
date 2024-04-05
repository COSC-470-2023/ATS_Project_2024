import datetime
import os

from ats import globals
from ats.logger import Logger
from ats.util import api_handler, data_handler, file_handler

logger = Logger.instance()

# Constants
COMPANY_DATE = '_company_date'
STOCKS = 'stocks'
SYMBOL = 'symbol'


@api_handler.query_builder
def build_queries(query_manager: api_handler.QueryManager,
                  config_data: list[dict]):
    # TODO: write docstring
    for entry in config_data:
        query_manager.add(entry[SYMBOL])


def make_mapping(date: datetime.date) -> data_handler.Mapping:
    # TODO: write docstring

    @data_handler.mapping_callback
    def company_date(kwargs: data_handler.Kwargs) -> str:
        return str(date)

    mapping = data_handler.Mapping()
    mapping.add(COMPANY_DATE, company_date)
    return mapping


def main():
    try:
        logger.info('Starting companies collection')
        config = file_handler.read_yaml(globals.FN_CFG_COMPANIES)

        logger.info('Fetching raw data from API')
        endpoint = config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        stocks = config[STOCKS]
        fetcher = api_handler.Fetcher(endpoint, api_key, build_queries)
        raw_data = fetcher.fetch(stocks)

        logger.info('Processing raw data')
        api_fields = config[globals.FIELD_CFG_API]
        non_api_fields = config[globals.FIELD_CFG_NON_API]
        date = datetime.datetime.now()
        mapping = make_mapping(date)
        data = data_handler.process_raw_data(raw_data,
                                             api_fields,
                                             non_api_fields,
                                             mapping)

        logger.inf('Writing processed data to output')
        file_handler.write_json(data, globals.FN_OUT_COMPANIES)
        logger.info('Companies collection complete')
    except Exception as e:
        logger.error(e)
        raise


if __name__ == "__main__":
    main()

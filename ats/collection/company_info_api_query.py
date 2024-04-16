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
    """
    Parse through company configuration file, make queries for each entry.
    :param query_manager: api_handler utility class. Builds API query URI.
    :param config_data: Configuration file input.
    """
    for entry in config_data:
        query_manager.add(entry[SYMBOL])


def make_mapping(date: datetime.date) -> data_handler.Mapping:
    """
    :param date: current date
    :return: mapping of date to company_date
    """
    @data_handler.mapping_callback
    def company_date(kwargs: data_handler.Kwargs) -> str:
        return str(date)

    mapping = data_handler.Mapping()
    mapping.add(COMPANY_DATE, company_date)
    return mapping


def main():
    """
    Executes data collection for company statement data, processes the raw data,
    and stores the results in JSON format. This function sets up logging, reads configuration,
    fetches and processes data based on parameters in company_info_config.yaml.
    """
    try:
        logger.info('Starting companies collection')
        config = file_handler.read_yaml(globals.FN_CFG_COMPANIES)

        logger.debug('Fetching raw data from API')
        endpoint = config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        stocks = config[STOCKS]
        fetcher = api_handler.Fetcher(endpoint, api_key, build_queries)
        raw_data = fetcher.fetch(stocks)

        logger.debug('Processing raw data')
        api_fields = config[globals.FIELD_CFG_API]
        non_api_fields = config[globals.FIELD_CFG_NON_API]
        date = datetime.datetime.now()
        mapping = make_mapping(date)
        data = data_handler.process_raw_data(raw_data,
                                             api_fields,
                                             non_api_fields,
                                             mapping)

        logger.debug(f'Writing processed data to output file {globals.FN_OUT_COMPANIES}')
        file_handler.write_json(data, globals.FN_OUT_COMPANIES)
        logger.success('Companies collection complete')
    except Exception as e:
        logger.error(f"Error occurred when gathering company information: {e}")
        raise


if __name__ == "__main__":
    main()

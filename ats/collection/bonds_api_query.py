import datetime
import os

from ats import globals
from ats.logger import Logger
from ats.util import api_handler, data_handler, file_handler

logger = Logger.instance()

# Constants
BOND_NAME = '_bond_name'
CHUNK = 90
TREASURY = 'treasury'


@api_handler.query_builder
def build_queries(query_manager: api_handler.QueryManager,
                  days: int,
                  date: datetime.date):
    # TODO: write docstring
    chunks = range(days // CHUNK)  # 90-day chunks + remaining chunk
    remainder = days % CHUNK  # Days in remaining chunk
    end_date = date

    for _ in chunks:
        start_date = end_date - datetime.timedelta(days=CHUNK)
        query_manager.add(str(start_date), str(end_date))
        end_date = start_date - datetime.timedelta(days=1)
    if remainder > 0:
        start_date = end_date - datetime.timedelta(days=remainder)
        query_manager.add(str(start_date), str(end_date))


def make_mapping(treasury: str) -> data_handler.Mapping:
    # TODO: write docstring
    @data_handler.mapping_callback
    def bond_name(kwargs: data_handler.Kwargs) -> str:
        return treasury

    mapping = data_handler.Mapping()
    mapping.add(BOND_NAME, bond_name)
    return mapping


def main():
    try:
        logger.info('Starting bonds collection')
        config = file_handler.read_yaml(globals.FN_CFG_BONDS)

        logger.info('Fetching raw data from API')
        endpoint = config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        days = os.getenv(globals.ENV_DAYS_QUERIED)
        days = int(days)
        date = datetime.date.today()
        fetcher = api_handler.Fetcher(endpoint, api_key, build_queries)
        raw_data = fetcher.fetch(days, date)

        logger.info('Processing raw data')
        api_fields = config[globals.FIELD_CFG_API]
        # TODO: support for multiple treasuries
        non_api_fields = config[globals.FIELD_CFG_NON_API]
        treasury = config[TREASURY]
        mapping = make_mapping(treasury)
        data = data_handler.process_raw_data(raw_data,
                                             api_fields,
                                             non_api_fields,
                                             mapping)

        logger.info('Writing processed data to output')
        file_handler.write_json(data, globals.FN_OUT_BONDS)
        logger.info('Bonds collection complete')
    except Exception as e:
        logger.error(e)
        raise


if __name__ == "__main__":
    main()

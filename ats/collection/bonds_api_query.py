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
    """
    Takes the inputted number of days from the ATS_DAYS_QUERIED environment variable,
    and builds an api query using date windows. Date windows are segmented by
    90-day intervals, which is the maximum range for FMP bonds query.
    :param query_manager: class used to build the api url and regex
    :param days: total number of days being queried
    :param date: current date
    """
    logger.debug("Creating Bond date windows.")
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
    logger.debug("Bond date windows creation completed.")


def make_mapping(treasury: str) -> data_handler.Mapping:
    """
    Maps the specified treasury to the dataset.
    :param treasury: Financial treasury for which bonds to gather from
    :return mapping: Field from the configuration to map this value to in output
    """
    @data_handler.mapping_callback
    def bond_name(kwargs: data_handler.Kwargs) -> str:
        return treasury

    mapping = data_handler.Mapping()
    mapping.add(BOND_NAME, bond_name)
    return mapping


def main():
    """
    Executes data collection for bond data, processes the raw data,
    and stores the results in JSON format. This function sets up logging, reads configuration,
    fetches and processes data based on parameters in bonds_config.yaml.
    """
    try:
        logger.info('Starting bonds collection')
        config = file_handler.read_yaml(globals.FN_CFG_BONDS)

        logger.debug('Fetching raw data from API')
        endpoint = config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        days = os.getenv(globals.ENV_DAYS_QUERIED)
        days = int(days)
        date = datetime.date.today()
        fetcher = api_handler.Fetcher(endpoint, api_key, build_queries)
        logger.debug(f'Creating Bond date windows for {days} days.')
        raw_data = fetcher.fetch(days, date)

        logger.debug('Processing raw data')
        api_fields = config[globals.FIELD_CFG_API]

        non_api_fields = config[globals.FIELD_CFG_NON_API]
        treasury = config[TREASURY]
        mapping = make_mapping(treasury)
        data = data_handler.process_raw_data(raw_data,
                                             api_fields,
                                             non_api_fields,
                                             mapping)

        logger.debug(f'Writing processed data to output file {globals.FN_OUT_BONDS}')
        file_handler.write_json(data, globals.FN_OUT_BONDS)
        logger.success('Bonds collection complete')
    except Exception as e:
        logger.error(f"Error occurred when gathering bonds data: {e}")
        raise


if __name__ == "__main__":
    main()

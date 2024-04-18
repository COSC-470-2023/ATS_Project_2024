import datetime
import os

from ats import globals
from ats.logger import Logger
from ats.util import api_handler, data_handler, file_handler

logger = Logger.instance()


def prune_old_entries(raw_data: list[dict],
                      days: int,
                      date: datetime.datetime) -> list[dict]:
    """
    Filters out entries from raw data that are older than the specified number of days from the given date.
    :param raw_data: A list of dictionaries, each representing an entry with a date key.
    :param days: The number of days from the current date to filter out. (Default: 1095)
    :param date: The current date.
    :return: A list of dictionaries containing only the entries within the specified date range.
    """
    pruned_data = []
    constraint_date = date - datetime.timedelta(days=days)
    for entry in raw_data:
        entry_date = datetime.datetime.strptime(entry['date'], '%Y-%m-%d')
        if entry_date >= constraint_date:
            pruned_data.append(entry)
    return pruned_data


def main():
    """
    Executes collection for companies which have changed their symbol, processes the raw data,
    and stores the results in JSON format. This function sets up logging, reads configuration,
    fetches and processes data based on parameters in symbol_change_config.yaml.
    """
    try:
        logger.info('Starting symbol change collection')
        config = file_handler.read_yaml(globals.FN_CFG_SYMBOL_CHANGE)

        logger.debug('Fetching raw data from API')
        endpoint = config[globals.FIELD_CFG_URL]
        api_key = os.getenv(globals.ENV_API_KEY)
        fetcher = api_handler.Fetcher(endpoint, api_key)
        raw_data = fetcher.fetch()

        days = os.getenv(globals.ENV_DAYS_QUERIED)
        days = int(days)
        date = datetime.datetime.today()
        pruned_data = prune_old_entries(raw_data, days, date)

        logger.debug('Processing raw data')
        api_fields = config[globals.FIELD_CFG_API]
        data = data_handler.process_raw_data(pruned_data,
                                             api_fields)

        logger.debug(f'Writing processed data to output file: {globals.FN_OUT_SYMBOL_CHANGE}')
        file_handler.write_json(data, globals.FN_OUT_SYMBOL_CHANGE)
        logger.success('Symbol change collection complete')
    except Exception as e:
        logger.error(f"Error occurred when gathering symbol changes: {e}")
        raise


if __name__ == "__main__":
    main()

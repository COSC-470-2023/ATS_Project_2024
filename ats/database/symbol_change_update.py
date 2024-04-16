import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import file_handler, db_handler
from ats.util.db_handler import ConnectionManager

connection_manager = db_handler.ConnectionManager.instance()
logger = Logger.instance()


def prune_old_data(connection, data):
    """

    :param connection: Connection to the database
    :param data: JSON output received from API
    :return: Pruned JSON output to ignore symbols that aren't in use
    """
    pruned_data = []
    query = sqlalchemy.text("SELECT symbol FROM companies")
    result = connection.execute(query)
    symbols = result.all()
    for symbol in symbols:
        for entry in data:
            if symbol == entry['_change_oldSymbol']:
                pruned_data.append(entry)
    return pruned_data


def update_symbol(connection, symbol):
    """
    Connects to the database and updates symbol accordingly
    :param connection: Connection to the database
    :param symbol: A symbol retrieved from JSON output
    :return:
    """
    logger.debug(f"Updating symbol: {symbol}")
    try:
        # Variable Declarations
        name = symbol["_change_newName"]
        old_symbol = symbol["_change_oldSymbol"]
        new_symbol = symbol["_change_newSymbol"]

        # SQL query
        company_update = sqlalchemy.text("UPDATE companies SET companyName = :_change_newName, symbol = :_change_newSymbol WHERE symbol = :_change_oldSymbol")

        connection.execute(company_update, parameters=symbol)
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when updating companies table. Exception: {e}")


def main():
    try:
        # Create connection with context manager, connection closed on commit
        with connection_manager.connect() as connection:
            data = file_handler.read_json(globals.FN_OUT_SYMBOL_CHANGE)
            pruned_data = prune_old_data(connection, data)
            for entry in pruned_data:
                update_symbol(connection, entry)
            connection.commit()
    except Exception as e:
        logger.critical(f"Error when updating remote database. Exception: {e}")

    logger.success("symbol_change_update.py ran successfully.")


if __name__ == "__main__":
    main()

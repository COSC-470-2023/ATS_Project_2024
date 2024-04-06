import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import file_handler, db_handler
from ats.util.db_handler import ConnectionManager

connection_manager = db_handler.ConnectionManager.instance()
logger = Logger.instance()


def update_symbol(connection, symbol):
    try:
        # Variable Declarations
        name = symbol["_change_newName"]
        old_symbol = symbol["_change_oldSymbol"]
        new_symbol = symbol["_change_newSymbol"]

        #  SQL query
        company_update = sqlalchemy.text("UPDATE companies SET companyName = :_change_newName, symbol = :_change_newSymbol WHERE symbol = :_change_oldSymbol")

        connection.execute(company_update, parameters=symbol)
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error in updating database: {e}")


def main():
    try:
        with connection_manager.connect() as connection:
            data = file_handler.read_json(globals.FN_OUT_SYMBOL_CHANGE)
            for entry in data:
                update_symbol(connection, entry)
            connection.commit()
    except Exception as e:
        logger.critical(f"Error when connecting to remote database: {e}")

    logger.success("symbol_change_update.py ran successfully.")


if __name__ == "__main__":
    main()

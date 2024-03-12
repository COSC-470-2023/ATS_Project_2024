import traceback

import sqlalchemy

from ats import loguru_init
from ats.globals import DIR_OUTPUT, OUTPUT_SYMBOL_CHANGE
from ats.util import connect, json_handler

logger = loguru_init.initialize()


def update_symbol(connection, symbol):
    try:
        # Variable Declarations
        name = symbol["_change_newName"]
        old_symbol = symbol["_change_oldSymbol"]
        new_symbol = symbol["_change_newSymbol"]

        #  SQL query
        company_update = sqlalchemy.text(f"UPDATE companies SET companyName = '{name}', symbol = '{new_symbol}' WHERE symbol = '{old_symbol}'")

        connection.execute(company_update)
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error in updating database: {e}")


def main():
    try:
        # Establish a connection to server
        with connect.connect() as conn:
            symbol_change = json_handler.load_output(DIR_OUTPUT + OUTPUT_SYMBOL_CHANGE)
            for symbol in symbol_change:
                update_symbol(conn, symbol)
            conn.commit()
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when connecting to remote database: {e}")

    logger.success("symbol_change_update.py ran successfully.")


if __name__ == "__main__":
    main()

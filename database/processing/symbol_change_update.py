import json
import traceback
from sqlalchemy import text
import connect

from data_collection.collection.json_handler import json_load_output
from dev_tools import loguru_init

# Globals
OUTPUT_FILE_PATH = "./SMF_Project_2023/data_collection/output/symbol_change_list.json"

logger = loguru_init.initialize()


def update_symbol(connection, symbol):
    logger.info(f"Updating symbol: {symbol}")
    try:
        # Variable Declarations
        name = symbol["_change_newName"]
        old_symbol = symbol["_change_oldSymbol"]
        new_symbol = symbol["_change_newSymbol"]
        logger.debug(f"{old_symbol} updated to {new_symbol}")

        #  SQL query
        company_update = text(f"UPDATE companies SET companyName = '{name}', symbol = '{new_symbol}' WHERE symbol = '{old_symbol}'")

        connection.execute(company_update)
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error in updating database: {e}")


def main():
    # Load json data
    symbol_change = json_load_output(OUTPUT_FILE_PATH)
    try:
        # Establish a connection to server
        with connect.connect() as conn:
            for symbol in symbol_change:
                update_symbol(conn, symbol)
            conn.commit()
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when connecting to remote database: {e}")

    logger.success("symbol_change_update.py ran successfully.")


if __name__ == "__main__":
    main()

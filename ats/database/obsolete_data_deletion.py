import traceback

import sqlalchemy

from ats.logger import Logger
from ats.util import db_handler

logger = Logger.instance()
connection_manager = db_handler.ConnectionManager.instance()

# List of tables that need to have obsolete data deleted from
deletion_list = [
    'bond_values',
    'company_statements',
    'historical_commodity_values',
    'historical_index_values',
    'historical_stock_values',
    'realtime_commodity_values',
    'realtime_index_values',
    'realtime_stock_values'
]


def data_deletion(table, conn):
    """
    Deletes records from the database that are older than 3 years
    :param table: Name of database table, taken from list above
    :param conn: Connection to the database
    """
    logger.debug(f"Deleting records from: {table}")
    # Delete entries that is stored longer than 3 years
    conn.execute(sqlalchemy.text(f"DELETE FROM {table} WHERE date < DATE_SUB(CURDATE(), INTERVAL 3 YEAR)"))


def main():
    try:
        # Create with context manager
        with connection_manager.connect() as conn:
            logger.info("Executing obsolete data deletion")
            # Iterate through all the tables in the database and fetch the table name for delete operation
            for table in deletion_list:
                # Avoid delete data in the company_changelogs
                if table != 'company_changelogs':
                    data_deletion(table, conn)
                    conn.commit()
                    
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when deleting from remote database. Exception: {e}")
    logger.success("obsolete_data_deletion ran successfully.")


# Protected entrypoint
if __name__ == "__main__":
    main()

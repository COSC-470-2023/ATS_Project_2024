#### We are testing in the Yuan's local environment ##### 
import connect
import traceback
from sqlalchemy import text
from dev_tools import loguru_init

logger = loguru_init.initialize()

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


def dataDeletion(table, conn):
    logger.info("Executing obsolet data deletion")
    # Delete entries that is stored longer than 3 years
    conn.execute(text(f"DELETE FROM {table} WHERE date < DATE_SUB(CURDATE(), INTERVAL 3 YEAR)"))


def main():
    try:
        # create with context manager, conn is created only for this script, commit the conn will not affect others
        with connect.connect() as conn:
            # Iterate through all the tables in the database and fetch the table name for delete operation
            for table in deletion_list:
                # Avoid delete data in the company_changelogs
                if table != 'company_changelogs':
                    dataDeletion(table, conn)
                    conn.commit()
                    
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when connecting to remote database: {e}")
    logger.success("obsolete_data_deletion ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

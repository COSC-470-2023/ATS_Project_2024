import traceback

import sqlalchemy

from ats.util import connect

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
    # Delete entries that is stored longer than 3 years
    conn.execute(sqlalchemy.text(f"DELETE FROM {table} WHERE date < DATE_SUB(CURDATE(), INTERVAL 3 YEAR)"))


def main():
    try:
        # create with context manager, conn is created only for this script, commit the conn will not affect others
        with connect.connect() as conn:
            # Iterate through all the tables in the database and fetch the table name for delete operation
            for table in deletion_list:
                # Avoid delete data in the company_changelogs
                if table != 'company_changelogs':
                    data_deletion(table, conn)
                    conn.commit()
                    
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")


# protected entrypoint
if __name__ == "__main__":
    main()

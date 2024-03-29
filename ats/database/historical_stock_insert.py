import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import db_handler, file_handler

logger = Logger.instance()


def check_keys(entry):
    logger.debug("Historical stock insertion: Checking keys")
    # keys expected to be committed
    keys = [    
        '_historical_date',
        '_historical_open',
        '_historical_high',
        '_historical_low',
        '_historical_close',
        '_historical_adjClose',
        '_historical_volume',
        '_historical_unadjustedVolume',
        '_historical_change',
        '_historical_changePercent',
        '_historical_vwap',
        '_historical_changeOverTime',
    ]
    # get key value, assign value to key. if key doesn't exist, assign value of None
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, index_id):
    logger.info(f"Inserting record for historical stock ID: {index_id}")
    # get key value, assign value to key. if key doesn't exist, assign value of None
    row = check_keys(entry)
    # append generated id
    row["company_id"] = index_id
    # parameterized query
    query = sqlalchemy.text("INSERT INTO `historical_stock_values` VALUES (:company_id, :_historical_date, :_historical_open, :_historical_high, :_historical_low, :_historical_close, :_historical_adjClose, :_historical_volume, :_historical_unadjustedVolume, :_historical_change, :_historical_changePercent, :_historical_vwap, :_historical_changeOverTime)")
    # Execute row insertion
    connection.execute(query, row)


# Used to get id associated with an index        
def get_company_id(entry, connection):
    logger.debug("Assigning historical stock ID")
    company_id = None

    try:
        # set query parameters
        params = {"symbol": entry["_historical_symbol"], "name": entry["_historical_name"], "isListed": 1}

        id_query = sqlalchemy.text("SELECT id FROM `companies` WHERE symbol = :symbol")
        # check if company exists in companies table
        result = connection.execute(id_query, parameters=params)

        row = result.one_or_none()

        if row is None:
            logger.debug("ID not found, creating new row")
            # if index doesn't exist, create new row in indexes table - trigger generates new ID
            connection.execute(sqlalchemy.text("INSERT INTO `companies` (`companyName`, `symbol`, `isListed`) VALUES (:name, :symbol, :isListed)"), parameters=params)

            # get id generated from trigger
            result = connection.execute(id_query, parameters=params)
            company_id = result.one()[0]
        else:
            # if the index exists, fetch the existing ID
            company_id = row[0]
    except Exception as e:
        logger.error(f"Error occurred when assigning ID: {e}")

    return company_id


def main():
    # Load json data
    historical_data = file_handler.read_json(globals.FN_OUT_HISTORICAL_STOCKS)
    try:
        # create with context manager
        with db_handler.connect() as conn:
            # begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in historical_data:
                    if isinstance(entry, dict):
                        company_id = get_company_id(entry, conn)
                        try:
                            # Execute row insertion
                            execute_insert(conn, entry, company_id)
                        except sqlalchemy.exc.SQLAlchemyError as e:
                            # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                            logger.error(f"Error: {e}")
                            continue
                    else:
                        # entry is not a dictionary, skip it
                        continue
           
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when connecting to remote database: {e}")

    logger.success("historical_stock_insert.py ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import db_handler, file_handler

logger = Logger.instance()
connection_manager = db_handler.ConnectionManager.instance()


def check_keys(entry):
    logger.debug("Realtime commodity insertion: Checking keys")
    # list of keys expected to be committed
    keys = [
        "_realtime_symbol",
        "_realtime_name",
        "_realtime_price",
        "_realtime_changePercent",
        "_realtime_change",
        "_realtime_dayLow",
        "_realtime_dayHigh",
        "_realtime_yearHigh",
        "_realtime_yearLow",
        "_realtime_mktCap",
        "_realtime_exchange",
        "_realtime_volume",
        "_realtime_volAvg",
        "_realtime_open",
        "_realtime_prevClose",
        "_realtime_date",
    ]

    # get key value, assign value to key. if key doesn't exist, assign value of None
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, commodity_id):
    logger.info(f"Inserting record for commodity ID: {commodity_id}")
    # check for any missing keys and assign values of None
    row = check_keys(entry)
    # append generated id
    row["commodity_id"] = commodity_id
    # parameterized query
    query = sqlalchemy.text(
            f"INSERT INTO `realtime_commodity_values` VALUES (:commodity_id, :_realtime_date, :_realtime_price, :_realtime_changePercent, :_realtime_change, :_realtime_dayLow, :_realtime_dayHigh, :_realtime_yearHigh, :_realtime_yearLow, :_realtime_mktCap, :_realtime_exchange, :_realtime_volume, :_realtime_volAvg, :_realtime_open, :_realtime_prevClose)"
        )
    # execute row insertion
    connection.execute(query, row)


def get_commodity_id(entry, connection):
    logger.debug("Assigning realtime commodity ID")
    commodity_id = None

    try:
        # set query parameters
        params = {"symbol": entry["_realtime_symbol"], "name": entry["_realtime_name"]}

        id_query = sqlalchemy.text("SELECT id FROM `commodities` WHERE symbol = :symbol")
        # check if index exists in indexes table
        result = connection.execute(id_query, parameters=params)

        row = result.one_or_none()

        if row is None:
            # if commodity doesn't exist, create new row in commodites table - trigger generates new ID
            connection.execute(sqlalchemy.text("INSERT INTO `commodities`(`commodityName`, `symbol`) VALUES (:_realtime_name, :_realtime_symbol)"), parameters=params)
            # get the generated ID
            result = connection.execute(id_query, parameters=params)
            commodity_id = result.one()[0]
        else:
            # if the commodities exists, fetch the existing ID
            commodity_id = row[0]
    except Exception as e:
        logger.error(f"Error occurred when assigning ID: {e}")

    return commodity_id


def main():
    # Load json data
    realtime_data = file_handler.read_json(globals.FN_OUT_REALTIME_COMMODITIES)

    try:
        # create connection with context manager, connection closed on exit
        with connection_manager.connect() as conn:
            # begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in realtime_data:
                    if isinstance(entry, dict):
                        commodity_id = get_commodity_id(entry, conn)
                        try:    
                            # process realtime data
                            execute_insert(conn, entry, commodity_id)
                        except sqlalchemy.exc.SQLAlchemyError as e:
                            # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                            print(f"Error: {e}")
                            continue
                    else:
                        # entry is not a dictionary, skip it
                        continue     
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when connecting to remote database: {e}")

    logger.success("realtime_commodity_insert ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

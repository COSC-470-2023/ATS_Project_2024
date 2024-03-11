import connect
import json
import traceback
from sqlalchemy import sql, text, SQLAlchemyError

from data_collection.collection.json_handler import json_load_output
from dev_tools import loguru_init

# Globals
OUTPUT_FILE_PATH = "./SMF_Project_2023/data_collection/output/realtime_index_output.json"

logger = loguru_init.initialize()


def check_keys(entry):
    logger.debug("Realtime index insertion: Checking keys")
    # keys expected to be committed
    keys = [
        "_realtime_date",
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
    ]
    # get key value, assign value to key. if key doesn't exist, assign value of None
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, index_id):
    logger.info(f"Inserting record for index ID: {index_id}")
    # check for any missing keys and assign values of None
    row = check_keys(entry)
    # append generated id
    row["index_id"] = index_id
    # parameterized query
    query = text(
            f"INSERT INTO `realtime_index_values` VALUES (:index_id, :_realtime_date, :_realtime_price, :_realtime_changePercent, :_realtime_change, :_realtime_dayLow, :_realtime_dayHigh, :_realtime_yearHigh, :_realtime_yearLow, :_realtime_mktCap, :_realtime_exchange, :_realtime_volume, :_realtime_volAvg, :_realtime_open, :_realtime_prevClose)"
        )
    # execute row insertion
    connection.execute(query, row)


def get_index_id(entry, connection):
    logger.debug("Assigning realtime index ID")

    try:
        # set query parameters
        params = {"symbol": entry["_realtime_symbol"], "name": entry["_realtime_name"]}

        id_query = text("SELECT id FROM `indexes` WHERE symbol = :symbol")
        # check if index exists in indexes table
        result = connection.execute(id_query, parameters=params)

        row = result.one_or_none()

        if row is None:
            # if index doesn't exist, create new row in indexes table - trigger generates new ID
            connection.execute(text("INSERT INTO `indexes` (`indexName`, `symbol`) VALUES (:name, :symbol)") ,parameters=params)

            # get the generated ID
            result = connection.execute(id_query, parameters=params)
            index_id = result.one()[0]
        else:
            # if the index exists, fetch the existing ID
            index_id = row[0]
    except Exception as e:
        logger.error(f"Error occurred when assigning ID: {e}")
    return index_id


def main():
    # Load json data
    realtime_data = json_load_output(OUTPUT_FILE_PATH)
    try:
        # create connection with context manager, connection closed on exit
        with connect.connect() as conn:
            # begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in realtime_data:
                    if isinstance(entry, dict):
                        index_id = get_index_id(entry, conn)
                        try:    
                            # process realtime data
                            execute_insert(conn, entry, index_id)
                        except SQLAlchemyError as e:
                            # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                            logger.error(f"Error: {e}")
                            continue
                    else:
                        # entry is not a dictionary, skip it
                        continue

    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when connecting to remote database: {e}")

    logger.success("realtime_index_insert.py ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

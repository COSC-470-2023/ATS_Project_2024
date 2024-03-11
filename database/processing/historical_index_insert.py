import connect
import json
import traceback
from sqlalchemy import text, SQLAlchemyError

from data_collection.collection.json_handler import json_load_output
from dev_tools import loguru_init

# Globals
OUTPUT_FILE_PATH = "./SMF_Project_2023/data_collection/output/historical_index_output.json"

logger = loguru_init.initialize()


def check_keys(entry):
    logger.debug("Historical index insertion: Checking keys")
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
    logger.info(f"Inserting record for index ID: {index_id}")
    # get key value, assign value to key. if key doesn't exist, assign value of None
    row = check_keys(entry)
    # append generated id
    row["index_id"] = index_id
    # parameterized query
    query = text("INSERT INTO `historical_index_values` VALUES (:index_id, :_historical_date, :_historical_open, :_historical_high, :_historical_low, :_historical_close, :_historical_adjClose, :_historical_volume, :_historical_unadjustedVolume, :_historical_change, :_historical_changePercent, :_historical_vwap, :_historical_changeOverTime)")
    # Execute row insertion
    connection.execute(query, row)


# Used to get id associated with an index
def get_index_id(entry, connection):
    logger.debug("Assigning historical index ID")

    try:
        # set query parameters
        params = {"symbol": entry["_historical_symbol"], "name": entry["_historical_name"]}

        id_query = text("SELECT id FROM `indexes` WHERE symbol = :symbol")
        # check if index exists in indexes table
        result = connection.execute(text("SELECT id FROM `indexes` WHERE symbol = :symbol"), parameters=params)

        row = result.one_or_none()

        if row is None:
            # if index doesn't exist, create new row in indexes table - trigger generates new ID
            connection.execute(text("INSERT INTO `indexes` (`indexName`, `symbol`) VALUES (:name, :symbol)") ,parameters=params)

            # get id generated from trigger
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
    historical_data = json_load_output(OUTPUT_FILE_PATH)
    try:
        # create with context manager
        with connect.connect() as conn:
            # begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in historical_data:
                    if isinstance(entry, dict):
                        index_id = get_index_id(entry, conn)
                        try:
                            # Excute row insertion
                            execute_insert(conn,entry,index_id)
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

    logger.success("historical_index_insert.py ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

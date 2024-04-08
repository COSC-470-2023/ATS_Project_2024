import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import db_handler, file_handler

logger = Logger.instance()
connection_manager = db_handler.ConnectionManager.instance()


def check_keys(entry):
    logger.debug("Historical index insertion: Checking keys")
    # keys expected to be committed
    keys = [
        "_historical_date",
        "_historical_open",
        "_historical_high",
        "_historical_low",
        "_historical_close",
        "_historical_adjClose",
        "_historical_volume",
        "_historical_unadjustedVolume",
        "_historical_change",
        "_historical_changePercent",
        "_historical_vwap",
        "_historical_changeOverTime",
    ]
    # get key value, assign value to key. if key doesn't exist, assign value of None
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, index_id):
    logger.info(f"Inserting record for index ID: {index_id}")
    # get key value, assign value to key. if key doesn't exist, assign value of None
    row = check_keys(entry)
    # append generated id
    row["index_id"] = index_id

    # check if record exists already
    check_query = sqlalchemy.text(
        "SELECT COUNT(*) FROM `historical_index_values` WHERE index_id = :index_id AND date = :_historical_date"
    )
    result = connection.execute(check_query, row).scalar()

    if result > 0:
        logger.warning(
            f"Record for company with ID: {index_id} already exists. Skipping to next record."
        )
        return
    try:
        # parameterized query
        query = sqlalchemy.text(
            "INSERT INTO `historical_index_values` VALUES (:index_id, :_historical_date, :_historical_open, :_historical_high, :_historical_low, :_historical_close, :_historical_adjClose, :_historical_volume, :_historical_unadjustedVolume, :_historical_change, :_historical_changePercent, :_historical_vwap, :_historical_changeOverTime)"
        )
        # Execute row insertion
        connection.execute(query, row)
    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(
            f"Failed to insert record for index {index_id} with date {entry['_historical_date']}: {e}"
        )


# Used to get id associated with an index
def get_index_id(entry, connection):
    logger.debug("Assigning historical index ID")
    index_id = None

    try:
        # set query parameters
        params = {
            "_historical_symbol": entry["_historical_symbol"],
            "_historical_name": entry["_historical_name"],
        }

        id_query = sqlalchemy.text(
            "SELECT id FROM `indexes` WHERE symbol = :_historical_symbol"
        )
        # check if index exists in indexes table
        result = connection.execute(id_query, parameters=params)

        row = result.one_or_none()

        if row is None:
            # if index doesn't exist, create new row in indexes table - trigger generates new ID
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO `indexes` (`indexName`, `symbol`) VALUES (:_historical_name, :_historical_symbol)"
                ),
                parameters=params,
            )

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
    historical_data = file_handler.read_json(globals.FN_OUT_HISTORICAL_INDEX)
    try:
        # create with context manager
        with connection_manager.connect() as conn:
            # begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in historical_data:
                    if isinstance(entry, dict):
                        index_id = get_index_id(entry, conn)
                        try:
                            # Execute row insertion
                            execute_insert(conn, entry, index_id)
                        except sqlalchemy.exc.SQLAlchemyError as e:
                            # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                            logger.error(f"SQLAlchemy Exception: {e}")
                            continue
                    else:
                        # entry is not a dictionary, skip it
                        continue

    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when updating remote database. Exception: {e}")

    logger.success("historical_index_insert.py ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

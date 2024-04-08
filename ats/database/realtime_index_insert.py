import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import db_handler, file_handler

logger = Logger.instance()
connection_manager = db_handler.ConnectionManager.instance()


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

    # check if record exists already
    check_query = sqlalchemy.text(
        "SELECT COUNT(*) FROM `realtime_index_values` WHERE index_id = :index_id AND date = :_realtime_date"
    )
    result = connection.execute(check_query, row).scalar()
    if result > 0:
        logger.warning(
            f"Record for index with ID: {index_id} and date: {row['_realtime_date']} already exists. Skipping to next record."
        )
        return
    try:
        # parameterized query
        query = sqlalchemy.text(
            f"INSERT INTO `realtime_index_values` VALUES (:index_id, :_realtime_date, :_realtime_price, :_realtime_changePercent, :_realtime_change, :_realtime_dayLow, :_realtime_dayHigh, :_realtime_yearHigh, :_realtime_yearLow, :_realtime_mktCap, :_realtime_exchange, :_realtime_volume, :_realtime_volAvg, :_realtime_open, :_realtime_prevClose)"
        )
        # execute row insertion
        connection.execute(query, row)
    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(
            f"Failed to insert record for index {index_id} with date {entry['_realtime_date']}: {e}"
        )


def get_index_id(entry, connection):
    logger.debug("Assigning realtime index ID")
    index_id = None

    try:
        # set query parameters
        params = {"symbol": entry["_realtime_symbol"], "name": entry["_realtime_name"]}

        id_query = sqlalchemy.text("SELECT id FROM `indexes` WHERE symbol = :symbol")
        # check if index exists in indexes table
        result = connection.execute(id_query, parameters=params)

        row = result.one_or_none()

        if row is None:
            # if index doesn't exist, create new row in indexes table - trigger generates new ID
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO `indexes` (`indexName`, `symbol`) VALUES (:name, :symbol)"
                ),
                parameters=params,
            )

            # get the generated ID
            result = connection.execute(id_query, parameters=params)
            index_id = result.one()[0]
        else:
            # if the index exists, fetch the existing ID
            index_id = row[0]
    except Exception as e:
        logger.error(
            f"Error occurred when assigning ID for entry: {entry['_realtime_symbol']}, {entry['_realtime_name']}: {e}"
        )
    return index_id


def main():
    # Load json data
    realtime_data = file_handler.read_json(globals.FN_OUT_REALTIME_INDEX)

    try:
        # create connection with context manager, connection closed on exit
        with connection_manager.connect() as conn:
            # begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in realtime_data:
                    if isinstance(entry, dict):
                        index_id = get_index_id(entry, conn)
                        try:
                            # process realtime data
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

    logger.success("realtime_index_insert.py ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

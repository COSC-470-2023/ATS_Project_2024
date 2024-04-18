import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import db_handler, file_handler

logger = Logger.instance()
connection_manager = db_handler.ConnectionManager.instance()


def check_keys(entry):
    """
    Checks keys, assigns value to None if key is not found/has no value
    :param entry: A key/value pair from the JSON output
    :return: Key/value pairs, if key/value is not detected(i.e. not provided by API), key will be assigned value None
    """
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
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, index_id):
    """
    Connects to database and executes MySQL insertion.
    :param connection: Connection to the database
    :param entry: A key/value pair
    :param index_id: A generated primary key for database
    """
    logger.debug(f"Inserting record for index ID: {index_id}")
    row = check_keys(entry)
    # Append generated id
    row["index_id"] = index_id

    # Check if record exists already
    check_query = sqlalchemy.text(
        "SELECT COUNT(*) FROM `realtime_index_values` WHERE index_id = :index_id AND date = :_realtime_date"
    )
    result = connection.execute(check_query, row).scalar()

    # If record exists, provide warning message and ignore insertion
    if result > 0:
        logger.warning(
            f"Record for index with ID: {index_id} and date: {row['_realtime_date']} already exists. Skipping to next record."
        )
        return
    try:
        # Parameterized query
        query = sqlalchemy.text(
            f"INSERT INTO `realtime_index_values` VALUES (:index_id, :_realtime_date, :_realtime_price, :_realtime_changePercent, :_realtime_change, :_realtime_dayLow, :_realtime_dayHigh, :_realtime_yearHigh, :_realtime_yearLow, :_realtime_mktCap, :_realtime_exchange, :_realtime_volume, :_realtime_volAvg, :_realtime_open, :_realtime_prevClose)"
        )
        # Execute row insertion
        connection.execute(query, row)
    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(
            f"Failed to insert record for index {index_id} with date {entry['_realtime_date']}: {e}"
        )


def get_index_id(entry, connection):
    """
    Queries the database to see if index already has an ID, if no ID is found for said index,
    the trigger will generate one. If an ID is found, return said ID.
    :param entry: A key/value pair
    :param connection: Connection to the database
    """
    logger.debug("Assigning realtime index ID")
    index_id = None

    try:
        # Set query parameters
        params = {"symbol": entry["_realtime_symbol"], "name": entry["_realtime_name"]}

        id_query = sqlalchemy.text("SELECT id FROM `indexes` WHERE symbol = :symbol")
        # Check if index exists in indexes table
        result = connection.execute(id_query, parameters=params)

        row = result.one_or_none()

        if row is None:
            # If index doesn't exist, create new row in indexes table - trigger generates new ID
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO `indexes` (`indexName`, `symbol`) VALUES (:name, :symbol)"
                ),
                parameters=params,
            )

            # Get the generated ID
            result = connection.execute(id_query, parameters=params)
            index_id = result.one()[0]
        else:
            # If the index exists, fetch the existing ID
            index_id = row[0]
    except Exception as e:
        logger.error(
            f"Error occurred when assigning ID for entry: {entry['_realtime_symbol']}, {entry['_realtime_name']}: {e}"
        )
    return index_id


def main():
    # Loads the realtime index output file, creates a database connection and executes insertion
    realtime_data = file_handler.read_json(globals.FN_OUT_REALTIME_INDEX)

    try:
        # Create connection with context manager, connection closed on exit
        with connection_manager.connect() as conn:
            # Begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in realtime_data:
                    if isinstance(entry, dict):
                        index_id = get_index_id(entry, conn)
                        try:
                            # Process realtime data
                            execute_insert(conn, entry, index_id)
                        except sqlalchemy.exc.SQLAlchemyError as e:
                            # Log sqlalchemy error, then continue to prevent silent rollbacks
                            logger.error(f"SQLAlchemy Exception: {e}")
                            continue
                    else:
                        # Entry is not a dictionary, skip it
                        continue

    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when updating remote database. Exception: {e}")

    logger.success("realtime_index_insert.py ran successfully.")


# Protected entrypoint
if __name__ == "__main__":
    main()

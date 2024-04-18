import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import db_handler, file_handler

logger = Logger.instance()
connection_manager = db_handler.ConnectionManager.instance()


def check_keys(entry):
    logger.debug("Realtime commodity insertion: Checking keys")
    # List of expected keys
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

    # Get key value, assign value to key. if key doesn't exist, assign value of None
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, commodity_id):
    """
    Connects to database and executes MySQL insertion.
    :param connection: Connection to the database
    :param entry: A key/value pair
    :param commodity_id: A generated primary key for database
    """
    logger.debug(f"Inserting record for commodity ID: {commodity_id}")
    # Check for any missing keys and assign values of None
    row = check_keys(entry)
    # Append generated id
    row["commodity_id"] = commodity_id
    # check if record exists already
    check_query = sqlalchemy.text(
        "SELECT COUNT(*) FROM `realtime_commodity_values` WHERE commodity_id = :commodity_id AND date = :_realtime_date"
    )
    result = connection.execute(check_query, row).scalar()
    if result > 0:
        logger.warning(
            f"Record for commodity with ID: {commodity_id} and date: {row['_realtime_date']} already exists. Skipping to next record."
        )
        return
    try:
        # Parameterized query
        query = sqlalchemy.text(
            f"INSERT INTO `realtime_commodity_values` VALUES (:commodity_id, :_realtime_date, :_realtime_price, :_realtime_changePercent, :_realtime_change, :_realtime_dayLow, :_realtime_dayHigh, :_realtime_yearHigh, :_realtime_yearLow, :_realtime_mktCap, :_realtime_exchange, :_realtime_volume, :_realtime_volAvg, :_realtime_open, :_realtime_prevClose)"
        )
        # Execute row insertion
        connection.execute(query, row)
    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(
            f"Failed to insert record for commodity {commodity_id} with date {entry['_realtime_date']}: {e}"
        )


def get_commodity_id(entry, connection):
    """
    Queries the database to see if commodity already has an ID, if no ID is found for said commodity,
    the trigger will generate one. If an ID is found, return said ID.
    :param entry: A key/value pair
    :param connection: Connection to the database
    """
    logger.debug("Assigning realtime commodity ID")
    commodity_id = None

    try:
        # Set query parameters
        params = {"symbol": entry["_realtime_symbol"], "name": entry["_realtime_name"]}

        id_query = sqlalchemy.text(
            "SELECT id FROM `commodities` WHERE symbol = :symbol"
        )
        # Check if commodity exists in commodities table
        result = connection.execute(id_query, parameters=params)

        row = result.one_or_none()

        if row is None:
            # If commodity doesn't exist, create new row in commodites table - trigger generates new ID
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO `commodities`(`commodityName`, `symbol`) VALUES (:_realtime_name, :_realtime_symbol)"
                ),
                parameters=params,
            )
            # Get the generated ID
            result = connection.execute(id_query, parameters=params)
            commodity_id = result.one()[0]
        else:
            # If the commodities exist, fetch the existing ID
            commodity_id = row[0]
    except Exception as e:
        logger.error(f"Error occurred when assigning ID: {e}")

    return commodity_id


def main():
    # Loads the realtime commodity output file, creates a database connection and executes insertion
    realtime_data = file_handler.read_json(globals.FN_OUT_REALTIME_COMMODITIES)

    try:
        # Create connection with context manager, connection closed on exit
        with connection_manager.connect() as conn:
            # Begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in realtime_data:
                    if isinstance(entry, dict):
                        commodity_id = get_commodity_id(entry, conn)
                        try:
                            # Process realtime data
                            execute_insert(conn, entry, commodity_id)
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

    logger.success("realtime_commodity_insert ran successfully.")


# Protected entrypoint
if __name__ == "__main__":
    main()

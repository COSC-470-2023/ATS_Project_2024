import datetime
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
    logger.debug("Realtime stock insertion: Checking keys")
    # List of expected keys
    keys = [
        "_realtime_date",
        "_realtime_price",
        "_realtime_changePercent",
        "_realtime_change",
        "_realtime_dayHigh",
        "_realtime_dayLow",
        "_realtime_yearHigh",
        "_realtime_yearLow",
        "_realtime_mktCap",
        "_realtime_exchange",
        "_realtime_open",
        "_realtime_prevClose",
        "_realtime_volume",
        "_realtime_volAvg",
        "_realtime_eps",
        "_realtime_pe",
        "_realtime_earningsAnnouncement",
        "_realtime_sharesOutstanding",
    ]
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, company_id):
    """
    Connects to database and executes MySQL insertion.
    :param connection: Connection to the database
    :param entry: A key/value pair
    :param company_id: A generated primary key for database
    """
    logger.debug(f"Inserting record for stock ID: {company_id}")
    row = check_keys(entry)

    # Check if earningsAnnouncement is not None, convert to a datetime object and format for mysql datetime
    # If it is None, assign None to earnings_announcement
    earnings_announcement = (
        datetime.datetime.strptime(
            row["_realtime_earningsAnnouncement"], "%Y-%m-%dT%H:%M:%S.%f%z"
        ).strftime("%Y-%m-%d %H:%M:%S")
        if row["_realtime_earningsAnnouncement"] is not None
        else None
    )

    # Append generated id and modify earnings announcement
    row["company_id"] = company_id
    row["_realtime_earningsAnnouncement"] = earnings_announcement
    # Check if record exists already
    check_query = sqlalchemy.text(
        "SELECT COUNT(*) FROM `realtime_stock_values` WHERE company_id = :company_id AND date = :_realtime_date"
    )
    result = connection.execute(check_query, row).scalar()

    # If record exists, provide warning message and ignore insertion
    if result > 0:
        logger.warning(
            f"Record for company with ID: {company_id} and date: {row['_realtime_date']} already exists. Skipping to next record."
        )
        return
    try:
        # Parameterized query
        query = sqlalchemy.text(
            "INSERT INTO `realtime_stock_values` VALUES (:company_id, :_realtime_date, :_realtime_price, :_realtime_changePercent, :_realtime_change, :_realtime_dayLow, :_realtime_dayHigh, :_realtime_yearHigh, :_realtime_yearLow, :_realtime_mktCap, :_realtime_exchange, :_realtime_volume, :_realtime_volAvg, :_realtime_open, :_realtime_prevClose, :_realtime_eps, :_realtime_pe, :_realtime_earningsAnnouncement, :_realtime_sharesOutstanding)"
        )
        # Execute row insertion
        connection.execute(query, row)
    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(
            f"Failed to insert record for company {company_id} with date {entry['_realtime_date']}: {e}"
        )


def get_company_id(entry, conn):
    """
    Queries the database to see if company already has an ID, if no ID is found for said company,
    the trigger will generate one. If an ID is found, return said ID.
    :param entry: A key/value pair
    :param conn: Connection to the database
    """
    logger.debug("Assigning realtime stock ID")
    company_id = None

    try:
        params = {
            "symbol": entry["_realtime_symbol"],
            "name": entry["_realtime_name"],
        }
        # check if company exists in companies table
        result = conn.execute(
            sqlalchemy.text("SELECT id FROM `companies` WHERE symbol = :symbol"),
            parameters=params,
        )
        row = result.one_or_none()

        if row is None:
            # if company doesn't exist, create new row in companies table - trigger generates new ID
            conn.execute(
                sqlalchemy.text(
                    "INSERT INTO `companies` (`companyName`, `symbol`) VALUES (:name, :symbol)"
                ),
                parameters=params,
            )

            # get the generated ID
            result = conn.execute(
                sqlalchemy.text("SELECT id FROM `companies` WHERE symbol = :symbol"),
                parameters=params,
            )
            company_id = result.one()[0]
        else:
            # if the company exists, fetch the existing ID
            company_id = row[0]
    except Exception as e:
        logger.error(f"Error occurred when assigning ID: {e}")

    return company_id


def main():
    # Loads the company output file, creates a database connection and executes insertion
    realtime_data = file_handler.read_json(globals.FN_OUT_REALTIME_STOCKS)

    try:
        # Create connection with context manager, connection closed on exit
        with connection_manager.connect() as conn:
            # Begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in realtime_data:
                    if isinstance(entry, dict):
                        company_id = get_company_id(entry, conn)
                        try:
                            # process realtime data
                            execute_insert(conn, entry, company_id)
                        except sqlalchemy.exc.SQLAlchemyError as e:
                            # Log sqlalchemy error, then continue to prevent silent rollbacks
                            logger.error(f"SQLAlchemy Exception: {e}")
                            continue
                    else:
                        # entry is not a dictionary, skip it
                        continue

    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Critical error when updating remote database. Exception: {e}")

    logger.success("realtime_stock_insert.py ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

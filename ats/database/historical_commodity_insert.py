import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import db_handler, file_handler

logger = Logger.instance()
connection_manager = db_handler.ConnectionManager.instance()


def check_keys(entry):
    logger.debug("Historical commodity insertion: checking keys")
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


def execute_insert(connection, entry, commodity_id):
    logger.info(f"Inserting record for commodity ID: {commodity_id}")
    # get key value, assign value to key. if key doesn't exist, assign value of None
    row = check_keys(entry)
    # append generated id
    row["commodity_id"] = commodity_id

    # check if record exists already
    check_query = sqlalchemy.text(
        "SELECT COUNT(*) FROM `historical_commodity_values` WHERE commodity_id = :commodity_id AND date = :_historical_date"
    )
    result = connection.execute(check_query, row).scalar()

    if result > 0:
        logger.warning(
            f"Record for commodity with ID: {commodity_id} already exists. Skipping to next record."
        )
        return
    try:
        # parameterized query
        query = sqlalchemy.text(
            "INSERT INTO `historical_commodity_values` VALUES (:commodity_id, :_historical_date, :_historical_open, :_historical_high, :_historical_low, :_historical_close, :_historical_adjClose, :_historical_volume, :_historical_unadjustedVolume, :_historical_change, :_historical_changePercent, :_historical_vwap, :_historical_changeOverTime)"
        )
        # Execute row insertion
        connection.execute(query, row)
    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(
            f"Failed to insert record for commodity {commodity_id} with date {entry['_historical_date']}: {e}"
        )


def get_commodity_id(entry, connection):
    logger.debug("Assigning historical commodity ID")
    commodity_id = None

    try:
        # set query parameters
        params = {
            "_historical_symbol": entry["_historical_symbol"],
            "_historical_name": entry["_historical_name"],
        }

        id_query = sqlalchemy.text(
            "SELECT id FROM `commodities` WHERE symbol = :_historical_symbol"
        )
        # check if commodity exists in commodities table
        result = connection.execute(id_query, parameters=params)

        row = result.one_or_none()

        if row is None:
            # if commodity doesn't exist, create new row in commodities table - trigger generates new ID
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO `commodities` (`commodityName`, `symbol`) VALUES (:_historical_name, :_historical_symbol)"
                ),
                parameters=params,
            )

            # get id generated from trigger
            result = connection.execute(id_query, parameters=params)
            commodity_id = result.one()[0]
        else:
            # if the commodity exists, fetch the existing ID
            commodity_id = row[0]
    except Exception as e:
        logger.error(f"Error occurred when assigning ID: {e}")

    return commodity_id


def main():
    # Load json data
    historical_data = file_handler.read_json(globals.FN_OUT_HISTORICAL_COMMODITY)
    try:
        # create with context manager
        with connection_manager.connect() as conn:
            # begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in historical_data:
                    if isinstance(entry, dict):
                        commodity_id = get_commodity_id(entry, conn)
                        try:
                            # Execute row insertion
                            execute_insert(conn, entry, commodity_id)
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

    logger.success("historical_commodity_insert.py ran successfully.")


if __name__ == "__main__":
    main()

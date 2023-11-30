# dakota/noah

import datetime
import connect
import json
import traceback

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def load_output_file(path):
    try:
        with open(path, "r") as output_file:
            output_data = json.load(output_file)
        return output_data
    except FileNotFoundError:
        print(f"Output file '{path}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{path}'")
        exit(1)

def check_keys(entry):
    # keys expected to be committed
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

    # get key value, assign value to key. if key doesn't exist, assign value of None
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, company_id):
    # check for any missing keys and assign values of None
    row = check_keys(entry)

    # check if earningsAnnouncement is not None, if it's not None convert to a datetime object and format for mysql datetime
    # if it is None, assign None to earnings_announcement
    earnings_announcement = (
        datetime.datetime.strptime(row["_realtime_earningsAnnouncement"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d %H:%M:%S") if row["_realtime_earningsAnnouncement"] is not None else None
    )

    # append generated id and modify earnings announcement
    row["company_id"] = company_id
    row["_realtime_earningsAnnouncement"] = earnings_announcement

    # parameterized query
    query = text("INSERT INTO `realtime_stock_values` VALUES (:company_id, :_realtime_date, :_realtime_price, :_realtime_changePercent, :_realtime_change, :_realtime_dayLow, :_realtime_dayHigh, :_realtime_yearHigh, :_realtime_yearLow, :_realtime_mktCap, :_realtime_exchange, :_realtime_volume, :_realtime_volAvg, :_realtime_open, :_realtime_prevClose, :_realtime_eps, :_realtime_pe, :_realtime_earningsAnnouncement, :_realtime_sharesOutstanding)")
    # execute row insertion, it would only work by explicitly naming the function args for unknown reasons
    connection.execute(statement=query, parameters=row)

def get_company_id(entry, conn):
    params = {"symbol": entry["_realtime_symbol"], "name": entry["_realtime_name"]}
    print(params)
    # check if company exists in companies table
    result = conn.execute(text("SELECT id FROM `companies` WHERE symbol = :symbol"), parameters=params)
    row = result.one_or_none()

    if row is None:
        # if company doesn't exist, create new row in companies table - trigger generates new ID
        conn.execute(text("INSERT INTO `companies` (`companyName`, `symbol`) VALUES (:name, :symbol)"), parameters=params)

        # get the generated ID
        result = conn.execute(text("SELECT id FROM `companies` WHERE symbol = :symbol"), parameters=params)
        company_id = result.one()[0]
    else:
        # if the company exists, fetch the existing ID
        company_id = row[0]
    return company_id


def main():
    # Load json data
    realtime_data = load_output_file(
        "./test_data/stocks_test.json"
    )

    try:
        # create connection with context manager, connection closed on exit
        with connect.connect() as conn:
            # begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in realtime_data:
                    if isinstance(entry, dict):
                        company_id = get_company_id(entry, conn)
                        try:
                            # process realtime data
                            execute_insert(conn, entry, company_id)
                        except SQLAlchemyError as e:
                            # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                            print(f"Error: {e}")
                            continue
                    else:
                        # entry is not a dictionary, skip it
                        continue

    except Exception as e:
        print(traceback.format_exc())
        print(f"Error: {e}")

# protected entrypoint
if __name__ == "__main__":
    main()
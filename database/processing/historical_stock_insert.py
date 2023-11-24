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


def execute_insert(connection, entry, company_id):
    for obj in range(len(entry["historical"])):
        # TODO; find test output data for historical, match up fields and update variables and insert query
        date = entry['historical'][obj]["_realtime_date"]
        price = entry['historical'][obj]["_realtime_price"]
        change_percentage = entry['historical'][obj]["_realtime_changePercent"]
        change = entry['historical'][obj]["_realtime_change"]
        day_high = entry['historical'][obj]["_realtime_dayHigh"]
        day_low = entry['historical'][obj]["_realtime_dayLow"]
        year_high = entry['historical'][obj]["_realtime_yearHigh"]
        year_low = entry['historical'][obj]["_realtime_yearLow"]
        mkt_cap = entry['historical'][obj]["_realtime_mktCap"]
        exchange = entry['historical'][obj]["_realtime_exchange"]
        open_price = entry['historical'][obj]["_realtime_open"]
        prev_close = entry['historical'][obj]["_realtime_prevClose"]
        volume = entry['historical'][obj]["_realtime_volume"]
        vol_avg = entry['historical'][obj]["_realtime_volAvg"]
        eps = entry['historical'][obj]["_realtime_eps"]
        pe = entry['historical'][obj]["_realtime_pe"]
        # ISO-8601 date, converting here for now but should probably be done during collection, or change the db field from datetime to iso
        # converting to datetime object (output data has an invalid iso-8601 format, so this is more complicated than it should be)
        earnings_announcement = datetime.datetime.strptime(
            entry["_realtime_earningsAnnouncement"], "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        # formatting to fit into mysql datetime type
        earnings_announcement = earnings_announcement.strftime("%Y-%m-%d %H:%M:%S")
        shares_outstanding = entry["_realtime_sharesOutstanding"]
        # Execute row insertion
        connection.execute(
            text(
                f"INSERT INTO `real_time_stock_values` VALUES ('{company_id}', '{date}', '{price}', '{change_percentage}', '{change}', '{day_high}', '{day_low}', '{year_high}', '{year_low}', '{mkt_cap}', '{exchange}', '{open_price}', '{prev_close}', '{volume}', '{vol_avg}', '{eps}', '{pe}', '{earnings_announcement}', '{shares_outstanding}')"
            )
        )


def get_company_id(entry, conn):
    symbol = entry["_realtime_symbol"]
    name = entry["_realtime_name"]
    # check if index exists in indexes table
    result = conn.execute(text(f"SELECT id FROM `companies` WHERE symbol = '{symbol}'"))
    row = result.one_or_none()

    if row is None:
        # if company doesn't exist, create new row in companies table - trigger generates new ID
        conn.execute(
            text(
                f"INSERT INTO `companies`(`companyName`, `symbol`) VALUES ('{name}', '{symbol}')"
            )
        )

        # get the generated ID
        result = conn.execute(
            text(f"SELECT id FROM `companies` WHERE symbol = '{symbol}'")
        )
        company_id = result.one()[0]
    else:
        # if the company exists, fetch the existing ID
        company_id = row[0]
    return company_id


def main():
    # Load json data
    realtime_data = load_output_file(
        "SMF_Project_2023\database\processing\\test_data\stocks_test.json"
    )

    try:
        # create with context manager, implicit commit on close
        with connect.connect() as conn:
            for entry in realtime_data:
                company_id = get_company_id(entry, conn)
                try:
                    # process realtime data
                    execute_insert(conn, entry, company_id)
                except SQLAlchemyError as e:
                    # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                    print(f"Error: {e}")
                    continue

    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")


# protected entrypoint
if __name__ == "__main__":
    main()

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
    row = [[x for x in entry.values()]]
    print(row)
    date = entry["_realtime_date"]
    price = entry["_realtime_price"]
    change_percentage = entry["_realtime_changePercent"]
    change = entry["_realtime_change"]
    day_high = entry["_realtime_dayHigh"]
    day_low = entry["_realtime_dayLow"]
    year_high = entry["_realtime_yearHigh"]
    year_low = entry["_realtime_yearLow"]
    mkt_cap = entry["_realtime_mktCap"]
    exchange = entry["_realtime_exchange"]
    open_price = entry["_realtime_open"]
    prev_close = entry["_realtime_prevClose"]
    volume = entry["_realtime_volume"]
    vol_avg = entry["_realtime_volAvg"]
    eps = entry["_realtime_eps"]
    pe = entry["_realtime_pe"]
    earnings_announcement = entry["_realtime_earningsAnnouncement"]
    shares_outstanding = entry["_realtime_sharesOutstanding"]
    # Execute row insertion
    connection.execute(
        text(
            f"INSERT INTO `real_time_stock_values` VALUES ('{company_id}', '{date}', '{price}', '{change_percentage}', '{change}', '{day_high}', '{day_low}', '{year_high}', '{year_low}', '{mkt_cap}', '{exchange}', '{open_price}', '{prev_close}', '{volume}', '{vol_avg}', '{eps}', '{pe}', '{earnings_announcement}', '{shares_outstanding}')"
        )
    )
    connection.commit()


def get_company_id(entry, conn):
    symbol = entry["_realtime_symbol"]
    name = entry["_realtime_name"]
    # check if index exists in indexes table
    result = conn.execute(text(f"SELECT id FROM `companies` WHERE symbol = '{symbol}'"))
    row = result.one_or_none()

    if row is None:
        # execute plain sql insert statement - transaction begins
        conn.execute(
            text(
                f"INSERT INTO `companies`(`companyName`, `symbol`) VALUES ('{name}', '{symbol}')"
            )
        )
        #conn.commit()
        # get the generated ID
        result = conn.execute(
            text(f"SELECT id FROM `companies` WHERE symbol = '{symbol}'")
        )
        company_id = result.one()[0]
    else:
        company_id = row[0]
    return company_id


def main():
    # Load json data
    realtime_data = load_output_file("SMF_Project_2023\database\processing\stocks_test.json")

    try:
        # create with context manager
        with connect.connect() as conn:
            for entry in realtime_data:
                company_id = get_company_id(entry, conn)
                try:
                    # process realtime data
                    execute_insert(conn, entry, company_id)
                except SQLAlchemyError as e:
                    print(f"Error: {e}")
                    continue

    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")

# protected entrypoint
if __name__ == "__main__":
    main()

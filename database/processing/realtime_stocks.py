import datetime
import connect
import json
import traceback

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
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


def main():
    # Load json data
    realtime_data = load_output_file("./data_collection/output/raw_index_output.json")

    try:
        # create with context manager
        with connect.connect() as conn:
            for entry in realtime_data:
                symbol = entry["symbol"]
                name = entry["name"]

                # check if index exists in companies table
                result = conn.execute(
                    text(f"SELECT id FROM `indexes` WHERE symbol = '{symbol}'")
                )
                row = result.one_or_none()

                if row is None:
                    conn.execute(
                        text(
                            f"INSERT INTO `indexes`(`indexname`, `symbol`) VALUES ('{name}', '{symbol}')"
                        )
                    )
                    conn.commit()

                    # get the generated ID
                    result = conn.execute(
                        text(f"SELECT id FROM `indexes` WHERE symbol = '{symbol}'")
                    )
                    company_id = result.one()[0]
                else:
                    company_id = row[0]

                # process realtime data

                # NOTE: entry keys will need to be changed to be inline with new output names
                date = datetime.datetime.fromtimestamp(entry["timestamp"])
                price = entry["price"]
                change_percentage = entry["changesPercentage"]
                change = entry["change"]
                day_high = entry["dayHigh"]
                day_low = entry["dayLow"]
                year_high = entry["yearHigh"]
                year_low = entry["yearLow"]
                mkt_cap = entry["marketCap"]
                exchange = entry["exchange"]
                open_price = entry["open"]
                prev_close = entry["previousClose"]
                volume = entry["volume"]
                vol_avg = entry["avgVolume"]

                try:
                    print(company_id)
                    # Execute row insertion
                    conn.execute(
                        text(
                            f"INSERT INTO `realtime_index_values` VALUES ('{company_id}', '{date}', '{price}', '{change_percentage}', '{change}', '{day_high}', '{day_low}', '{year_high}', '{year_low}', 0, '{exchange}','{open_price}', '{prev_close}', '{volume}', '{vol_avg}')"
                        )
                    )
                    # conn.commit()
                except SQLAlchemyError as e:
                    print(f"Error: {e}")

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")


# protected entrypoint
if __name__ == "__main__":
    main()

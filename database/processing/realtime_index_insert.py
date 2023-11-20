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

def execute_insert(connection, entry, index_id):
    date = datetime.datetime.fromtimestamp(entry["_realtime_date"])
    price = entry['_realtime_price']
    change_percentage = entry['_realtime_changesPercent']
    change = entry['_realtime_change']
    day_high = entry['_realtime_dayHigh']
    day_low = entry['_realtime_dayLow']
    year_high = entry['_realtime_yearHigh']
    year_low = entry['_realtime_yearLow']
    mkt_cap = entry['_realtime_mktCap']
    exchange = entry['_realtime_exchange']
    open_price = entry['_realtime_openPrice']
    prev_close = entry['_realtime_prevClose']
    volume = entry['_realtime_volume']
    vol_avg = entry['_realtime_volAvg']
    # Execute row insertion
    connection.execute(text(f"INSERT INTO `realtime_index_values` VALUES ('{index_id}', '{date}', '{price}', '{change_percentage}', '{change}', '{day_high}', '{day_low}', '{year_high}', '{year_low}', '{mkt_cap}, '{exchange}','{open_price}', '{prev_close}', '{volume}', '{vol_avg}')"))
    connection.commit()

def get_index_id(entry, conn):
    symbol = entry['symbol']
    name = entry['name']
    # check if index exists in indexes table
    result = conn.execute(text(f"SELECT id FROM `indexes` WHERE symbol = '{symbol}'"))
    row = result.one_or_none()

    if row is None:
        # execute plain sql insert statement - transaction begins
        conn.execute(text(f"INSERT INTO `indexes`(`indexName`, `symbol`) VALUES ('{name}', '{symbol}')"))
        conn.commit()
        # get the generated ID
        result = conn.execute(text(f"SELECT id FROM `indexes` WHERE symbol = '{symbol}'")) 
        index_id = result.one()[0]
    else:
        index_id = row[0] 
    return index_id

def main():
    # Load json data
    realtime_data = load_output_file('./test_files/static_test_files/static_index_realtime.json')

    try:
        # create with context manager
        with connect.connect() as conn:
            for entry in realtime_data:
                index_id = get_index_id(entry, conn)
                try:    
                    # process realtime data
                    execute_insert(conn, entry, index_id)
                except SQLAlchemyError as e:
                    # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                    print(f"Error: {e}")
                    continue

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")

# protected entrypoint
if __name__ == "__main__":
    main()
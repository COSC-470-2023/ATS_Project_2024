import datetime
import connect
import json
import traceback

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def load(path):
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
        
def execute_insert(connection, entry, commodity_id):
    # Declare and initialize variables
    date = entry['_realtime_date'] 
    price = entry['_realtime_price']
    changePercent = entry['_realtime_changePercent']
    change = entry['_realtime_change']
    dayHigh = entry['_realtime_dayHigh']
    dayLow = entry['_realtime_dayLow']
    yearHigh = entry['_realtime_yearHigh']
    yearLow = entry['_realtime_yearLow']
    marketCap = entry['_realtime_mktCap']
    exchange = entry['_realtime_exchange']
    commodityOpen = entry['_realtime_open']
    close = entry['_realtime_prevClose']
    volume = entry['_realtime_volume']
    volumeAverage = entry['_realtime_volAvg']
    
    # Execute row insertion
    connection.execute(
        text(
            f"insert into `realtime_commodity_values` values ('{commodity_id}', '{date}', '{price}', '{changePercent}', '{change}', '{dayHigh}', '{dayLow}', '{yearHigh}', '{yearLow}', '{marketCap}', '{exchange}', '{commodityOpen}', '{close}', '{volume}', '{volumeAverage}')"
            )
        )


def get_commodity_id(entry, connection):
    #Declare and initalize variables
    symbol = entry['_realtime_symbol']
    name = entry['_realtime_name']
    selectQuery = f"select id from `commodities` where symbol = '{symbol}'"
    
    # Check if commodity exists in commodities table
    result = connection.execute(text(selectQuery))
    row = result.one_or_none()

    if row is None:
        # if commodity doesn't exist, create new row in commodites table - trigger generates new ID
        connection.execute(
            text(
                f"INSERT INTO `commodities`(`id`, `commodityName`, `symbol`) values (NULL, '{name}', '{symbol}')"
            )
        )

        # get the generated ID
        result = connection.execute(text(selectQuery))
        company_id = result.one()[0]
    else:
        # if the company exists, fetch the existing ID
        company_id = row[0]
        
    return company_id

def main():
    # load json 
    # File name may need changes depending on query outputs
    # variable setting may have to be adjusted too
    data = load('../../data_collection/output/commodities_output.json')

    try:
        # create with context manager, implicit commit on close
        with connect.connect() as conn:
            for entry in data:
                commodity_id = get_commodity_id(entry, conn)
                try:
                    # process realtime data
                    execute_insert(conn, entry, commodity_id)
                except SQLAlchemyError as e:
                    # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                    print(f"Error: {e}")
                    continue

    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")

if __name__ == "__main__":
    main()

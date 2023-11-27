import connect
import json
import traceback
from sqlalchemy import sql
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Globals
OUTPUT_FILE_PATH = "./test_files/static_test_files/static_commodities_realtime.json"

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
        
def execute_insert(connection, entry, commodity_id):
    # Declare and initialize variables
    date = entry['_realtime_date'] 
    price = entry['_realtime_price']
    change_percentage = entry['_realtime_changePercent']
    change = entry['_realtime_change']
    day_low = entry['_realtime_dayLow']
    day_high = entry['_realtime_dayHigh']
    year_high = entry['_realtime_yearHigh']
    year_low = entry['_realtime_yearLow']
    market_cap = entry['_realtime_mktCap']
    if market_cap is None:
        market_cap = "NULL"
    else:
        market_cap = "'" + market_cap + "'"
    exchange = entry['_realtime_exchange']
    volume = entry['_realtime_volume']
    volume_avg = entry['_realtime_volAvg']
    open = entry['_realtime_open']
    prev_close = entry['_realtime_prevClose']
    
      # Execute row insertion
    connection.execute(
        text(
            f"INSERT INTO `realtime_commodity_values` VALUES ('{commodity_id}', '{date}', '{price}', '{change_percentage}', '{change}', '{day_low}', '{day_high}', '{year_high}', '{year_low}', {market_cap}, '{exchange}', '{volume}', '{volume_avg}', '{open}', '{prev_close}')"
        )
    )
    
def get_commodity_id(entry, connection):
    #Declare and initalize variables
    symbol = entry['_realtime_symbol']
    name = entry['_realtime_name']
    id_query = f"SELECT id FROM `commodities` WHERE symbol = '{symbol}'"
    
    # Check if commodity exists in commodities table
    result = connection.execute(text(id_query))
    row = result.one_or_none()

    if row is None:
        # if commodity doesn't exist, create new row in commodites table - trigger generates new ID
        connection.execute(
            text(
                f"INSERT INTO `commodities`(`commodityName`, `symbol`) VALUES ('{name}', '{symbol}')"
            )
        )
        

        # get the generated ID
        result = connection.execute(text(id_query))
        commodity_id = result.one()[0]
    else:
        # if the company exists, fetch the existing ID
        commodity_id = row[0]
    return commodity_id

def main():
    # load ouput
    realtime_data = load_output_file(OUTPUT_FILE_PATH)

    try:
        # create with context manager, implicit commit on close
        with connect.connect() as conn:
            for entry in realtime_data:
                commodity_id = get_commodity_id(entry, conn)
                try:
                    # process realtime data
                    execute_insert(conn, entry, commodity_id)
                except SQLAlchemyError as e:
                    # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                    print(f"Error: {e}")
                    continue
                    
            # Commit changes to database (otherwise it rolls back)
            conn.commit()       
            

    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")
        

# protected entrypoint
if __name__ == "__main__":
    main()

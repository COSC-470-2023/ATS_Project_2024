import connect
import json
import traceback
from sqlalchemy import sql
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
        
def execute_insert(connection, entry, commodity_id):
    # Declare and initialize variables
    date = entry['_realtime_date'] 
    price = entry['_realtime_price']
    change_percent = entry['_realtime_changePercent']
    change = entry['_realtime_change']
    day_high = entry['_realtime_dayHigh']
    day_low = entry['_realtime_dayLow']
    year_high = entry['_realtime_yearHigh']
    year_low = entry['_realtime_yearLow']
    mkt_cap = entry['_realtime_mktCap']
    mkt_cap = mkt_cap if mkt_cap != None else sql.null() # mkt_cap is usually null. Need to convert 'None' to 'NULL' for mysql
    exchange = entry['_realtime_exchange']
    commodity_open = entry['_realtime_open']
    close = entry['_realtime_prevClose']
    volume = entry['_realtime_volume']
    vol_avg = entry['_realtime_volAvg']
    
    # Execute row insertion
    connection.execute(
        text(
            f"INSERT INTO `realtime_commodity_values` VALUES ('{commodity_id}', '{date}', '{price}', '{change_percent}', '{change}', '{day_high}', '{day_low}', '{year_high}', '{year_low}', {mkt_cap}', '{exchange}', '{commodity_open}', '{close}', '{volume}', '{vol_avg}')"
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
        company_id = result.one()[0]
    else:
        # if the company exists, fetch the existing ID
        company_id = row[0]
        
    return company_id

def main():
    # load json 
    # File name may need changes depending on query outputs
    # variable setting may have to be adjusted too
    realtime_data = load_output_file('../../data_collection/output/commodity_output.json')

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

    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")

# protected entrypoint
if __name__ == "__main__":
    main()

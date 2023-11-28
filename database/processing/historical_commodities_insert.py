import connect
import json
import traceback
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Globals
OUTPUT_FILE_PATH = "./data_collection/output/historical_commodity_output.json"

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
        date = entry['_historical_date']
        commodity_open = entry['_historical_open']
        high = entry['_historical_high']
        low = entry['_historical_low']
        close = entry['_historical_close']
        adj_close = entry['_historical_adjClose']
        volume = entry['_historical_volume']
        unadjusted_volume = entry['_historical_unadjustedVolume']
        change = entry['_historical_change']
        change_percentage = entry['_historical_changePercent']
        vwap = entry['_historical_vwap']
        change_over_time = entry['_historical_changeOverTime']
        # Execute row insertion
        connection.execute(
            text(
                f"INSERT INTO `historical_commodity_values` VALUES ('{commodity_id}', '{date}', '{commodity_open}', '{high}', '{low}', '{close}', '{adj_close}', '{volume}', '{unadjusted_volume}', '{change}', '{change_percentage}', '{vwap}', '{change_over_time}')"
            )
        )
        
def get_commodity_id(entry, connection):
    #Declare and initialize variables
    symbol = entry["_historical_symbol"]
    name = entry["_historical_name"]
    id_query = f"SELECT id from `commodities` WHERE symbol = '{symbol}'"
    # check if index exists in indexes table
    result = connection.execute(text(id_query))
    row = result.one_or_none()

    if row is None:
        # if company doesn't exist, create new row in commodities table - trigger generates new ID
        connection.execute(
            text(
                f"INSERT INTO `commodities`(`commodityName`, `symbol`) VALUES ('{name}', '{symbol}')"
            )
        )
        connection.commit()
        # get the generated ID
        result = connection.execute(text(id_query))
        commodity_id = result.one()[0]
    else:
        # if the company exists, fetch the existing ID
        commodity_id = row[0]
    return commodity_id

def main():
    try:
        # load json data
        historical_data = load_output_file(OUTPUT_FILE_PATH)
        # create with context manager, implicit commit on close
        with connect.connect() as conn:
            for entry in historical_data:
                commodity_id = get_commodity_id(entry, conn)
                try:
                    # process historical data
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

if __name__ == "__main__":
    main()

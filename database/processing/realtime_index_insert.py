import connect
import json
import traceback
from sqlalchemy import sql
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Globals
OUTPUT_FILE_PATH = "./SMF_Project_2023/data_collection/output/realtime_index_output.json"

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
    # Declare and initialize variables
    date = entry["_realtime_date"]
    price = entry['_realtime_price']
    change_percentage = entry['_realtime_changePercent']
    change = entry['_realtime_change']
    day_low = entry['_realtime_dayLow']
    day_high = entry['_realtime_dayHigh']
    year_high = entry['_realtime_yearHigh']
    year_low = entry['_realtime_yearLow']
    mkt_cap =  entry['_realtime_mktCap']
    mkt_cap = mkt_cap if mkt_cap != None else sql.null() # mkt_cap is usually null. Need to convert 'None' to 'NULL' for mysql
    exchange = entry['_realtime_exchange']
    volume = entry['_realtime_volume']
    vol_avg = entry['_realtime_volAvg']
    open = entry['_realtime_open']
    prev_close = entry['_realtime_prevClose']
    
    # Execute row insertion
    connection.execute(
        text(
            f"INSERT INTO `realtime_index_values` VALUES ('{index_id}', '{date}', '{price}', '{change_percentage}', '{change}', '{day_low}', '{day_high}', '{year_high}', '{year_low}', {mkt_cap}, '{exchange}', '{volume}', '{vol_avg}', '{open}', '{prev_close}')"
        )
    )


def get_index_id(entry, connection):
    symbol = entry['_realtime_symbol']
    name = entry['_realtime_name']
    id_query = f"SELECT id FROM `indexes` WHERE symbol = '{symbol}'"
    # check if index exists in indexes table
    result = connection.execute(text(id_query))
    row = result.one_or_none()

    if row is None:
        # if index doesn't exist, create new row in indexes table - trigger generates new ID
        connection.execute(
            text(
                f"INSERT INTO `indexes` (`indexName`, `symbol`) VALUES ('{name}', '{symbol}')"
            )
        )
        connection.commit()
        # get the generated ID
        result = connection.execute(text(id_query)) 
        index_id = result.one()[0]
    else:
        # if the index exists, fetch the existing ID
        index_id = row[0] 
    return index_id

def main():
    try:
        # create with context manager
        with connect.connect() as conn:
            # Load output
            realtime_data = load_output_file(OUTPUT_FILE_PATH)
            for entry in realtime_data:
                if bool(entry):
                    index_id = get_index_id(entry, conn)
                    try:    
                        # process realtime data
                        execute_insert(conn, entry, index_id)
                    except SQLAlchemyError as e:
                        # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                        print(f"Error: {e}")
                        continue
                else:
                    continue
            conn.commit()
            

    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")

# protected entrypoint
if __name__ == "__main__":
    main()
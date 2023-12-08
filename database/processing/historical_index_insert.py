import connect
import json
import traceback
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Globals
OUTPUT_FILE_PATH = "./SMF_Project_2023/data_collection/output/historical_index_output.json"

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
        '_historical_date',
        '_historical_open',
        '_historical_high',
        '_historical_low',
        '_historical_close',
        '_historical_adjClose',
        '_historical_volume',
        '_historical_unadjustedVolume',
        '_historical_change',
        '_historical_changePercent',
        '_historical_vwap',
        '_historical_changeOverTime',
    ]
    # get key value, assign value to key. if key doesn't exist, assign value of None
    return {key: entry.get(key, None) for key in keys}
        
def execute_insert(connection, entry, index_id):
    # get key value, assign value to key. if key doesn't exist, assign value of None
    row = check_keys(entry)
    # append generated id
    row["index_id"] = index_id
    # parameterized query
    query = text("INSERT INTO `historical_index_values` VALUES (:index_id, :_historical_date, :_historical_open, :_historical_high, :_historical_low, :_historical_close, :_historical_adjClose, :_historical_volume, :_historical_unadjustedVolume, :_historical_change, :_historical_changePercent, :_historical_vwap, :_historical_changeOverTime)")
    # Excute row insertion
    connection.execute(query, row)

# Used to get id associated with an index        
def get_index_id(entry, connection):
    # set query parameters
    params = {"symbol": entry["_historical_symbol"], "name": entry["_historical_name"]}

    id_query = text("SELECT id FROM `indexes` WHERE symbol = :symbol")
    # check if index exists in indexes table
    result = connection.execute(text("SELECT id FROM `indexes` WHERE symbol = :symbol"), parameters=params)
    
    row = result.one_or_none()

    if row is None:
        # if index doesn't exist, create new row in indexes table - trigger generates new ID
        connection.execute(text("INSERT INTO `indexes` (`indexName`, `symbol`) VALUES (:name, :symbol)") ,parameters=params)
    
        # get id generated from trigger
        result = connection.execute(id_query, parameters=params) 
        index_id = result.one()[0]    
    else:
        # if the index exists, fetch the existing ID
        index_id = row[0]
    return index_id

def main():
    try:
        # Load json data
        historical_data = load_output_file(OUTPUT_FILE_PATH)
        # create with context manager
        with connect.connect() as conn:
            # begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in historical_data:
                    if isinstance(entry, dict):
                        index_id = get_index_id(entry, conn)
                        try:
                            # Excute row insertion
                            execute_insert(conn,entry,index_id)
                        except SQLAlchemyError as e:
                            # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                            print(f"Error: {e}")
                            continue
                    else:
                        # entry is not a dictionary, skip it
                        continue

                
    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")

# protected entrypoint
if __name__ == "__main__":
    main()

# THINGS TO UPDATE
    # for loop in execute_insert() will need to be changed to properly iterate over new historical output (once we know what that look like)

import connect
import json
import traceback
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

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
    # NOTE: entry keys will need to be changed to be inline with new output names
        date = entry['_historical_date']
        index_open = entry['_historical_open']
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
        # Excute row insertion
        connection.execute(
            text(
                f"INSERT INTO `historical_index_values` VALUES ('{index_id}', '{date}', '{index_open}', '{high}', '{low}', '{close}','{adj_close}', '{volume}', '{unadjusted_volume}', '{change}', '{change_percentage}', '{vwap}', '{change_over_time}')"
            )
        )
        connection.commit()

# Used to get id associated with an index        
def get_index_id(entry, connection):
    symbol = entry['_historical_symbol']
    name = entry['_historical_name']
    id_query = f"SELECT id FROM `indexes` WHERE symbol = '{symbol}'"
    # check if index exists in indexes table
    result = connection.execute(text(id_query))
    row = result.one_or_none()
    if row is None:
        # execute plain sql insert statement - trigger will fire
        connection.execute(
            text(
                f"INSERT INTO `indexes`(`indexname`, `symbol`) VALUES ('{name}', '{symbol}')"
            )
        )
        connection.commit()
        # get id generated from trigger
        result = connection.execute(text(id_query)) 
        index_id = result.one()[0]    
    else:
        index_id = row[0]
    return index_id

def main():
    try:
        # Load json data
        historical_data = load_output_file('./data_collection/output/index_output.json')
        # create with context manager
        with connect.connect() as conn:
            for entry in historical_data:
                index_id = get_index_id(entry, conn)
                try:
                    # Excute row insertion
                    execute_insert(conn,entry,index_id)
                except IntegrityError as e:
                    print("An error has occured, no insertion has been made: ", e)
                    continue
                
    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")

# protected entrypoint
if __name__ == "__main__":
    main()

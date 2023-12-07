import connect
import json
import traceback
from sqlalchemy import sql
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Globals
#OUTPUT_FILE_PATH = "./SMF_Project_2023/data_collection/output/realtime_commodity_output.json"
OUTPUT_FILE_PATH = "./static_commodities_realtime.json"

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
    # list of keys expected to be committed
    keys = [
        "_realtime_symbol",
        "_realtime_name",
        "_realtime_price",
        "_realtime_changePercent",
        "_realtime_change",
        "_realtime_dayLow",
        "_realtime_dayHigh",
        "_realtime_yearHigh",
        "_realtime_yearLow",
        "_realtime_mktCap",
        "_realtime_exchange",
        "_realtime_volume",
        "_realtime_volAvg",
        "_realtime_open",
        "_realtime_prevClose",
        "_realtime_eps",
        "_realtime_pe",
        "_realtime_earningsAnnouncement",
        "_realtime_sharesOutstanding",
        "_realtime_date",
    ]

    # get key value, assign value to key. if key doesn't exist, assign value of None
    return {key: entry.get(key, None) for key in keys}

def execute_insert(connection, entry, commodity_id):
    # check for missing keys, assign them values of None
    row = check_keys(entry)

    # append generated id to dict
    row["commodity_id"] = commodity_id

    # parameterized query
    query = text("INSERT INTO `realtime_commodity_values` VALUES (:commodity_id, :_realtime_symbol, :_realtime_name, :_realtime_price, :_realtime_changePercent, :_realtime_change, :_realtime_dayLow, :_realtime_dayHigh, :_realtime_yearHigh, , :_realtime_yearLow, :_realtime_mktCap, :_realtime_exchange, :_realtime_volume, :_realtime_volAvg, :_realtime_open, :_realtime_prevClose, :_realtime_eps, :_realtime_pe, :_realtime_earningsAnnouncement, :_realtime_sharesOutstanding, :_realtime_date)")

    # dict unpacked into query :parameters by matching key to parameter name
    connection.execute(statement=query, parameters=row)
    
def get_commodity_id(entry, connection):
    # create dict of parameters to pass
    params = {"symbol": entry["_realtime_symbol"], "name": entry["_realtime_name"]}

    # query to fetch id
    id_query = text("SELECT id FROM `commodities` WHERE symbol = ':_realtime_symbol'")

    # check if commodity exists in commodities table already
    result = connection.execute(id_query, parameters=params)
    row = result.one_or_none()

    if row is None:
        # if commodity doesn't exist, create new row in commodites table - trigger generates new ID
        connection.execute(text("INSERT INTO `commodities`(`commodityName`, `symbol`) VALUES (:_realtime_name, :_realtime_symbol)"), parameters=params)
        # get the generated ID
        result = connection.execute(id_query, parameters=params)
        commodity_id = result.one()[0]
    else:
        # if the company exists, fetch the existing ID
        commodity_id = row[0]
    return commodity_id

def main():
    # load ouput
    realtime_data = load_output_file(OUTPUT_FILE_PATH)

    try:
        # create connection with context manager, closed on exit
        with connect.connect() as conn:
            # begin transaction with context manager, implicit commit on exit
            with conn.begin():
                for entry in realtime_data:
                    if isinstance(entry, dict):
                        commodity_id = get_commodity_id(entry, conn)
                        try:
                            # process realtime data
                            execute_insert(conn, entry, commodity_id)
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

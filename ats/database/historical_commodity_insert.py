import json
import traceback

import sqlalchemy

from ats.globals import DIR_OUTPUT, OUTPUT_HISTORICAL_COMMODITY
from ats.util import connect


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


def execute_insert(connection, entry, commodity_id):
    # get key value, assign value to key. if key doesn't exist, assign value of None
    row = check_keys(entry)
    # append generated id
    row["commodity_id"] = commodity_id
    # parameterized query
    query = sqlalchemy.text("INSERT INTO `historical_commodity_values` VALUES (:commodity_id, :_historical_date, :_historical_open, :_historical_high, :_historical_low, :_historical_close, :_historical_adjClose, :_historical_volume, :_historical_unadjustedVolume, :_historical_change, :_historical_changePercent, :_historical_vwap, :_historical_changeOverTime)")
    # Execute row insertion
    connection.execute(query, row)


def get_commodity_id(entry, connection):
    # set query parameters
    params = {"symbol": entry["_historical_symbol"], "name": entry["_historical_name"]}

    id_query = sqlalchemy.text("SELECT id FROM `commodities` WHERE symbol = :symbol")
    # check if commodity exists in commodities table
    result = connection.execute(sqlalchemy.text("SELECT id FROM `commodities` WHERE symbol = :symbol"), parameters=params)
    
    row = result.one_or_none()

    if row is None:
        # if commodity doesn't exist, create new row in commodities table - trigger generates new ID
        connection.execute(sqlalchemy.text("INSERT INTO `commodities` (`commodityName`, `symbol`) VALUES (:name, :symbol)"), parameters=params)
    
        # get id generated from trigger
        result = connection.execute(id_query, parameters=params) 
        commodity_id = result.one()[0]    
    else:
        # if the commodity exists, fetch the existing ID
        commodity_id = row[0]
    return commodity_id


def main():
    try:
        # Load json data
        historical_data = load_output_file(DIR_OUTPUT + OUTPUT_HISTORICAL_COMMODITY)
        # create with context manager
        with connect.connect() as conn:
            # begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for entry in historical_data:
                    if isinstance(entry, dict):
                        commodity_id = get_commodity_id(entry, conn)
                        try:
                            # Execute row insertion
                            execute_insert(conn, entry, commodity_id)
                        except sqlalchemy.exc.SQLAlchemyError as e:
                            # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                            print(f"Error: {e}")
                            continue
                    else:
                        # entry is not a dictionary, skip it
                        continue 

    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")


if __name__ == "__main__":
    main()

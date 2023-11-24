import connect
import json
import traceback
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
    for obj in range(len(entry["historical"])):
        # Declare and initialize variables
        date = entry['historical'][obj]["_historical_date"]
        commodity_open = entry['historical'][obj]["_historical_open"]
        high = entry['historical'][obj]["_historical_high"]
        low = entry['historical'][obj]["_historical_low"]
        close = entry['historical'][obj]["_historical_close"]
        adj_close = entry['historical'][obj]["_historical_adjClose"]
        volume = entry['historical'][obj]["_historical_volume"]
        unadjusted_volume = entry['historical'][obj]["_historical_unadjustedVolume"]
        change = entry['historical'][obj]["_historical_change"]
        change_percentage = entry['historical'][obj]["_historical_changePercent"]
        vwap = entry['historical'][obj]["_historical_vwap"]
        change_over_time = entry['historical'][obj]["_historical_changeOverTime"]
        

        # Execute row insertion
        connection.execute(
            text(
                f"insert into `historical_commodity_values`(`commodity_id`, `date`, `open`, `high`, `low`, `close`, `adjClose`, `volume`, `unadjustedVolume`, `change`, `changePercentage`, `vwap`, `changeOverTime`) values ('{commodity_id}', '{date}', '{commodity_open}', '{high}', '{low}', '{close}', '{adj_close}', '{volume}', '{unadjusted_volume}', '{change}', '{change_percentage}', '{vwap}', '{change_over_time}')"
            )
        )
        connection.commit()
        
def get_commodity_id(entry, connection):
    #Declare and initialize variables
    symbol = entry["_historical_symbol"]
    name = entry["_historical_name"]
    id_query = f"select id from `commodities` where symbol = '{symbol}'"
    # check if index exists in indexes table
    result = connection.execute(text(id_query))
    row = result.one_or_none()

    if row is None:
        # if company doesn't exist, create new row in commodities table - trigger generates new ID
        connection.execute(
            text(
                f"INSERT INTO `commodities`(`commodityName`, `symbol`) values ('{name}', '{symbol}')"
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
    # load json 
    # idk what this will be called. update when able
    # variable setting may have to be adjusted too
    historical_data = load_output_file('./data_collection/output/commodity_output.json')

    try:
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

    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")

if __name__ == "__main__":
    main()

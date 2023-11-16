import connect
import json
import traceback
import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


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

def main():
    # load json 
    # idk what this will be called. update when able
    # variable setting may have to be adjusted too
    data = load('../../data_collection/output/historical_commodities_output.json')

    try:
        # create with context manager
        with connect.connect() as conn:
            for entry in data:
                symbol = entry['symbol']
                name = entry['name']
                # establish if it exists already
                result = conn.execute(text(f"select id from `commodities` where symbol = '{symbol}'"))
                row = result.one_or_none()
                if row is None:
                    # execute plain sql insert statement - transaction begins
                    conn.execute(text(f"insert into `commodities`(`id`, `commodityName`, `symbol`) values (NULL, '{name}', '{symbol}')"))
                    conn.commit()
                    # get the generated ID
                    result = conn.execute(text(f"select id from `commodities` where symbol = '{symbol}'")) 
                    CommodityID = result.one()[0]
                else:
                    CommodityID = row[0]
                
                # each commodity will have multiple dates with data
                for h_entry in entry['data']:
                    # putting data into variables (I really hate this)
                    date = h_entry['date']
                    commodityOpen = h_entry['open']
                    price = h_entry['price']
                    high = h_entry['high']
                    low = h_entry['low']
                    close = h_entry['close']
                    adjClose = h_entry['adjClose']
                    volume = h_entry['volume']
                    unadjustedVolume = h_entry['unadjustedVolume']
                    change = h_entry['change']
                    changePercent = h_entry['changePercentage']
                    vwap = h_entry['vwap']
                    changeOverTime = h_entry['changeOverTime']
                    try:
                        conn.execute(text(f"insert into `historical_commodity_values`(`commodity_id`, `date`, `open`, `high`, `low`, `close`, `adjClose`, `volume`, `unadjustedVolume`, `change`, `changePercentage`, `vwap`, `changeOverTime`) values ('{CommodityID}', '{date}', '{commodityOpen}', '{high}', '{low}', '{close}', '{adjustedClose}', '{volume}', '{unadjustedVolume}', '{change}', '{changePercent}', '{vwap}', '{changeOverTime}')"))
                        conn.commit()
                    except IntegrityError as e: # catch duplicate entry
                        pass # do nothing
                
            
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")

if __name__ == "__main__":
    main()

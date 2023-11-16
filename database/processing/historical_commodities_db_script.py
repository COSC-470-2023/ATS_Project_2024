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
    data = load('../../data_collection/output/unified_commodities_output.json')

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
                    
                # putting data into variables (I really hate this)
                date = datetime.datetime.fromtimestamp(entry['realtime_data']['timestamp']) 
                price = entry['realtime_data']['price']
                changePercent = entry['realtime_data']['changePercentage']
                change = entry['realtime_data']['change']
                dayHigh = entry['realtime_data']['dayHigh']
                dayLow = entry['realtime_data']['dayLow']
                yearHigh = entry['realtime_data']['yearHigh']
                yearLow = entry['realtime_data']['yearLow']
                marketCap = entry['realtime_data']['mktCap']
                exchange = entry['realtime_data']['exchange']
                commodityOpen = entry['realtime_data']['open']
                close = entry['realtime_data']['previousClose']
                volume = entry['realtime_data']['volume']
                volumeAverage = entry['realtime_data']['volAvg']
                try:
                    conn.execute(text(f"insert into `realtime_commodity_values`(`commodity_id`, `date`, `price`, `changePercentage`, `change`, `dayHigh`, `dayLow`, `yearHigh`, `yearLow`, `mktCap`, `exchange`, `open`, `prevClose`, `volume`, `volAvg`) values ('{CommodityID}', '{date}', '{price}', '{changePercent}', '{change}', '{dayHigh}', '{dayLow}', '{yearHigh}', '{yearLow}', '{marketCap}', '{exchange}', '{commodityOpen}', '{close}', '{volume}', '{volumeAverage}')"))
                    conn.commit()
                except IntegrityError as e: # catch duplicate entry
                    volume = volume # do nothing
                
                for h_entry in entry['historical_data']:
                    date = h_entry['date']
                    commodityOpen = h_entry['open']
                    high = h_entry['high']
                    low = h_entry['low']
                    close = h_entry['close']
                    volume = h_entry['volume']
                    try:
                        conn.execute(text(f"insert into `Commodity_Values`(`CommodityID`, `Date`, `Open`, `High`, `Low`, `Close`, `Volume`) values ('{CommodityID}', '{date}', '{commodityOpen}', '{high}', '{low}', '{close}', '{volume}')"))
                        conn.commit()
                    except IntegrityError as e: # catch duplicate entries
                        continue
                
            
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")

if __name__ == "__main__":
    main()

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

def insert(jsonFile):
    # load json 
    # idk what this will be called. update when able
    # variable setting may have to be adjusted too
    data = load(jsonFile)

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
                date = datetime.datetime.fromtimestamp(entry['timestamp']) 
                price = entry['price']
                changePercent = entry['changesPercentage']
                change = entry['change']
                dayHigh = entry['dayHigh']
                dayLow = entry['dayLow']
                yearHigh = entry['yearHigh']
                yearLow = entry['yearLow']
                marketCap = entry['marketCap']
                if marketCap is None:
                    marketCap = "NULL"
                else:
                    marketCap = "'" + marketCap + "'"
                exchange = entry['exchange']
                commodityOpen = entry['open']
                close = entry['previousClose']
                volume = entry['volume']
                volumeAverage = entry['avgVolume']
                try:
                    conn.execute(text(f"insert into `realtime_commodity_values`(`commodity_id`, `date`, `price`, `changePercentage`, `change`, `dayHigh`, `dayLow`, `yearHigh`, `yearLow`, `mktCap`, `exchange`, `open`, `prevClose`, `volume`, `volAvg`) values ('{CommodityID}', '{date}', '{price}', '{changePercent}', '{change}', '{dayHigh}', '{dayLow}', '{yearHigh}', '{yearLow}', {marketCap}, '{exchange}', '{commodityOpen}', '{close}', '{volume}', '{volumeAverage}')"))
                    conn.commit()
                except IntegrityError as e: # catch duplicate entry
                    pass
                
            
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")

if __name__ == "__main__":
    jsonFile = '../../data_collection/output/realtime_commodities_output.json'
    insert(jsonFile)


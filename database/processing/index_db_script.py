import datetime
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

def main():
    # load json
    realtime_data = load_output_file('./data_collection/output/raw_index_output.json')
    #historical_data = load_output_file('../../data_collection/output/historical_index_output.json')

    try:
        # create with context manager
        with connect.connect() as conn:
            for entry in realtime_data:
                symbol = entry['symbol']
                name = entry['name']

                # check if index exists in indexes table
                result = conn.execute(text(f"SELECT id FROM `indexes` WHERE symbol = '{symbol}'"))
                row = result.one_or_none()

                if row is None:
                    # execute plain sql insert statement - transaction begins
                    conn.execute(text(f"INSERT INTO `indexes`(`indexname`, `symbol`) VALUES ('{name}', '{symbol}')"))
                    conn.commit()

                    # get the generated ID
                    result = conn.execute(text(f"SELECT id FROM `indexes` WHERE symbol = '{symbol}'")) 
                    index_id = result.one()[0]
                else:
                    index_id = row[0]
                    
                # process realtime data
                date = datetime.datetime.fromtimestamp(entry["timestamp"])
                price = entry['price']
                change_percentage = entry['changesPercentage']
                change = entry['change']
                day_high = entry['dayHigh']
                day_low = entry['dayLow']
                year_high = entry['yearHigh']
                year_low = entry['yearLow']
                mkt_cap = entry['marketCap'] # Remove from db, seems to be null in all cases.
                exchange = entry['exchange']
                open_price = entry['open']
                prev_close = entry['previousClose']
                volume = entry['volume']
                vol_avg = entry['averageVolume']

                try:
                    conn.execute(text(f"INSERT INTO `realtime_index_values` VALUES ('{index_id}', '{date}', '{price}', '{change_percentage}', '{change}', '{day_high}', '{day_low}', '{year_high}', '{year_low}', 0, '{exchange}','{open_price}', '{prev_close}', '{volume}', '{vol_avg}')"))
                    conn.commit()           
                except IntegrityError as e:
                    continue

            # historical insertions may need to be handled in a different script

            # process historical data
            # for h_entry in historical_data:
            #     date = h_entry['date']
            #     index_open = h_entry['open']
            #     high = h_entry['high']
            #     low = h_entry['low']
            #     close = h_entry['close']
            #     adj_close = h_entry['adjClose']
            #     volume = h_entry['volume']
            #     unadjusted_volume = h_entry['unadjustedVolume']
            #     change = h_entry['change']
            #     change_percentage = h_entry['changePercentage']
            #     vwap = h_entry['vwap']
            #     change_over_time = h_entry['changeOverTime']
            #     try: 
            #         conn.execute(text(f"INSERT INTO `historical_index_values` VALUES ('{index_id}', '{date}', '{index_open}', '{high}', '{low}', '{close}','{adj_close}', '{volume}', '{unadjusted_volume}', '{change}', '{change_percentage}', '{vwap}', '{change_over_time}')"))
            #         conn.commit()
            #     except IntegrityError as e: # catch duplicate entries
            #         continue
                
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")

# protected h_entrypoint
if __name__ == "__main__":
    main()
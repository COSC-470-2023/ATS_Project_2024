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
    # Load json data
    historical_data = load_output_file('./data_collection/output/raw_historical_index_output.json')

    try:
        # create with context manager
        with connect.connect() as conn:
            for entry in historical_data:
                symbol = entry['symbol']

                # check if index exists in indexes table
                result = conn.execute(text(f"SELECT id FROM `indexes` WHERE symbol = '{symbol}'"))
                row = result.one_or_none()

                if row is None:
                    # execute plain sql insert statement - trigger will fire

                    # small issue here, name is not included in histrocial output:
                        # 'name' field may need to be appended to ouput or we make an API call here
                    conn.execute(text(f"INSERT INTO `indexes`(`indexname`, `symbol`) VALUES ('test', '{symbol}')"))
                    conn.commit()

                    # get id generated from trigger
                    result = conn.execute(text(f"SELECT id FROM `indexes` WHERE symbol = '{symbol}'")) 
                    index_id = result.one()[0]
                else:
                    index_id = row[0]
                    
                # process historical data
                # NOTE: entry keys will need to be changed to be inline with new output names
                for obj in range(len(entry['historical'])):
                    date = entry['historical'][obj]['date']
                    index_open = entry['historical'][obj]['open']
                    high = entry['historical'][obj]['high']
                    low = entry['historical'][obj]['low']
                    close = entry['historical'][obj]['close']
                    adj_close = entry['historical'][obj]['adjClose']
                    volume = entry['historical'][obj]['volume']
                    unadjusted_volume = entry['historical'][obj]['unadjustedVolume']
                    change = entry['historical'][obj]['change']
                    change_percentage = entry['historical'][obj]['changePercent']
                    vwap = entry['historical'][obj]['vwap']
                    change_over_time = entry['historical'][obj]['changeOverTime']
                
                    try:
                        # Excute row insertion
                        conn.execute(text(f"INSERT INTO `historical_index_values` VALUES ('{index_id}', '{date}', '{index_open}', '{high}', '{low}', '{close}','{adj_close}', '{volume}', '{unadjusted_volume}', '{change}', '{change_percentage}', '{vwap}', '{change_over_time}')"))
                        conn.commit()
                    except IntegrityError as e:
                        continue
                
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")

# protected entrypoint
if __name__ == "__main__":
    main()
# Helper function to convery historical stock list queries from FMP API into system usable output
# Supports static files and testing
# Pass the file name including file extension as an argument via script or cli
# Current version expects single additional argument indicating file name to be loaded from /test_files/static_test_files/...

import json
import sys
import os
import errno

# Load the static file with the raw query output
def load_json(file_name):
    file_path = '../test_files/static_test_files/' + file_name
    try:
        json_file = open(file_path, "r")
        parsed_json = json.load(json_file)
        return parsed_json
    except IOError:
        print(f'IOError while accessing configuration file at path: {file_path}')
        exit(1)  

# Overwrite the static file
def write_json(json_content, file_name):
    output_dir = "../test_files/static_test_files/"
    if not os.path.exists(os.path.dirname(output_dir)):
        try:
            os.makedirs(os.path.dirname(output_dir))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(output_dir+file_name, "w") as outfile:
        json.dump(json_content, outfile, indent=2)

# Converts and remaps the raw query output
def convert_raw_json(raw_json_output):
    modified_json_output = []
    # Find historicalStockList in the query output
    for hist in raw_json_output:
        if hist == 'historicalStockList':
            # Find each symbol in the query output
            for hist_entry in raw_json_output[hist]:
                print(hist_entry)
                symbol_name = hist_entry['symbol']
                print (symbol_name)
                # Pull values for each historical date entry
                for hist_values in hist_entry['historical']:
                    print(hist_values)
                    date = hist_values['date']
                    open = hist_values['open']
                    high = hist_values['high']
                    low = hist_values['low']
                    close = hist_values['close']
                    adjClose = hist_values['adjClose']
                    volume = hist_values['volume']
                    unadjustedVolume  = hist_values['unadjustedVolume']
                    change = hist_values['change']
                    changePercent = hist_values['changePercent']
                    vwap = hist_values['vwap']
                    changeOverTime = hist_values['changeOverTime']
                    name = get_symbol_name(symbol_name)
                    modified_json_output.append({
                        "_historical_symbol":symbol_name,
                        "_historical_name":name,
                        "_historical_date":date,
                        "_historical_open":open,
                        "_historical_high":high,
                        "_historical_low":low,
                        "_historical_close":close,
                        "_historical_adjClose":adjClose,
                        "_historical_volume":volume,
                        "_historical_unadjustedVolume":unadjustedVolume,
                        "_historical_change":change,
                        "_historical_changePercent":changePercent,
                        "_historical_vwap":vwap,
                        "_historical_changeOverTime":changeOverTime
                    })
        else:
            continue
    
    return modified_json_output

# Helper function to pull name associated with stock symbol from the config file names
def get_symbol_name(stock_symb):
    symbol_name = ''
    # Defined with names in system config as of 11/26/2023
    symbol_names = {"AAPL":"Apple Inc.", "NDAQ":"Nasdaq, Inc.", "META":"Meta Platforms, Inc.", "GOOG":"Alphabet Inc.",
                     "MSFT":"Microsoft Corporation", "NVDA":"NVIDIA Corporation", "WBA":"Walgreens Boots Alliance, Inc.",
                     "TSLA":"Tesla, Inc.", "AMZN":"Amazon.com, Inc.", "WMT":"Walmart Inc.", "ADBE":"Adobe Inc.",
                     "JNJ":"Johnson & Johnson", "V":"Visa Inc.", "CVX":"Chevron Corporation",
                     "^GSPC":"S&P 500", "^IXIC":"NASDAQ Composite", "^DJI":"Dow Jones Industrial Average", 
                     "^RUA":"Russell 3000", "^FTSE":"FTSE 100", "HGUSD":"Copper", "CLUSD":"Crude Oil", "GCUSD":"Gold Futures",
                     "SIUSD":"Silver Futures", "NGUSD":"Natural Gas"} 
    if stock_symb in symbol_names:
        symbol_name = symbol_names[stock_symb]
    
    return symbol_name

def main(json_file_name):
    raw_json_file = load_json(json_file_name)
    remapped_output = convert_raw_json(raw_json_file)
    # Slicing the raw off the file name
    output_json_file_name = json_file_name[json_file_name.find('_')+1:]
    write_json(remapped_output, output_json_file_name)
    exit(0)

if __name__ == "__main__":
    print(str(sys.argv))
    main(sys.argv[1])
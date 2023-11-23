# Helper function to remap FinancialModelingPrep RAW API query output into expected output field names
import json

# Global var for output for bonds fields
bonds__fields = ["_bond_name",
"_bond_date",
"_bond_rate",
"_bond_duration",
"_bond_currency",
"_bond_month1",
"_bond_month2",
"_bond_month3",
"_bond_month6",
"_bond_year1",
"_bond_year2",
"_bond_year3",
"_bond_year5",
"_bond_year7",
"_bond_year10",
"_bond_year20",
"_bond_year30"]
# Global var for output for realtime query fields
_realtime_fields = ["_realtime_name",
"_realtime_symbol",
"_realtime_date",
"_realtime_price",
"_realtime_changePercent",
"_realtime_change",
"_realtime_dayHigh",
"_realtime_dayLow",
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
"_realtime_sharesOutstanding"]
# Global var for output historical query fields
_historical_fields = ["_historical_name",
"_historical_symbol",
"_historical_date",
"_historical_open",
"_historical_high",
"_historical_low",
"_historical_close",
"_historical_adjClose",
"_historical_volume",
"_historical_unadjustedVolume",
"_historical_change",
"_historical_changePercent",
"_historical_vwap",
"_historical_changeOverTime"]
# TODO Company Info remapping

# Load specified file for conversion
def load_config(json_file_name):
    config_path = "test_files/static_test_files/{json_file_name}"
    try:
        config_file = open(config_path, "r")
        config = json.load(config_file)
        return config
    except IOError:
        print(f"IOError while accessing historical query config file at path: {config_path}")

def remap_bonds():

    return 1

def remap_realtime():
    return 1

def remap_historical():
    return 1

def remap_company_info():
    return 1
def main(json_file_name):
    initial_json_file = load_config(json_file_name)

    return 1
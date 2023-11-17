"""
- This script is used to take stock data collected from the Financial Modeling Prep API, and load it into the OLTP database.
- Data is read from a JSON output file, validated, then inserted into the database.
"""

import connect
import json
import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

def read_config(filename):
    try:
        with open(filename, "r") as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Config file '{filename}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{filename}'")
        exit(1)

def read_output(filename):
    try:
        with open(filename, "r") as output_file:
            config = json.load(output_file)
        return config
    except FileNotFoundError:
        print(f"Output file '{filename}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{filename}'")
        exit(1)


stock_data = read_output("../../Data_Collection/Output/Stocks_Output.json")

def main():
    try:
        with connect() as conn:
            # iterate over stock data
            for stock in stock_data:
                symbol = stock["symbol"]
                company_name = stock["name"]
                open_price = stock["open"]
                high_price = stock["dayHigh"]
                low_price = stock["dayLow"]
                close_price = stock["price"]
                volume = stock["volume"]
                exchange = stock["exchange"]
                date = datetime.datetime.fromtimestamp(
                    stock["timestamp"]
                )

                fetch_company_id = conn.execute(text(f"SELECT id FROM companies WHERE companyname = '{company_name}' AND Symbol = '{symbol}'"))
                insert_company = conn.execute(text(f"INSERT INTO Companies (CompanyName, Symbol) VALUES ('{company_name}', '{symbol}')"))
                conn.execute(text("insert into `Companies` values (1,2,3)"))
                conn.commit()
                result = conn.execute(text("select * from `Bonds`"))
                for row in result:
                    print(row.Column)
    except Exception as e:
        print(e)
        print("SQL Connection error")

if __name__ == "__main__":
    main()
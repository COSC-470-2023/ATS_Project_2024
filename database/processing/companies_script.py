
- This script is used to take stock data collected from the Financial Modeling Prep API, and load it into the OLTP database.
- Data is read from a JSON output file, validated, then inserted into the database.


import connect
import json
import datetime
import credentials

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


def read_config(filename)
    try
        with open(filename, r) as config_file
            config = json.load(config_file)
        return config
    except FileNotFoundError
        print(fConfig file '{filename}' not found.)
        exit(1)
    except json.JSONDecodeError
        print(fError decoding JSON in '{filename}')
        exit(1)

def read_output(filename)
    try
        with open(filename, r) as output_file
            config = json.load(output_file)
        return config
    except FileNotFoundError
        print(fOutput file '{filename}' not found.)
        exit(1)
    except json.JSONDecodeError
        print(fError decoding JSON in '{filename}')
        exit(1)


stock_data = read_output(....Data_CollectionOutputStocks_Output.json)

try
    # create with context manager
    with connect.connect() as conn
        for entry in stock_data
            
            # establish if it exists already
            result = conn.execute(text(fselect ID from `Commodity_List` where Symbol = '{symbol}'))
            row = result.one_or_none()
            if row is None
                # execute plain sql insert statement - transaction begins
                conn.execute(text(finsert into `Commodity_List`(`ID`, `Name`, `Symbol`) values (NULL, '{name}', '{symbol}')))
                conn.commit()
                # get the generated ID
                result = conn.execute(text(fselect ID from `Commodity_List` where Symbol = '{symbol}')) 
                CommodityID = result.one()[0]
            else
                CommodityID = row[0]
                
            date = datetime.datetime.fromtimestamp(entry['realtime_data']['timestamp']) 
            commodityOpen = entry['realtime_data']['open']
            high = entry['realtime_data']['dayHigh']
            low = entry['realtime_data']['dayLow']
            #close = entry['realtime_data']['previousClose'] no close
            volume = entry['realtime_data']['volume']
            try
                conn.execute(text(finsert into `Commodity_Values`(`CommodityID`, `Date`, `Open`, `High`, `Low`, `Close`, `Volume`) values ('{CommodityID}', '{date}', '{commodityOpen}', '{high}', '{low}', null, '{volume}')))
                conn.commit()
            except IntegrityError as e # catch duplicate entry
                volume = volume # do nothing
            
            for h_entry in entry['historical_data']
                date = h_entry['date']
                commodityOpen = h_entry['open']
                high = h_entry['high']
                low = h_entry['low']
                close = h_entry['close']
                volume = h_entry['volume']
                try
                    conn.execute(text(finsert into `Commodity_Values`(`CommodityID`, `Date`, `Open`, `High`, `Low`, `Close`, `Volume`) values ('{CommodityID}', '{date}', '{commodityOpen}', '{high}', '{low}', '{close}', '{volume}')))
                    conn.commit()
                except IntegrityError as e # catch duplicate entries
                    continue
            
        
except Exception as e
    print(e)
    print(traceback.format_exc())
    print(SQL connection error)


try
    # Establish a connection to server
    connection = mysql.connector.connect(config[companies])

    if connection.is_connected()
        # Print the MySQL server version
        db_info = connection.get_server_info()
        print(fConnected to MySQL Server version {db_info})

        cursor = connection.cursor(buffered=True)

        # Iterate over stock data
        for stock in stock_data
            # Variable Declarations
            symbol = stock[symbol]
            company_name = stock[name]
            open_price = stock[open]
            high_price = stock[dayHigh]
            low_price = stock[dayLow]
            close_price = stock[price]
            volume = stock[volume]
            exchange = stock[exchange]
            date = datetime.datetime.fromtimestamp(
                stock[timestamp]
            )  # Date translated from Unix timestamp to DATETIME format

            # Queries
            get_company_id = fSELECT id FROM Companies WHERE CompanyName = '{company_name}' AND Symbol = '{symbol}'
            companies_insert = fINSERT INTO Companies (CompanyName, Symbol) VALUES ('{company_name}', '{symbol}')

            # Query Companies table for matching symbol.
            cursor.execute(fSELECT COUNT() FROM Companies WHERE symbol = '{symbol}')
            result = cursor.fetchone()
            num_rows = result[0]

            # If no matching symbol is found, create new entry in Companies table
            if num_rows == 0
                # companies_insert query will cause trigger to fire, generating a new companyID associated with the stock
                cursor.execute(companies_insert)
                connection.commit()
                # Query companies table for new generated ID
                cursor.execute(get_company_id)
                company_id = cursor.fetchone()[0]
                # Insert into stock_values table
                cursor.execute(
                    fINSERT INTO Stock_Values VALUES ('{company_id}', '{date}','{open_price}', '{high_price}', '{low_price}', '{close_price}', '{volume}', '{exchange}')
                )
                connection.commit()
            # If matching symbol, insert into stocks_values using retrieved ID
            elif num_rows == 1
                cursor.execute(get_company_id)
                company_id = cursor.fetchone()[0]
                cursor.execute(
                    fINSERT INTO Stock_Values VALUES ('{company_id}', '{date}','{open_price}', '{high_price}', '{low_price}', '{close_price}', '{volume}', '{exchange}')
                )
                connection.commit()

except mysql.connector.Error as err
    print(fError {err})
finally
    if connection.is_connected()
        # Close the database connection
        connection.close()
        print(Connection closed)

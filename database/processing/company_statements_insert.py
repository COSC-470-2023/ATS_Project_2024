# dakota/noah

import datetime
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


def execute_insert(connection, entry, company_id):
    # would be nice to sync the order of fields in the database to the order of keys in the output data
    # so we could use list comprehension instead. would be easier to manipulate the data and easier to pass parameters
    # for bound/prepared statements. also easier to maintain, key name changes shouldn't matter

    date = entry["_company_date"]
    price = entry["_company_price"]
    beta = entry["_company_beta"]
    volAvg = entry["_company_volAvg"]
    mktCap = entry["_company_mktCap"]
    latsDiv = entry["_company_lastDiv"]
    changes = entry["_company_changes"]
    currency = entry["_company_currency"]
    cik = entry["_company_cik"]
    isin = entry["_company_isin"]
    cusip = entry["_company_cusip"]
    exchangeFullName = entry["_company_exchangeFullName"]
    exchange = entry["_company_exchange"]
    industry = entry["_company_industry"]
    ceo = entry["_company_ceo"]
    sector = entry["_company_sector"]
    country = entry["_company_country"]
    fullTimeEmployees = entry["_company_fullTimeEmployees"]
    phone = entry["_company_phone"]
    address = entry["_company_address"]
    city = entry["_company_city"]
    state = entry["_company_state"]
    zip = entry["_company_zip"]
    dcfDiff = entry["_company_dcfDiff"]
    dcf = entry["_company_dcf"]
    ipoDate = entry["_company_ipoDate"]
    isEtf = 1 if entry["_company_isEtf"] else 0
    isActivelyTrading = 1 if entry["_company_isActivelyTrading"] else 0
    isAdr = 1 if entry["_company_isAdr"] else 0
    isFund = 1 if entry["_company_isFund"] else 0

    # Execute row insertion
    connection.execute(
        text(
            f"INSERT INTO `company_statements` VALUES ('{company_id}', '{date}', '{price}', '{beta}', '{volAvg}', '{mktCap}', '{latsDiv}', '{changes}', '{currency}', '{cik}', '{isin}', '{cusip}', '{exchangeFullName}', '{exchange}', '{industry}', '{ceo}', '{sector}', '{country}', '{fullTimeEmployees}','{phone}','{address}','{city}', '{state}','{zip}','{dcfDiff}','{dcf}','{ipoDate}','{isEtf}','{isActivelyTrading}','{isAdr}','{isFund}')")
    )
    connection.commit()


def get_company_id(entry, conn):
    name = entry["_company_name"]
    symbol = entry["_company_symbol"]
    # check if company exists in companies table
    result = conn.execute(text(f"SELECT id FROM `companies` WHERE symbol = '{symbol}'"))
    row = result.one_or_none()

    if row is None:
        # if company doesn't exist, create new row in companies table - trigger generates new ID
        conn.execute(
            text(
                f"INSERT INTO `companies`(`companyName`, `symbol`) VALUES ('{name}', '{symbol}')"
            )
        )

        # get the generated ID
        result = conn.execute(
            text(f"SELECT id FROM `companies` WHERE symbol = '{symbol}'")
        )
        company_id = result.one()[0]
    else:
        # if the company exists, fetch the existing ID
        company_id = row[0]
    return company_id


def main():
    # Load json data
    realtime_data = load_output_file("database/processing/test_data/company_test.json")

    try:
        # create with context manager, implicit commit on close
        with connect.connect() as conn:
            for entry in realtime_data:
                company_id = get_company_id(entry, conn)
                try:
                    # process realtime data
                    execute_insert(conn, entry, company_id)
                except SQLAlchemyError as e:
                    # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                    print(f"Error: {e}")
                    continue

    except Exception as e:
        print(traceback.format_exc())
        print(f"SQL connection error: {e}")

# protected entrypoint
if __name__ == "__main__":
    main()

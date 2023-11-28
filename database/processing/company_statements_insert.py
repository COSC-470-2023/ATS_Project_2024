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

    keys = [
        "_company_date",
        "_company_price",
        "_company_beta",
        "_company_volAvg",
        "_company_mktCap",
        "_company_lastDiv",
        "_company_changes",
        "_company_currency",
        "_company_cik",
        "_company_isin",
        "_company_cusip",
        "_company_exchangeFullName",
        "_company_exchange",
        "_company_industry",
        "_company_ceo",
        "_company_sector",
        "_company_country",
        "_company_fullTimeEmployees",
        "_company_phone",
        "_company_address",
        "_company_city",
        "_company_state",
        "_company_zip",
        "_company_dcfDiff",
        "_company_dcf",
        "_company_ipoDate",
        "_company_isEtf",
        "_company_isActivelyTrading",
        "_company_isAdr",
        "_company_isFund",
    ]

    row = {key: entry.get(key, None) for key in keys}

    # convert bool to int for insertion, modify in row
    row["_company_isEtf"] = 1 if entry["_company_isEtf"] else 0
    row["_company_isActivelyTrading"] = 1 if entry["_company_isActivelyTrading"] else 0
    row["_company_isAdr"] = 1 if entry["_company_isAdr"] else 0
    row["_company_isFund"] = 1 if entry["_company_isFund"] else 0

    # append generated id
    row["company_id"] = company_id

    # parameterized query
    query = text("INSERT INTO `company_statements` VALUES (:company_id, :_company_date, :_company_price, :_company_beta, :_company_volAvg, :_company_mktCap, :_company_lastDiv, :_company_changes, :_company_currency, :_company_cik, :_company_isin, :_company_cusip, :_company_exchangeFullName, :_company_exchange, :_company_industry, :_company_ceo, :_company_sector, :_company_country, :_company_fullTimeEmployees, :_company_phone, :_company_address, :_company_city, :_company_state, :_company_zip, :_company_dcfDiff, :_company_dcf, :_company_ipoDate, :_company_isEtf, :_company_isActivelyTrading, :_company_isAdr, :_company_isFund)")

    # execute insertion
    connection.execute(statement=query, parameters=row)


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
            with conn.begin():
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

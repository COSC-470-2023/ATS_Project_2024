import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import db_handler, file_handler

logger = Logger.instance()
connection_manager = db_handler.ConnectionManager.instance()


def check_keys(entry):
    """
    Checks keys, assigns value to None if key is not found/has no value
    :param entry: A key/value pair from the JSON output
    :return: Key/value pairs, if key/value is not detected(i.e. not provided by API), key will be assigned value None
    """
    logger.debug("Company Statement insertion: Checking keys")
    # List of expected keys
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
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, company_id):
    """
    Connects to database and executes MySQL insertion.
    :param connection: Connection to the database
    :param entry: A key/value pair
    :param company_id: A generated primary key for database
    """
    logger.debug(f"Inserting record for company ID: {company_id}")
    row = check_keys(entry)

    # If the key exists and value wasn't changed to None
    if row["_company_isEtf"] is not None:
        # Convert bool to int for insertion, modify in row
        row["_company_isEtf"] = 1 if row["_company_isEtf"] else 0
    if row["_company_isActivelyTrading"] is not None:
        row["_company_isActivelyTrading"] = (
            1 if row["_company_isActivelyTrading"] else 0
        )
    if row["_company_isAdr"] is not None:
        row["_company_isAdr"] = 1 if row["_company_isAdr"] else 0
    if row["_company_isFund"] is not None:
        row["_company_isFund"] = 1 if row["_company_isFund"] else 0

    # Append generated id
    row["company_id"] = company_id

    # Check if record exists already
    check_query = sqlalchemy.text(
        "SELECT COUNT(*) FROM `company_statements` WHERE company_id = :company_id AND date = :_company_date"
    )
    result = connection.execute(check_query, row).scalar()

    # If record exists, provide warning message and ignore insertion
    if result > 0:
        logger.warning(
            f"Record for company with ID: {company_id} and date: {row['_company_date']} already exists. Skipping to next record."
        )
        return

    # Parameterized query
    query = sqlalchemy.text(
        """INSERT INTO `company_statements` VALUES (:company_id, :_company_date, 
        :_company_price, :_company_beta, :_company_volAvg, :_company_mktCap, 
        :_company_lastDiv, :_company_changes, :_company_currency, :_company_cik, 
        :_company_isin, :_company_cusip, :_company_exchangeFullName, :_company_exchange, 
        :_company_industry, :_company_ceo, :_company_sector, :_company_country, 
        :_company_fullTimeEmployees, :_company_phone, :_company_address, :_company_city, 
        :_company_state, :_company_zip, :_company_dcfDiff, :_company_dcf, 
        :_company_ipoDate, :_company_isEtf, :_company_isActivelyTrading, :_company_isAdr, 
        :_company_isFund)"""
    )

    connection.execute(statement=query, parameters=row)


def get_company_id(entry, conn):
    """
    Queries the database to see if company already has an ID, if no ID is found for said company,
    the trigger will generate one. If an ID is found, return said ID.
    :param entry: A key/value pair
    :param conn: Connection to the database
    """
    logger.debug("Assigning company ID")
    company_id = None
    try:
        # Parameters for queries
        params = {
            "symbol": entry["_company_symbol"],
            "name": entry["_company_name"],
        }
        # Check if company exists in companies table
        result = conn.execute(
            sqlalchemy.text("SELECT id FROM `companies` WHERE symbol = :symbol"),
            parameters=params,
        )
        row = result.one_or_none()

        if row is None:
            # If company doesn't exist, create new row in companies table - trigger generates new ID
            conn.execute(
                sqlalchemy.text(
                    "INSERT INTO `companies` (`companyName`, `symbol`) VALUES (:name, :symbol)"
                ),
                parameters=params,
            )

            # Get the generated ID
            result = conn.execute(
                sqlalchemy.text("SELECT id FROM `companies` WHERE symbol = :symbol"),
                parameters=params,
            )
            company_id = result.one()[0]
        else:
            # If the company exists, fetch the existing ID
            company_id = row[0]
    except Exception as e:
        logger.error(f"Error occurred when assigning ID: {e}")
    return company_id


def main():
    # Loads the company output file, creates a database connection and executes insertion
    company_data = file_handler.read_json(globals.FN_OUT_COMPANIES)
    try:
        # Create with context manager, implicit commit on close
        with connection_manager.connect() as conn:
            with conn.begin():
                for entry in company_data:
                    if isinstance(entry, dict):
                        company_id = get_company_id(entry, conn)
                        try:
                            # Process company data
                            execute_insert(conn, entry, company_id)
                        except sqlalchemy.exc.SQLAlchemyError as e:
                            # Log sqlalchemy error, then continue to prevent silent rollbacks
                            logger.error(f"SQLAlchemy Exception: {e}")
                            continue
                    else:
                        # Entry is not a dictionary, skip it
                        continue

    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Error when updating remote database. Exception: {e}")

    logger.success("company_statements_insertion ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

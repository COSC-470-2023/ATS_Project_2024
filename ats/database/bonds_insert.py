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
    logger.debug("Bond insertion: Checking keys")
    # List of expected keys
    keys = [
        "_bond_date",
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
        "_bond_year30",
    ]
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, bond_id):
    """
    Connects to database and executes MySQL insertion.
    :param connection: Connection to the database
    :param entry: A key/value pair
    :param bond_id: A generated primary key for database
    """
    logger.debug(f"Inserting record for bond ID: {bond_id}")
    row = check_keys(entry)
    # Append generated id
    row["bond_id"] = bond_id

    # Check if record exists already
    check_query = sqlalchemy.text(
        "SELECT COUNT(*) FROM `bond_values` WHERE bond_id = :bond_id AND date = :_bond_date"
    )
    result = connection.execute(check_query, row).scalar()
    # If record exists, provide warning message and ignore insertion
    if result > 0:
        logger.warning(
            f"Record for bond with ID: {bond_id} and date: {row['_bond_date']} already exists. Skipping to next record."
        )
        return
    # Execute row insertion
    insert_query = sqlalchemy.text(
            "INSERT INTO `bond_values` VALUES (:bond_id, :_bond_date, :_bond_month1, :_bond_month2, :_bond_month3, "
            + ":_bond_month6, :_bond_year1, :_bond_year2, :_bond_year3, :_bond_year5, :_bond_year7, :_bond_year10, "
            + ":_bond_year20, :_bond_year30)"
    )
    connection.execute(insert_query, row)


def get_bond_id(entry, connection):
    """
    Queries the database to see if bond already has an ID, if no ID is found for said bond, the trigger will generate one.
    If ID is found, return said ID.
    :param entry: A key/value pair
    :param connection: Connection to the database
    """
    logger.debug("Assigning bond ID")
    bond_id = None
    # Declare and initialize variables
    name = entry["_bond_name"]
    id_query = f"SELECT id FROM `bonds` WHERE treasuryName = '{name}'"

    # Check if bond exists in bonds table
    result = connection.execute(sqlalchemy.text(id_query))
    row = result.one_or_none()
    try:
        if row is None:
            # If bond doesn't exist, create new row in bonds table - trigger generates new ID
            connection.execute(
                sqlalchemy.text(
                    f"INSERT INTO `bonds`(`treasuryName`) VALUES ('{name}')"
                )
            )
            # Get the generated ID
            result = connection.execute(sqlalchemy.text(id_query))
            bond_id = result.one()[0]
        else:
            # If the bond exists, fetch the existing ID
            bond_id = row[0]
    except Exception as e:
        logger.error(f"Error occurred when assigning ID: {e}")
    return bond_id


def main():
    # Loads the bonds output file, creates a database connection and executes insertion
    bonds_data = file_handler.read_json(globals.FN_OUT_BONDS)
    try:
        # Create with context manager, implicit commit on close
        with connection_manager.connect() as conn:
            for entry in bonds_data:
                if bool(entry):
                    bond_id = get_bond_id(entry, conn)
                    try:
                        # Process bond data
                        execute_insert(conn, entry, bond_id)
                    except sqlalchemy.exc.SQLAlchemyError as e:
                        # Log sqlalchemy error, then continue to prevent silent rollbacks
                        logger.error(f"SQLAlchemy Exception: {e}")
                else:
                    continue
            # Commit changes to database (otherwise it rolls back)
            conn.commit()
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Critical Error when updating remote database. Exception: {e}")

    logger.success("bonds_insert ran successfully.")


# Protected entrypoint
if __name__ == "__main__":
    main()

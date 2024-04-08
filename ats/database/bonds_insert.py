import traceback

import sqlalchemy

from ats import globals
from ats.logger import Logger
from ats.util import db_handler, file_handler

logger = Logger.instance()
connection_manager = db_handler.ConnectionManager.instance()


def check_keys(entry):
    logger.debug("Bond insertion: Checking keys")
    # keys expected to be committed
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
    # get key value, assign value to key. if key doesn't exist, assign value of None
    return {key: entry.get(key, None) for key in keys}


def execute_insert(connection, entry, bond_id):
    logger.info(f"Inserting record for bond ID: {bond_id}")
    # check for any missing keys and assign values of None
    row = check_keys(entry)
    # append generated id
    row["bond_id"] = bond_id

    # check if record exists already
    check_query = sqlalchemy.text(
        "SELECT COUNT(*) FROM `bond_values` WHERE bond_id = :bond_id AND date = :_bond_date"
    )
    result = connection.execute(check_query, row).scalar()
    if result > 0:
        logger.warning(
            f"Record for bond with ID: {bond_id} and date: {row['_bond_date']} already exists. Skipping to next record."
        )
        return
    print(row["bond_id"])
    # Execute row insertion
    connection.execute(
        sqlalchemy.text(
            """INSERT INTO `bond_values` VALUES (:bond_id, :_bond_date, :_bond_month1, :_bond_month2, :_bond_month3, 
            :_bond_month6, :_bond_year1, :_bond_year2, :_bond_year3, :_bond_year5, :_bond_year7, :_bond_year10, 
            :_bond_year20, :_bond_year30)"""
        )
    )


def get_bond_id(entry, connection):
    # Declare and initialize variables
    name = entry["_bond_name"]
    id_query = f"SELECT id FROM `bonds` WHERE treasuryName = '{name}'"

    # Check if bond exists in bonds table
    result = connection.execute(sqlalchemy.text(id_query))
    row = result.one_or_none()
    try:
        if row is None:
            # if bond doesn't exist, create new row in bonds table - trigger generates new ID
            connection.execute(
                sqlalchemy.text(
                    f"INSERT INTO `bonds`(`treasuryName`) VALUES ('{name}')"
                )
            )
            # get the generated ID
            result = connection.execute(sqlalchemy.text(id_query))
            bond_id = result.one()[0]
        else:
            # if the bond exists, fetch the existing ID
            bond_id = row[0]
    except Exception as e:
        logger.error(f"Getting ID failed: {e}")
    return bond_id


def main():
    # load output
    bonds_data = file_handler.read_json(globals.FN_OUT_BONDS)
    try:
        # create with context manager, implicit commit on close
        with connection_manager.connect() as conn:
            for entry in bonds_data:
                if bool(entry):
                    bond_id = get_bond_id(entry, conn)
                    try:
                        # process bond data
                        execute_insert(conn, entry, bond_id)
                    except sqlalchemy.exc.SQLAlchemyError as e:
                        # log sqlalchemy error, then continue to prevent silent rollbacks
                        logger.error(f"Error: {e}")
                else:
                    continue
            # Commit changes to database (otherwise it rolls back)
            conn.commit()
    except Exception as e:
        print(traceback.format_exc())
        logger.critical(f"Critical Error when updating remote database. Exception: {e}")

    logger.success("bonds_insert ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

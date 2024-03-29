import json
import traceback

import sqlalchemy

from ats import loguru_init
from ats.globals import DIR_OUTPUT, OUTPUT_BONDS
from ats.util import connect

# Loguru init
logger = loguru_init.initialize()


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


def execute_insert(connection, entry, bond_id):
    # Declare and initialize variables
    date = entry["_bond_date"]
    month1 = entry["_bond_month1"]
    month2 = entry["_bond_month2"]
    month3 = entry["_bond_month3"]
    month6 = entry["_bond_month6"]
    year1 = entry["_bond_year1"]
    year2 = entry["_bond_year2"]
    year3 = entry["_bond_year3"]
    year5 = entry["_bond_year5"]
    year7 = entry["_bond_year7"]
    year10 = entry["_bond_year10"]
    year20 = entry["_bond_year20"]
    year30 = entry["_bond_year30"]

    # Execute row insertion
    logger.info(f"Inserting record for bond ID: {bond_id}")
    connection.execute(
        sqlalchemy.text(
            f"INSERT INTO `bond_values` VALUES ('{bond_id}', '{date}', '{month1}', '{month2}', '{month3}', '{month6}', '{year1}', '{year2}', '{year3}', {year5}, '{year7}', '{year10}', '{year20}', '{year30}')"
        )
    )


def get_bond_id(entry, connection):
    # Declare and initialize variables
    name = entry["_bond_name"]
    id_query = f"SELECT id FROM `bonds` WHERE treasuryName = '{name}'"

    # Check if bond exists in bonds table
    result = connection.execute(sqlalchemy.text(id_query))
    row = result.one_or_none()

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
    return bond_id


def main():
    # load output
    bonds_data = load_output_file(DIR_OUTPUT + OUTPUT_BONDS)
    try:
        # create with context manager, implicit commit on close
        with connect.connect() as conn:
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
        print(f"SQL connection error: {e}")
        logger.critical(f"Error when connecting to remote database: {e}")

    logger.success("bonds_insert ran successfully.")


# protected entrypoint
if __name__ == "__main__":
    main()

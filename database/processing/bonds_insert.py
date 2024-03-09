import connect
import json
import traceback

from sqlalchemy import sql, text, SQLAlchemyError

from data_collection.collection.json_handler import json_load_output
from dev_tools import loguru_init

# Globals
OUTPUT_FILE_PATH = "./SMF_Project_2023/data_collection/output/bonds_output.json"

# Loguru init
logger = loguru_init.initialize()


def execute_insert(connection, entry, bond_id):
    logger.info(f"Inserting record for bond ID: {bond_id}")
    try:
        # Declare and initialize variables
        date = entry['_bond_date']
        month1 = entry['_bond_month1']
        month2 = entry['_bond_month2']
        month3 = entry['_bond_month3']
        month6 = entry['_bond_month6']
        year1 = entry['_bond_year1']
        year2 = entry['_bond_year2']
        year3 = entry['_bond_year3']
        year5 = entry['_bond_year5']
        year7 = entry['_bond_year7']
        year10 = entry['_bond_year10']
        year20 = entry['_bond_year20']
        year30 = entry['_bond_year30']
    except Exception as e:
        logger.error(f"Error occurred when assigning bond field values: {e}")
    
    # Execute row insertion
    connection.execute(
        text(
            f"INSERT INTO `bond_values` VALUES ('{bond_id}', '{date}', '{month1}', '{month2}', '{month3}', '{month6}', '{year1}', '{year2}', '{year3}', {year5}, '{year7}', '{year10}', '{year20}', '{year30}')"
        )
    )


def get_bond_id(entry, connection):
    logger.info("Assigning bond ID")

    try:
        # Declare and initialize variables
        name = entry['_bond_name']
        id_query = f"SELECT bond_id FROM `bonds` WHERE treasuryName = '{name}'"

        # Check if bond exists in bonds table
        result = connection.execute(text(id_query))
        row = result.one_or_none()
        if row is None:
            logger.debug("Bond ID not found, creating new row")
            # if bond doesn't exist, create new row in bonds table - trigger generates new ID
            connection.execute(
                text(
                    f"INSERT INTO `bonds`(`treasuryName`) VALUES ('{name}')"
                )
            )
            # get the generated ID
            result = connection.execute(text(id_query))
            bond_id = result.one()[0]
        else:
            # if the bond exists, fetch the existing ID
            bond_id = row[0]
    except Exception as e:
        logger.error(f"Error occurred when assigning ID: {e}")
    return bond_id


def main():
    # load output
    bonds_data = json_load_output(OUTPUT_FILE_PATH)
    try:
        # create with context manager, implicit commit on close
        with connect.connect() as conn:
            for entry in bonds_data:
                if bool(entry):
                    bond_id = get_bond_id(entry, conn)
                    try:
                        # process bond data
                        execute_insert(conn, entry, bond_id)
                    except SQLAlchemyError as e:
                        # log sqlalchemy error, then continue to prevent silent rollbacks
                        logger.error(f"Error: {e}")
                        continue
                else:
                    continue         
            # Commit changes to database (otherwise it rolls back)
            conn.commit()       
    except Exception as e:
        print(traceback.format_exc())
        logger.error(f"Error when connecting to remote database: {e}")

    logger.success("bonds_insertion ran successfully.")
        

# protected entrypoint
if __name__ == "__main__":
    main()

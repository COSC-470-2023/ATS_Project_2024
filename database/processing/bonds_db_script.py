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
        
def execute_insert(entry, entry_row, connection, bond_id):
    #declare and initialize variables, rate is handled a little differently since it's from the same spot as the duration
    dateVal = entry['_bond_date']
    rate = entry[entry_row]
    #execute insert into bond_values
    connection.execute(text(f"insert into `bond_values`(`Date`, `bondID`, `Rate`) values ('{dateVal}', '{bond_id}', '{rate}')"))

def get_bond_id(entry, entry_row, connection):
    currencyVal = entry['_bond_currency']
    treasuryNameVal = entry['_bond_name']
    
    if entry_row not in ["_bond_date", "_bond_currency", "_bond_name"]:
            duration = entry_row[6:]
            result = connection.execute(text(f"SELECT bond_id FROM `bonds` WHERE treasuryName = '{treasuryNameVal}' AND currency = '{currencyVal}' AND duration = '{duration}'"))
            sql_row = result.one_or_none()
            if sql_row is None:
                # execute plain sql insert statement - transaction begins
                connection.execute(text(f"INSERT INTO `bonds`(`bond_id`, `treasuryName`, 'currency', 'duration') VALUES (NULL, '{treasuryNameVal}', '{currencyVal}', '{duration}')"))
                connection.commit()
                # get the generated ID
                result = connection.execute(text(f"SELECT bond_id FROM `bonds` WHERE treasuryName = '{treasuryNameVal} AND 'currency = '{currencyVal}' AND duration = '{duration}'")) 
                bond_id = result.one()[0]
            else:
                bond_id = sql_row[0]
                
            return bond_id
    else:
        #returns false if the entry_row is either date, currency or name
        return False


def main():
    # load json
    data = load_output_file('../../Data_Collection/Output/bonds_output.json')

    try:
        # create with context manager
        with connect.connect() as conn:
            for entry in data:
               for entry_row in entry:
                   bond_id = get_bond_id(entry, entry_row, conn)
                   # If the returned bond_id is False then the insertion is skipped
                   if(bond_id == False):
                       continue
                   try:
                       # process bond data
                       execute_insert(entry, entry_row, conn, bond_id)
                   except SQLAlchemyError as e:
                       # catch base SQLAlchemy exception, print SQL error info, then continue to prevent silent rollbacks
                       print(f"Error: {e}")
                       continue
            
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")

if __name__ == "__main__":
    main()

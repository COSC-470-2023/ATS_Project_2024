import connect
import json
import traceback

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

#changes that will need to be made, Bonds table has now been split into 2 tables. New values in each table https://drive.google.com/drive/u/0/folders/144umsHenP5lvvVF1C70aVtW5BvJn6VTI
#table 1: Bonds(bond_id BIGINT, country VARCHAR2(30), duration VARCHAR2(10), currency VARCHAR2(8))
#table 2: Bond_values(bond_ID BIGINT, date DATETIME, rate DECIMAL)

def load(path):
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

def main():
    # load json
    data = load('../../Data_Collection/Output/bonds_output.json')

    try:
        # create with context manager
        with connect.connect() as conn:
            for entry in data:
                dateVal = entry['_bond_date']
                currencyVal = entry['_bond_currency']
                treasuryNameVal = entry['_bond_name']
                for row in entry:
                    # skip the first few rows
                    if row == "_bond_date" or "_bond_currency" or "_bond_name":
                        continue
                    duration = row[6:] # cut off the _bond_ stuff that exists for some reason
                    # see if the entry already exists, and if not, make it
                    result = conn.execute(text(f"SELECT bond_id FROM `bonds` WHERE treasuryName = '{treasuryNameVal} AND 'currency = '{currencyVal}' AND 'duration = '{duration}'"))
                    row = result.one_or_none()
                    if row is None:
                        # execute plain sql insert statement - transaction begins
                        conn.execute(text(f"INSERT INTO `bonds`(`bond_id`, `treasuryName`, 'currency', 'duration') VALUES (NULL, '{treasuryNameVal}', '{currencyVal}', '{duration}')"))
                        conn.commit()
                        # get the generated ID
                        result = conn.execute(text(f"SELECT bond_id FROM `bonds` WHERE treasuryName = '{treasuryNameVal} AND 'currency = '{currencyVal}'")) 
                        bondID = result.one()[0]
                    else:
                        bondID = row[0]                   
                    rate = entry[row]
                    try:
                        conn.execute(text(f"insert into `bond_values`(`Date`, `bondID`, `Rate`) values ('{dateVal}', '{bondID}', '{rate}')"))
                        conn.commit()
                    except IntegrityError as e: # catch duplicate entries
                        continue
                
            
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")

if __name__ == "__main__":
    main()

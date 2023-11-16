# -*- coding: utf-8 -*-
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
    data = load('../../Data_Collection/Output/Raw_Bonds_Output.json')

    try:
        # create with context manager
        with connect.connect() as conn:
            for entry in data:
                date = entry['date']
                
                result = conn.execute(text(f"select bond_id from `bond_values` where date = '{date}'"))
                row = result.one_or_none()
                if row is None:
                    # execute plain sql insert statement - transaction begins
                    conn.execute(text(f"insert into `bond_values`(`bond_id`, `date`) values (NULL, '{date}')"))
                    conn.commit()
                    # get the generated ID
                    result = conn.execute(text(f"select id from `bond_values` where date = '{date}'")) 
                    bondID = result.one()[0]
                else:
                    bondID = row[0]                   
                
                for d_entry in entry:
                    bondDuration = d_entry
                    rate = entry[d_entry]
                    currency = d_entry['currency']
                    country = d_entry['country']
                    try:
                        conn.execute(text(f"insert into `Bonds`('Bond_id', 'Country', `Duration`,'Currency', `Rate`) values ('{bondID}', '{country}', {bondDuration}', '{currency}', '{rate}')"))
                        conn.commit()
                    except IntegrityError as e: # catch duplicate entries
                        continue
                
            
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")

if __name__ == "__main__":
    main()
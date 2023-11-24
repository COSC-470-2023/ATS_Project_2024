import json
import traceback
from sqlalchemy import text
import connect


def load_output_file(path):
    try:
        with open(path, "r") as output_file:
            output_data = json.load(output_file)
            if not output_data:
                print("No symbol change update required")
        return output_data
    except FileNotFoundError:
        print(f"Error: Output file '{path}' not found.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in '{path}'.")
        print(e)
        exit(1)


def update_symbol(connection, symbol):
    try:
        # Variable Declarations
        name = symbol["name"]
        old_symbol = symbol["oldSymbol"]
        new_symbol = symbol["newSymbol"]

        #  SQL query
        company_update = text(f"UPDATE Companies SET companyName = '{name}', symbol = '{new_symbol}' WHERE symbol = '{old_symbol}'")

        connection.execute(company_update)
        connection.commit()
    except Exception as e:
        print(f"Error in updating database: {e}")
        print(traceback.format_exc())

def main():
    try:
        # Establish a connection to server
        with connect.connect() as conn:
            symbol_change = load_output_file('./SMF_Project_2023/data_collection/output/dummy_output_file.json')
            for symbol in symbol_change:
                update_symbol(conn, symbol)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("Database connection error")

if __name__ == "__main__":
    main()

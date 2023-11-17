import connect
import json
import traceback
from sqlalchemy import text


def load(path):
    try:
        with open(path, "r") as output_file:
            if output_file.read(2) == '[]':
                output_file.seek(0)
                print("No symbol change update required")
                exit(0)
            output_data = json.load(output_file)
        return output_data
    except FileNotFoundError:
        print(f"Output file '{path}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{path}'.")
        exit(1)


# Load database credentials from the config file
config = load("config.json")
symbol_change = load("data_collection/output/dummy_output_file.json")


def main():
    try:
        # Establish a connection to server
        with connect.connect() as conn:
            for symbol in symbol_change:
                # Variable Declarations
                date = symbol["date"]
                name = symbol["name"]
                old_symbol = symbol["oldSymbol"]
                new_symbol = symbol["newSymbol"]

                #  SQL query
                company_update = text(f"UPDATE Companies SET companyName = '{name}', symbol = '{new_symbol}' WHERE company_id IN (SELECT company_id FROM Companies WHERE symbol = '{old_symbol}';);")
                conn.execute(company_update)
                conn.commit()

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")


if __name__ == "__main__":
    main()


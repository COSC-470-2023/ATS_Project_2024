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
        print(f"Error: Output file '{path}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{path}'.")
        exit(1)

def update(conn, symbol):
    try:
        # Variable Declarations
        date = symbol["date"]
        name = symbol["name"]
        old_symbol = symbol["oldSymbol"]
        new_symbol = symbol["newSymbol"]

        #  SQL query
        company_update = text("UPDATE Companies SET companyName = %s, symbol = %s WHERE company_id IN (SELECT company_id FROM Companies WHERE symbol = %s)")
        # Use a tuple to parametize variables (prevent injection)
        data = (name, old_symbol, new_symbol)

        conn.execute(company_update, data)
        conn.commit()
    except Exception as e:
        print(f"Error in updating database: {e}")
        print(traceback.format_exc())
def main():
    try:
        # Load database credentials from the config file
        config = load("config.json")
        # Establish a connection to server
        with connect.connect(**config) as conn:
            symbol_change = load("data_collection/output/dummy_output_file.json")

            for symbol in symbol_change:
                update(conn, symbol)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("Database connection error")


if __name__ == "__main__":
    main()


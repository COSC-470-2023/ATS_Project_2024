import connect
import json
import traceback

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


# Read data collection output file when available
def read_output(filename):
    try:
        with open(filename, "r") as output_file:
            if output_file.read(2) == '[]':
                output_file.seek(0)
                print("No symbol change update required")
                exit(0)
            output = json.load(output_file)
        return output
    except FileNotFoundError:
        print(f"Output file '{filename}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{filename}'")
        exit(1)


def main():
    symbol_change = read_output("symbol_change_output.json")

    try:
        with connect.connect() as conn:
            # Iterate over symbol_change
            for symbol in symbol_change:
                # Variable Declarations
                date = symbol["date"]
                name = symbol["name"]
                old_symbol = symbol["oldSymbol"]
                new_symbol = symbol["newSymbol"]

                # update company table
                company_update = text(f"UPDATE Companies SET companyName = '{name}', symbol = '{new_symbol}' WHERE company_id IN (SELECT company_id FROM Companies WHERE symbol = '{old_symbol}')")

                try:
                    conn.execute(company_update)
                    conn.commit()
                except IntegrityError as ie:
                    print(f"Integrity Error: {ie}")
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("SQL connection error")


if __name__ == "__main__":
    main()

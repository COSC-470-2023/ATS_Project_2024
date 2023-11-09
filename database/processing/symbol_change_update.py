import mysql.connector
import json

def read_config(filename):
    try:
        with open(filename, "r") as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Config file '{filename}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{filename}'")
        exit(1)


# Load database credentials from the config file
config = read_config("config.json")

def read_output(filename):
    try:
        with open(filename, "r") as output_file:
            config = json.load(output_file)
        return config
    except FileNotFoundError:
        print(f"Output file '{filename}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{filename}'")
        exit(1)


# TODO read data collection output file when available
symbol_change = read_output(filename)


try:
    # Establish a connection to server
    connection = mysql.connect.connect(**config["atsdb"])

    if connection.is_connected():
        # Print the MySQL server version
        db_info = connection.get_server_info()
        print(f"Connected to MySQL Server version {db_info}")

        cursor = connection.cursor(buffered=True)

        # Iterate over symbol_change
        for symbol in symbol_change:
            # Variable Declarations
            date = symbol["date"]
            name = symbol["name"]
            old_symbol = symbol["oldSymbol"]
            new_symbol = symbol["newSymbol"]

            # Queries
            # TODO create sql queries to update the database with symbol change information

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if connection.is_connected():
        # Close connection
        connection.close()
        print("Connection closed")

from flask import Blueprint, render_template, request, flash, jsonify

import yaml
from flask_login import login_required
from .decorators import admin_required
from dotenv import load_dotenv
from ats.globals import FN_CFG_COMPANIES, FN_CFG_HISTORICAL, FN_CFG_REALTIME

load_dotenv()

configuration = Blueprint("configuration", __name__)


# Default route
@configuration.route("/", methods=["GET", "POST"])
@admin_required
def home():
    return render_template("configuration.html")


realtime_config_path = "./config/" + FN_CFG_REALTIME
historical_config_path = "./config/" + FN_CFG_HISTORICAL
company_config_path = "./config/" + FN_CFG_COMPANIES
api_stock_file = "./config/api_stock.yaml"
constituents = "./config/index_config.yaml"

config_list = [realtime_config_path, historical_config_path, company_config_path]


# Route for populating the current config list
@configuration.route("/get_config", methods=["GET"])
@admin_required
def get_config():
    """
    Retrieves and returns the current stock configuration in JSON format.
    **Future: Rework to use util classes**
    """
    # Get the config file
    with open(realtime_config_path, "r") as configfile:
        config = yaml.safe_load(configfile)

    # Extracting both symbols and name from stocks
    stock_info = [
        {"symbol": stock["symbol"], "name": stock["name"]}
        for stock in config.get("stocks", [])
    ]

    return jsonify(stock_info)


# Route for removing stock on the config
@configuration.route("/remove_config", methods=["POST"])
@admin_required
def remove_config():
    """
    Removes specified stocks from the configuration based on input symbols and updates the config file.
    **Future: Rework to use util classes**
    """
    symbols_to_remove = request.json.get('symbols', [])

    for file in config_list:
        # Load the config file
        with open(file, "r") as config_file:
            config = yaml.safe_load(config_file)

        # Remove the stocks
        if "stocks" in config:
            config["stocks"] = [
                stock
                for stock in config["stocks"]
                if stock["symbol"] not in symbols_to_remove
            ]

        # Save the modified config back to the file
        with open(file, "w") as config_file:
            yaml.dump(config, config_file)

    return jsonify({"message": "Stocks removed successfully"})


# Function to fetch all the stock from the API
# def fetch_stock_list():
#     api_key = os.getenv("ATS_API_KEY")
#     if not api_key:
#         raise ValueError("ATS_API_KEY environment variable is not set.")

#     url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}"
#     response = requests.get(url)

#     print("Response status code:", response.status_code)

#     if response.status_code == 200:
#         data = response.json()
#         symbols_list = []

#         stocks_list = [{'symbol': stock['symbol'], 'name': stock['name']} for stock in data]

#         yaml_data = {'stocks': stocks_list}

#         with open(api_stock_file, 'w') as yaml_file:
#             yaml.dump(yaml_data, yaml_file)

#         print("YAML file successfully created.")

#         return symbols_list
#     else:
#         print("Failed to fetch stock list:", response.status_code)
#         return None


@configuration.route("/compare_stocks", methods=["GET"])
@admin_required
def compare_stocks():
    """
    Compares stocks listed in the configuration file with those from the API.
    Returns stocks not common between the local config and API data.
    """
    # Load the config file
    with open(realtime_config_path, "r") as configfile:
        config = yaml.safe_load(configfile)

    # Fetch the list of stock from API
    # available_stocks = fetch_stock_list()

    # Load the api_stock.yaml
    with open(api_stock_file, "r") as configfile:
        api_stocks = yaml.safe_load(configfile)

    available_stocks = [
        {"symbol": stock["symbol"], "name": stock["name"]}
        for stock in api_stocks.get("stocks", [])
    ]

    # Check if available_stocks is empty
    if available_stocks is not None:
        # Check if 'stocks' key exists in config
        if "stocks" in config:
            # Extract symbols from config file
            config_symbols = {stock["symbol"] for stock in config["stocks"]}

            # Extract symbols from API
            api_symbols = {stock["symbol"] for stock in available_stocks}

            # Find symbols not common in both config and API
            not_common_symbols = list(api_symbols - config_symbols)

            # Filter available_stocks to get common stocks
            not_common_stocks = [
                {"symbol": stock["symbol"], "name": stock["name"]}
                for stock in available_stocks
                if stock["symbol"] in not_common_symbols
            ]

            return jsonify({"not_common_stocks": not_common_stocks})
        else:
            return jsonify(
                {"message": "No 'stocks' key found in config", "not_common_stocks": []}
            )
    else:
        return jsonify(
            {"message": "Failed to fetch available stocks", "not_common_stocks": []}
        )



@configuration.route("/add_stocks", methods=["POST"])
@admin_required
def add_stocks():
    """
    Adds new stocks to the configuration. Loads the config file, gets the selected symbols and names, and adds them to the config
    """
    with open(stock_config_file, 'r') as configfile:
        config = yaml.safe_load(configfile)

    # Get the selected symbols and names from the request JSON
    selected_stocks = request.json.get("selected_stocks", [])

    # Check if selected stocks are provided
    if selected_stocks:
        for file in config_list:
            # Load the config file
            with open(file, "r") as configfile:
                config = yaml.safe_load(configfile)

            # Ensure 'stocks' key exists in config
            if "stocks" not in config:
                config["stocks"] = []

            # Add the selected stocks to the config
            for stock in selected_stocks:
                if stock not in [stock["symbol"] for stock in config["stocks"]]:
                    config["stocks"].insert(
                        0, {"symbol": stock["symbol"], "name": stock["name"]}
                    )

            # Save the modified config back to the file
            with open(file, "w") as configfile:
                yaml.dump(config, configfile)

        return jsonify(
            {
                "message": "Selected stocks added successfully",
                "selected_stocks": selected_stocks,
            }
        )
    else:
        return jsonify({"message": "No stocks selected to add", "selected_stocks": []})

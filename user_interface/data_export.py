from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    jsonify,
    session,
)
from flask_login import login_required
from sqlalchemy import inspect
import csv

# import models
from .models import *

data_export = Blueprint("data_export", __name__)

# TODO: CHANGE THE IMPORT FROM WITH OPEN TO ALANS VERSION OF IMPORT

# Maps string representation of tabels so that they can be used from the form
entity_map = {
    "Companies": Companies,
    "Commodities": Commodities,
    "Indexes": Indexes,
    "Bonds": Bonds,
}


@data_export.route("", methods=["GET"])
@login_required
def load_stocks():
    if request.method == "GET":
        entity = request.args.get("dataValue")

        # Retrieve query params to pass to front-end
        realtime_disabled = request.args.get("realtimeDisabled", "false") == "true"
        historical_disabled = request.args.get("historicalDisabled", "false") == "true"

        if entity == "company-info" or entity == None:
            checklist_items = Companies.query.all()
        else:
            checklist_items = entity_map[entity].query.all()

        return render_template(
            "data_export.html",
            entity=entity,
            items=checklist_items,
            realtime_disabled=realtime_disabled,
            historical_disabled=historical_disabled,
        )


@data_export.route("/export-data", methods=["GET", "POST"])
@login_required
def export_data():
    if request.method == "POST":
        selected = request.form.getlist("data-item")
        table_prefix = request.form.get("data-type")
        entity = request.form.get("select-data")
        print(entity)
        data_table_name = ""
        id_specifier = ""

        # Dynamic query for getting all entities tracked in database (stocks, bonds, index, commodities)
        # Logic for dynamic table names (Will need to revist later for a better solution)
        if entity == "Companies" or entity == "None":
            id_specifier = "company_id"
            data_table_name = "StockValues"
            entity_query = Companies.query.filter(Companies.symbol.in_(selected))
        elif entity == "company-info":
            table_prefix = ""
            id_specifier = "company_id"
            data_table_name = "CompanyStatements"
            entity_query = Companies.query.filter(Companies.symbol.in_(selected))
        elif entity == "Bonds":
            table_prefix = ""
            id_specifier = "bond_id"
            data_table_name = "BondValues"
            entity_query = entity_map[entity].query.filter(
                entity_map[entity].treasuryName.in_(selected)
            )
        elif entity == "Indexes":
            id_specifier = "index_id"
            data_table_name = "IndexValues"
            entity_query = entity_map[entity].query.filter(
                entity_map[entity].symbol.in_(selected)
            )
        elif entity == "Commodities":
            print("hello for comm")
            id_specifier = "commodity_id"
            data_table_name = "CommodityValues"
            entity_query = entity_map[entity].query.filter(
                entity_map[entity].symbol.in_(selected)
            )

        ids = []
        # grabbing ids for all queried rows
        for entity in entity_query:
            ids.append(entity.id)

        print(data_table_name)

        table = table_prefix + data_table_name

        # table mapping instead of if hell, had to rewrite to work with getting the column headers
        table_mapping = {
            "CompanyStatements": CompanyStatements,
            "realtimeStockValues": RealtimeStockValues,
            "historicalStockValues": HistoricalStockValues,
            "realtimeIndexValues": RealtimeIndexValues,
            "historicalIndexValues": HistoricalIndexValues,
            "realtimeCommodityValues": RealtimeCommodityValues,
            "historicalCommodityValues": HistoricalCommodityValues,
            "BondValues": BondValues,
        }

        # dynamic query that selects the current table and queries it with the company ids
        query = table_mapping[table].query.filter(
            getattr(table_mapping[table], id_specifier).in_(ids)
        )

        # sqlalch->inspect to retrieve all columns headers (yes .c as columns seems shady as hell, but it seems to work ¯\_(ツ)_/¯)
        columnNames = [column.name for column in inspect(table_mapping[table]).c]

        with open("user_interface\output\data.csv", "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",")
            csvwriter.writerow(columnNames)  # adds first row as columns headers
            for row in query:  # writing the data from the query
                csvwriter.writerow([getattr(row, column) for column in columnNames])
                # gets the columns from the query and writes each cell one at a time based on the columns

        return send_file(
            "output\data.csv",
            mimetype="text/csv",
            as_attachment=True,
        )

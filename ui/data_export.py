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

from ats.globals import DIR_UI_OUPUT
from . import db

# import models
from .models import *

data_export = Blueprint("data_export", __name__)

# Maps string representation of tabels so that they can be used from the form
entity_table_map = {
    "Companies": Companies,
    "Commodities": Commodities,
    "Indexes": Indexes,
    "Bonds": Bonds,
    "company-info": Companies,
}

# Mapping prefix combined with table name to Models
value_table_map = {
    "CompanyStatements": CompanyStatements,
    "realtimeStockValues": RealtimeStockValues,
    "historicalStockValues": HistoricalStockValues,
    "realtimeIndexValues": RealtimeIndexValues,
    "historicalIndexValues": HistoricalIndexValues,
    "realtimeCommodityValues": RealtimeCommodityValues,
    "historicalCommodityValues": HistoricalCommodityValues,
    "BondValues": BondValues,
}

# Map to handle different cases based on entity type
id_table_map = {
    "Companies": ("company_id", "StockValues"),
    "company-info": ("company_id", "CompanyStatements"),
    "Bonds": ("bond_id", "BondValues"),
    "Indexes": ("index_id", "IndexValues"),
    "Commodities": ("commodity_id", "CommodityValues"),
}

# Get default data to populate page on initial load.
default_items = Companies.query.all()
default_fields = (
    Companies.__table__.columns.keys() + RealtimeStockValues.__table__.columns.keys()
)
name_field = "companyName"


# Default route (Hit when page first loads)
@data_export.route("/", methods=["GET", "POST"])
@login_required
def home():
    return render_template(
        "data_export.html",
        items=default_items,
        fields=default_fields,
        name_field=name_field,
    )


# Route for populating the data list base on form state
@data_export.route("/get-data-list", methods=["POST"])
@login_required
def get_data_list():
    selected_entity = request.form["selected_entity"]
    table = entity_table_map[selected_entity]

    # Serialize items from query to be passed as json
    items = [item.serialize() for item in table.query.all()]
    return jsonify({"items": items})


# Route for populating the field list based on form state
@data_export.route("/get-field-list", methods=["POST"])
@login_required
def get_field_list():
    selected_entity = request.form["selected_entity"]
    table_prefix = request.form["selected_data_type"]
    table_suffix = id_table_map[selected_entity][1]

    # Bonds and company-info have no 'realtime' or 'historical' prefix
    if selected_entity == "Bonds" or selected_entity == "company-info":
        table_name = table_suffix
    else:
        table_name = table_prefix + table_suffix

    # Determine tables base on mapped keys
    lookup_table = entity_table_map[selected_entity]
    values_table = value_table_map[table_name]

    # Get table fields
    lookup_fields = lookup_table.__table__.columns.keys()
    value_fields = values_table.__table__.columns.keys()

    return jsonify({"lookup_fields": lookup_fields, "value_fields": value_fields})


# Route for downloading data based on data selected in the form.
@data_export.route(
    "/export-data", methods=["GET", "POST"]
)  # TODO: Fix functionality to work with date range and selected fields
@login_required
def export_data():
    if request.method == "POST":
        # Collect form data
        selected_data = request.form.getlist("data-item")
        selected_lookup_fields = request.form.getlist("lookup-field-item")
        selected_value_fields = request.form.getlist("value-field-item")
        table_prefix = request.form.get("data-type")
        entity_type = request.form.get("select-data")

        # Assign mapped values
        id_specifier = id_table_map[entity_type][0]
        data_table_name = id_table_map[entity_type][1]

        # Dynamic query for getting all entitites tracked in database based on the form data given (stocks, bonds, index, commodities)
        if entity_type == "Bonds":
            entity_query = entity_table_map[entity_type].query.filter(
                entity_table_map[entity_type].treasuryName.in_(selected_data)
            )
        else:
            entity_query = entity_table_map[entity_type].query.filter(
                entity_table_map[entity_type].symbol.in_(selected)
            )

        # Store ids to be used for further queries
        ids = []
        for entity in entity_query:
            ids.append(entity.id)

        table = table_prefix + data_table_name

        # dynamic query that selects the current table and queries it with the company ids
        query = value_table_map[table].query.filter(
            getattr(value_table_map[table], id_specifier).in_(ids)
        )

        column_names = get_fields(value_table_map[table])

        output_file_name = "data.csv"

        output_file_path = os.path.join(DIR_UI_OUPUT, output_file_name)

        with open(output_file_path, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",")
            csvwriter.writerow(column_names)  # adds first row as columns headers
            for row in query:  # writing the data from the query
                csvwriter.writerow([getattr(row, column) for column in column_names])
                # gets the columns from the query and writes each cell one at a time based on the columns

        return send_file(
            "../" + output_file_path,
            mimetype="text/csv",
            as_attachment=True,
        )


def get_fields(table):
    return table.__table__.columns.keys()


def build_table_name(entity_type, table_prefix):
    data_table_name = id_table_map[entity_type][1]
    if entity_type == "Bonds" or entity_type == "company-info":
        table_prefix = ""

    table = table_prefix + data_table_name

    return table

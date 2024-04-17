import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    jsonify,
    session,
    flash,
)
from flask_login import login_required, current_user
from sqlalchemy import inspect
from datetime import datetime
import csv

from ats.globals import DIR_UI_OUTPUT
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
    "Companies": ("company_id", "StockValues", "Stock"),
    "company-info": ("company_id", "CompanyStatements", "Stock"),
    "Bonds": ("bond_id", "BondValues", "Bond"),
    "Indexes": ("index_id", "IndexValues", "Index"),
    "Commodities": ("commodity_id", "CommodityValues", "Commodity"),
}


# Default route (Hit when page first loads)
@data_export.route("/", methods=["GET", "POST"])
@login_required
def home():
    """
    Renders the data export homepage.
    :return: html template
    """
    return render_template("data_export.html", user=current_user)


@data_export.route("/get-data-list", methods=["POST"])
@login_required
def get_data_list():
    """
    Route for populating the data list base on form state.
    :return: a list of items based on the selected entity from the form.
    """
    selected_entity = request.form["selected_entity"]
    table = entity_table_map[selected_entity]

    # Serialize items from query to be passed as json
    items = [item.serialize() for item in table.query.all()]
    return jsonify({"items": items})


@data_export.route("/get-field-list", methods=["POST"])
@login_required
def get_field_list():
    """
    Route for populating the field list based on form state.
    :return: fields for selected data types based on the entity chosen in the form.
    """
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


@data_export.route("/export-data", methods=["GET", "POST"])
@login_required
def export_data():
    """
    Handles the export of data based on user selections, creating a CSV file and returning it to the user.
    """
    try:
        if request.method == "POST":
            # Collect form data
            selected_data = request.form.getlist("data-item")
            selected_lookup_fields = request.form.getlist("lookup-field-item")
            selected_value_fields = request.form.getlist("value-field-item")
            all_selected_fields = selected_lookup_fields + selected_value_fields
            entity_type = request.form.get("select-data")
            entity_name = id_table_map[entity_type][2]
            table_prefix = (
                ""
                if entity_type == "Bonds" or entity_type == "company-info"
                else request.form.get("data-type")
            )

            date_range = request.form.get("daterange")
            start_date, end_date = date_range.split(" - ")

            # Convert dates to datetime objects
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

            # Assign mapped values
            value_table_suffix = id_table_map[entity_type][1]
            value_table = value_table_map.get(table_prefix + value_table_suffix)
            lookup_table = entity_table_map[entity_type]

            # Check for data and field selection, if no selection, flash error message and return
            if not selected_data or not all_selected_fields:
                flash(
                    f"You must select at least one {entity_name} and at least one field before exporting.",
                    "error",
                )
                return redirect(request.referrer or url_for("data_export.home"))

            # Quries database based on form selections
            query = build_query(
                entity_type,
                lookup_table,
                value_table,
                selected_data,
                selected_lookup_fields,
                selected_value_fields,
                start_date,
                end_date,
            )

            # Build file path
            output_file_name = entity_type + "-data.csv"
            output_file_path = os.path.join(DIR_UI_OUTPUT, output_file_name)
            # Create ouput dir if it doesn't exist
            os.makedirs(os.path.dirname(DIR_UI_OUTPUT), exist_ok=True)

            with open(output_file_path, "w", newline="") as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=",")
                # add first row as columns headers
                csvwriter.writerow(all_selected_fields)
                # write query rows to file
                for row in query:
                    csvwriter.writerow(row)

            return send_file(
                "../" + output_file_path,
                mimetype="text/csv",
                as_attachment=True,
            )

    except Exception as e:
        flash(
            "An error occured while exporting your data. Please check the system logs, or contact the system administrator.",
            "error",
        )

    return redirect(request.referrer or url_for("data_export.home"))


def build_query(
    entity_type,
    lookup_table,
    value_table,
    selected_data,
    lookup_fields,
    value_fields,
    start_date,
    end_date,
):
    """
    Function that builds query based on the provided tables, table entities, fields, and date range
    :param entity_type: type of entity. Ex. 'Bonds', 'Companies' etc.
    :param lookup_table: table model used for retrieving lookup fields.
    :param value_table: table model used for retrieving value fields related to the entry.
    :param selected_data: List of identifiers selected by the user to filter the query.
    :param lookup_fields: List of lookup table column names to include in the query results.
    :param value_fields: List of value table column names to include in the query results.
    :param start_date: Start date for filtering
    :param end_date: End date for filtering
    :return: A list of results based on above params.
    """
    if entity_type == "Bonds":
        query = (
            db.session.query(lookup_table, value_table)
            .join(value_table)
            .filter(lookup_table.treasuryName.in_(selected_data))
            .filter(value_table.date >= start_date, value_table.date <= end_date)
            .with_entities(
                *[getattr(lookup_table, column) for column in lookup_fields]
                + [getattr(value_table, column) for column in value_fields]
            )
            .all()
        )
    else:
        query = (
            db.session.query(lookup_table, value_table)
            .join(value_table)
            .filter(lookup_table.symbol.in_(selected_data))
            .filter(value_table.date >= start_date, value_table.date <= end_date)
            .with_entities(
                *[getattr(lookup_table, column) for column in lookup_fields]
                + [getattr(value_table, column) for column in value_fields]
            )
            .all()
        )
    return query

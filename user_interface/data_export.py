from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
)
from flask_login import login_required
from sqlalchemy import inspect
import csv
import yaml
import sys

sys.path.insert(0, "./data_collection/collection")

from . import db

# import Models
from .models import Companies
from .models import RealtimeStockValues
from .models import HistoricalStockValues
from .models import CompanyStatements

# import yaml_handler as yh
data_export = Blueprint("data_export", __name__)

# TODO: CHANGE THE IMPORT FROM WITH OPEN TO ALANS VERSION OF IMPORTS


@data_export.route("")
@login_required
def load_stocks():
    stocks = Companies.query.all()
    return render_template("data_export.html", stocks=stocks)


@data_export.route("/export-data", methods=["GET", "POST"])
@login_required
def export_data():
    if request.method == "POST":
        selected = request.form.getlist("stock-name")
        table = request.form.get("table-name")
        if table is None:
            return "Table not found", 404
        
        companies = Companies.query.filter(Companies.symbol.in_(selected))

        ids = []
        #creating ids list for companies using the PK of the companies to avoid running joins on the database.
        for company in companies:
            ids.append(company.id)


        #table mapping instead of if hell, had to rewrite to work with getting the column headers
        table_mapping = {"historical": HistoricalStockValues,"realtimeData": RealtimeStockValues,"companyinfo": CompanyStatements,}
        
        
        #dynamic query that selects the current table and queries it with the company ids
        query = table_mapping[table].query.filter(table_mapping[table].company_id.in_(ids))

        #if hell that has been changed into mapping
        # elif table == "historical":
        #     query = HistoricalStockValues.query.filter(
        #         HistoricalStockValues.company_id.in_(ids)
        #     )
        # elif table == "realtimeData":
        #     query = RealtimeStockValues.query.filter(
        #         RealtimeStockValues.company_id.in_(ids)
        #     )
        # elif table == "companyinfo":
        #     query = CompanyStatements.query.filter(
        #         CompanyStatements.company_id.in_(ids)
        #     )
        
        #old query logic
        # query = RealtimeStockValues.query.filter(
        #     RealtimeStockValues.company_id.in_(ids)
        # )

        #sqlalch->inspect to retrieve all columns headers (yes .c as columns seems shady as hell, but it seems to work ¯\_(ツ)_/¯)
        columnNames = [column.name for column in inspect(table_mapping[table]).c]

        with open("user_interface\output\data.csv", "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",")
            csvwriter.writerow(columnNames) #adds first row as columns headers
            for row in query: #writing the data from the query
                csvwriter.writerow([getattr(row, column) for column in columnNames]) 
                #gets the columns from the query and writes each cell one at a time based on the columns

        #old write csv code
        # with open("user_interface\output\data.csv", "w", newline="") as csvfile:
        #     csvwriter = csv.writer(csvfile, delimiter=",")
        #     for stock in query:
        #         csvwriter.writerow(
        #             [
        #                 stock.company_id,
        #                 stock.date,
        #                 stock.price,
        #                 stock.changePercentage,
        #                 stock.change,
        #                 stock.dayLow,
        #                 stock.dayHigh,
        #                 stock.yearHigh,
        #                 stock.yearLow,
        #                 stock.mktCap,
        #                 stock.exchange,
        #                 stock.volume,
        #                 stock.volumeAvg,
        #                 stock.open,
        #                 stock.prevClose,
        #                 stock.eps,
        #                 stock.pe,
        #                 stock.earningsAnnouncement,
        #                 stock.sharesOutstanding,
        #             ]
        #         )

        return send_file(
            "output\data.csv",
            mimetype="text/csv",
            as_attachment=True,
        )

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
)
from flask_login import login_required
import csv
import yaml
import sys

sys.path.insert(0, "./data_collection/collection")

from . import db

# import Models
from .models import Companies
from .models import RealtimeStockValues

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

        companies = Companies.query.filter(Companies.symbol.in_(selected))

        ids = []

        for company in companies:
            ids.append(company.id)

        query = RealtimeStockValues.query.filter(
            RealtimeStockValues.company_id.in_(ids)
        )

        with open("user_interface\output\data.csv", "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",")
            for stock in query:
                csvwriter.writerow(
                    [
                        stock.company_id,
                        stock.date,
                        stock.price,
                        stock.changePercentage,
                        stock.change,
                        stock.dayLow,
                        stock.dayHigh,
                        stock.yearHigh,
                        stock.yearLow,
                        stock.mktCap,
                        stock.exchange,
                        stock.volume,
                        stock.volumeAvg,
                        stock.open,
                        stock.prevClose,
                        stock.eps,
                        stock.pe,
                        stock.earningsAnnouncement,
                        stock.sharesOutstanding,
                    ]
                )

        return send_file(
            "output\data.csv",
            mimetype="text/csv",
            as_attachment=True,
        )

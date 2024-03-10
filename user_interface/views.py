from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return redirect(url_for("views.login"))


@views.route("/login")
def login():
    return render_template("login.html")


@views.route("/configuration")
@login_required
def configuration():
    return render_template("configuration.html", user=current_user)


# @views.route('/data-export')
# @login_required
# def export():
#     return render_template('data_export.html', user=current_user)

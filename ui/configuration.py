from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from .decorators import admin_required

configuration = Blueprint("configuration", __name__)


@configuration.route("/")
@admin_required
def home():
    return render_template("configuration.html", user=current_user)

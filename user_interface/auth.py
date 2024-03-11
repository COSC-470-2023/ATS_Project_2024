from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import Users
from werkzeug.security import generate_password_hash, check_password_hash

# Create authorization Blueprint
auth = Blueprint("auth", __name__)


# TODO: Need to change error and success messages to be meaningful
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Users.query.filter_by(username=username).first()

        # Check for valid user
        if user:
            if user.password == password:
                flash("Login successful", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.configuration"))
            else:
                flash("error", category="error")
        else:
            flash("No user found", category="error")

    return render_template("login.html")


# Route for logout functionality
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# TODO: Functionality must be added with create user page
@auth.route("/create-user", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        first_name = request.form.get("first-name")
        last_name = request.form.get("last-name")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            pass

    return render_template("create_user.html")

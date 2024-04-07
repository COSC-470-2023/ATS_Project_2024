from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .decorators import admin_required

# Create authorization Blueprint
auth = Blueprint("auth", __name__)


@auth.route("/")
def home():
    return redirect(url_for("auth.login"))


# Route for handling login authentication
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        # Check for valid user
        if user:
            if check_password_hash(user.password, password):
                flash(f"Welcome, {user.firstName}!", category="success")
                login_user(user, remember=True)
                if user.isAdmin:
                    return redirect(url_for("configuration.home"))
                else:
                    return redirect(url_for("data_export.home"))
            else:
                flash(
                    "The password you provided was incorrect, please try again.",
                    category="error",
                )
        else:
            flash(
                "There is no account associated with that username. Please try again or contact a system administrator.",
                category="error",
            )

    return render_template("login.html")


# Route for logout functionality
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# Route for creating new users based on form data
@auth.route("/create-user", methods=["GET", "POST"])
@admin_required
def create_user():
    if request.method == "POST":
        first_name = request.form.get("first-name")
        last_name = request.form.get("last-name")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user_type = request.form.get("user-select")
        is_admin = True if user_type == "Admin" else False

        check_for_user = User.query.filter_by(username=username).first()

        # Verify matching passwords
        if password1 != password2:
            flash("Passwords do not match, please try again.", "error")
        # Check if user already exists
        elif check_for_user:
            flash(
                "A user with that username already exists, please try a different username.",
                "error",
            )
        else:
            try:
                new_user = User(
                    username=username,
                    password=generate_password_hash(password1),
                    firstName=first_name,
                    lastName=last_name,
                    isAdmin=is_admin,
                )
                db.session.add(new_user)
                db.session.commit()
                flash("User created succussfully!", "success")
            except Exception as e:
                flash(
                    "An error occured while attempting to create the account, please try again.", "error"
                )

    return render_template("create_user.html")


# TODO: Implement if there is time
@auth.route("/change-password", methods=["POST"])
@login_required
def change_password():
    if request.method == "POST":
        pass

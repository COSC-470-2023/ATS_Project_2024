import re
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .decorators import admin_required

MIN_USERNAME_LENGTH = 5
MIN_PASSWORD_LENGTH = 8
MIN_INPUT_LENGTH = 1
MAX_INPUT_LENGTH = 30

UNAME_REGEX = "^[a-zA-Z0-9_-]+$"
NAME_REGEX = "^[a-zA-Z]+$"
PASSWORD_REGEX = r"^[^\s'\"]*$"

# Create authorization Blueprint
auth = Blueprint("auth", __name__)


@auth.route("/")
def home():
    # Redirects to the login page.
    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login, input validation, user authentication.
    GET: Renders the login page.
    POST: Validates input and authenticates user.
    """
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        # Validate user input
        # Check username
        if not is_valid_input(
            username, UNAME_REGEX, MIN_USERNAME_LENGTH, MAX_INPUT_LENGTH
        ):
            flash("Please enter a valid username.", "error")
            return redirect(request.referrer or url_for("auth.home"))
        # Check password
        if not is_valid_input(password, PASSWORD_REGEX, 1, MAX_INPUT_LENGTH):
            flash("Please enter a valid password.", "error")
            return redirect(request.referrer or url_for("auth.home"))

        user = User.query.filter_by(username=username).first()

        # Check for valid user
        if user:
            if check_password_hash(user.password, password):
                flash(f"Welcome, {user.firstName}!", category="success")
                login_user(user, remember=True)
                # Redirect admins to configuration page, basic users to data-export
                if user.isAdmin:
                    return redirect(url_for("configuration.home"))
                else:
                    return redirect(url_for("data_export.home"))
            else:
                flash(
                    "Your username or password is incorrect, please try again.",
                    category="error",
                )
        else:
            flash(
                "Your username or password is incorrect, please try again.",
                category="error",
            )

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    # Logout current user and redirect to login page
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/create-user", methods=["GET", "POST"])
@admin_required
def create_user():
    """
    Route for creating new users based on form data.
    GET: Renders the user creation page.
    POST: Validates input, creates a new user if validation is successful.
    """
    if request.method == "POST":
        first_name = request.form.get("first-name").strip()
        last_name = request.form.get("last-name").strip()
        username = request.form.get("username").strip()
        password1 = request.form.get("password1").strip()
        password2 = request.form.get("password2").strip()
        user_type = request.form.get("user-select")
        is_admin = True if user_type == "Admin" else False

        # Validate user input
        if not is_valid_input(
            first_name, NAME_REGEX, MIN_INPUT_LENGTH, MAX_INPUT_LENGTH
        ):
            flash("Please enter a valid first name.", "error")
            return redirect(request.referrer)
        if not is_valid_input(
            last_name, NAME_REGEX, MIN_INPUT_LENGTH, MAX_INPUT_LENGTH
        ):
            flash("Please enter a valid last name.", "error")
            return redirect(request.referrer)
        # check username
        if not is_valid_input(
            username, UNAME_REGEX, MIN_USERNAME_LENGTH, MAX_INPUT_LENGTH
        ):
            flash("Please enter a valid username.", "error")
            return redirect(request.referrer)
        # check password
        if not is_valid_input(
            password1, PASSWORD_REGEX, MIN_PASSWORD_LENGTH, MAX_INPUT_LENGTH
        ):
            flash(
                f"The password you've provided is invalid, please ensure it is at least {MIN_PASSWORD_LENGTH} characters long.",
                "error",
            )
            return redirect(request.referrer)

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
                    "An error occured while attempting to create the account, please try again.",
                    "error",
                )

    return render_template("create_user.html")


@auth.route("/change-password", methods=["POST"])
@login_required
def change_password():
    # Placeholder. Implement in future
    if request.method == "POST":
        pass


def is_valid_input(input, regex, min_length, max_length):
    """
    Validates the input based on a regex pattern and length constraints.
    :param input: Input value retrieved from a form.
    :param regex: Regular expression used for input restriction.
    :param min_length: Minimum input length.
    :param max_length: Maximum input length.
    :return: True if the input is valid, False otherwise.
    """
    return (
        bool(re.match(regex, input))
        and len(input) <= max_length
        and len(input) >= min_length
    )

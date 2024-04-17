from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user


def admin_required(f):
    """
    Decorator for admin verificaiton. Redirects non-admin users.
    Users not logged in are redirected to the login page.
    :param f: The function to decorate.
    :return: Decorated function with access control.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login to access this page.", "error")
            return redirect(url_for("auth.login"))
        elif not current_user.isAdmin:
            flash("You do not have permission to access that page.", "error")
            return redirect(request.referrer)
        return f(*args, **kwargs)

    return decorated_function

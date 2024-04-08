from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user


# Decorator for admin verificaiton
def admin_required(f):
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

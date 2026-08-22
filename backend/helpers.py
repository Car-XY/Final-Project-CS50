import requests

from flask import flash, redirect, request, url_for, session
from functools import wraps


def apology(message, code=400):
    """Flash an error message and redirect the user back to where they came from"""

    flash(message, "error")
    # url_for checks for the route function name, in which case the homepage is index
    return redirect(request.referrer or url_for("index"))


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


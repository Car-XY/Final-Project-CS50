import requests

from flask import flash, redirect, request, url_for, session
from functools import wraps


def apology(message, redirect_url=None, error="error"):
    """Flash an error message and redirect the user"""

    # either pass in "success" for a green box or nothin for a red box
    flash(message, error)
    
    # either a url is passed in or it relies on fall backs: url_for checks for the route function name
    return redirect(redirect_url or request.referrer or url_for("index"))


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


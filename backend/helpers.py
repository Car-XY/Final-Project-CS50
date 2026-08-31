import requests
import sqlite3
import os

from flask import flash, redirect, request, url_for, session, g
from functools import wraps
from datetime import date, timedelta

# makes sure my database is always the same one no matter where I launch app.py from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "goal_tracker.db")

# Configure my database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def apology(message, redirect_url=None, error="error"):
    """Flash an error message and redirect the user"""

    # either pass in "success" for a green box or nothin for a red box
    flash(message, error)
    
    # either a url is passed in or it relies on fall backs: url_for checks for the route function name
    return redirect(redirect_url or request.referrer or url_for("index"))


def get_streak(habit_id):
    db = get_db()
    rows = db.execute(
        "SELECT completed_date FROM habit_logs WHERE habit_id = ? ORDER BY completed_date DESC",
        (habit_id,)
    ).fetchall()

    completed_dates = {row["completed_date"] for row in rows}

    streak = 0
    check_date = date.today()

    while check_date.isoformat() in completed_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak


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


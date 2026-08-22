import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
from flask_wtf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)
app.config["SECRET_KEY"] = "Anchor-Cary-Hehehaw"  # move to env var later

csrf = CSRFProtect(app)

# makes sure my database is always the same one no matter where I launch app.py from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "goal_tracker.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure my database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# automaticcally makes the user username available to jinja so I don't have to pass it in everytime
@app.context_processor
def inject_user():
    return dict(username=session.get("username"))

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    
    if request.method == "POST":

        # Forget any user_id
        session.clear()

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        db = get_db()
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),) # NEED THIS FOR THIS TO BE A ONE ITEM TUPLE, also for all future usecases values must be in tuples
        ).fetchall()  # in here db.execute pulls everything to a cursor, similar to a pointer in c, so fetchall() extracts all the info that the cursor is pointing to

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Remember username
        session["username"] = request.form.get("username")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure a username was submitted
        if not request.form.get("username"):  # ensures someone can't submit empty user
            return apology("must provide a username")

        # Ensure a password was submitted
        if not request.form.get("password"):
            return apology("must provide a password")

        # Ensure password and confirmation password match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Hash the password
        hash = generate_password_hash(request.form.get("password"))

        # Ensure username is not a duplicate
        try:
            db = get_db()
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       (request.form.get("username"), hash))
            db.commit() # as I am not using cs50 training wheels anymore, anytime I need to commit something to server files I need to do commit()
        except sqlite3.IntegrityError:  # good practice to define the error so that it is easier to debug
            return apology("username already taken")

        return redirect("/")
    else:
        # renders my register template if user did not click "register" button
        return render_template("register.html")
    

# remove this when shipping
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, port=5000)
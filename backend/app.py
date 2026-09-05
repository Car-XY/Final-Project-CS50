import os
import sqlite3
import re

from flask import Flask, flash, redirect, render_template, request, session, g, url_for
from flask_session import Session
from flask_wtf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, timedelta

from helpers import apology, login_required, get_db, get_streak

# Configure application
app = Flask(__name__)
app.config["SECRET_KEY"] = "Anchor-Cary-Hehehaw"  # move to env var later so it isn't leaked to github repo (also change it)

csrf = CSRFProtect(app)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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
    return render_template("index.html", greeting=True)


@app.route("/habits", methods=["GET", "POST"])
@login_required
def habits():
    # checking for completion button for streaking
    db = get_db()

    now = datetime.now()
    curr_date = now.strftime("%Y-%m-%d")

    if request.method == "POST":
        if request.form.get("completion_btt"):
            db.execute("INSERT INTO habit_logs (habit_id, completed_date) VALUES (?, ?)", 
                    (request.form.get("completion_btt"), curr_date))
            db.commit()
            return apology("Marked as done", error="success")
        else:
            return render_template("habits.html")
    else:
        habits = db.execute("SELECT id, habit, description, start_date, end_date, colour FROM habits WHERE user_id = ?", (session["user_id"],)).fetchall()

        id_list = [row["id"] for row in habits]
        # my streak table is created w/ unique(habit_id, completed_date) to ensure no two duplicates of habit and date can exist)
        streaks = {}
        completed_date = {}

        for habit_id in id_list:
            streaks[habit_id] = get_streak(habit_id)
            row = db.execute("SELECT completed_date FROM habit_logs WHERE habit_id = ? ORDER BY completed_date DESC LIMIT 1", (habit_id,)).fetchone()
            # if __ else None ensures that data is stored in my dictionary even when I don't have a mnost recent completed date and sqlite3 returns NoneType
            completed_date[habit_id] = row["completed_date"] if row else None
        return render_template ("habits.html", habits=habits, streak=streaks, completed_date=completed_date, today=curr_date)


@app.route("/habits/add", methods=["GET", "POST"])
@login_required
def addhabit():

    if request.method == "POST":
        habit = request.form.get("habit")
        start = request.form.get("start_date")
        end = request.form.get("end_date")
        colour = request.form.get("colour")

        # just in case no colour is submitted
        if not colour or not re.fullmatch(r"#[0-9a-fA-F]{6}", colour):
            colour = "#ffffff"  # fallback to default


        now = datetime.now()

        curr_date = now.strftime("%Y-%m-%d")

        if not habit:
            return apology("must give a name for your habit")

        if not start:
            return apology("must give a start date")

        if start > end:
            return apology("Start date cannot be after end date")

        if curr_date > end:
            return apology("End date cannot be before today")
        
        db = get_db()
        try:
            db.execute("INSERT INTO habits (user_id, habit, description, start_date, end_date, colour) VALUES (?, ?, ?, ?, ?, ?)", 
                    (session["user_id"], habit, request.form.get("description"), start, end, colour))
        except sqlite3.IntegrityError:
            return apology("Something went wrong saving this habit")
        
        db.commit()
        return apology("Habit creation successful!", redirect_url=url_for("habits"), error="success")
    else:
        return render_template("habit_add.html")


@app.route("/habits/edit", methods=["GET", "POST"])
@login_required
def edithabit():
    if request.method == "POST":
        db = get_db()
        rows = db.execute("SELECT id FROM habits WHERE user_id = ?", (session["user_id"],)).fetchall()

        # using list comprehension. Easier way to create new list from existing list
        id_list = [row["id"] for row in rows]

        for id in id_list:
            # checking for deletion of habit first
            if request.form.get(f"{id}_delete"):
                db.execute("DELETE FROM habits WHERE id = ?", (id,))
                db.commit()
                return apology("Habit Deleted!", error="success")
            
            habit = request.form.get(f"{id}_habit")
            start = request.form.get(f"{id}_start_date")
            end = request.form.get(f"{id}_end_date")
            colour = request.form.get(f"{id}_colour")

            # just in case no colour is submitted
            if not colour or not re.fullmatch(r"#[0-9a-fA-F]{6}", colour):
                colour = "#ffffff"  # fallback to default

            now = datetime.now()
            curr_date = now.strftime("%Y-%m-%d")

            if not habit:
                return apology(f"habit {habit}: must give a name for your habit")

            if not start:
                return apology(f"habit {habit}: must give a start date")

            if start > end:
                return apology(f"habit {habit}: Start date cannot be after end date")

            if curr_date > end:
                return apology(f"habit {habit}: End date cannot be before today")

            try:
                db.execute("""UPDATE habits SET 
                habit = ?, 
                description = ?, 
                start_date = ?, 
                end_date = ?, 
                colour = ?
                WHERE id = ?"""
                        , (habit, request.form.get(f"{id}_description"), start, end, colour, id))
            except sqlite3.IntegrityError:
                return apology(f"habit {habit}: something went wrong saving this habit")
            
            db.commit()
        return apology("Habits edited!", redirect_url=url_for("habits"), error="success")
    else:
        db = get_db()
        habits = db.execute("SELECT id, habit, description, start_date, end_date, colour FROM habits WHERE user_id = ?", (session["user_id"],)).fetchall()
        return render_template ("habit_edit.html", habits=habits)



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
        return render_template("login.html", greeting=True)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return render_template("login.html", greeting=True)


@app.route("/reflect", methods=["GET", "POST"])
def reflect():
    """Renders reflection page"""
    db = get_db()

    if request.method == "POST":
        try:
            db.execute("INSERT INTO reflections (user_id, title, date, content) VALUES (?, ?, ?, ?)", 
                       (session["user_id"], request.form.get("title"), request.form.get("date"), request.form.get("content")))
        except sqlite3.IntegrityError:
            return apology("something went wrong saving this reflection")

        db.commit()
        return apology("Reflection save successful!", error="success")
    else:
        reflections = db.execute("SELECT * FROM reflections WHERE user_id = ? ORDER BY date DESC", (session["user_id"],)).fetchall()
        return render_template("reflection.html", reflections=reflections)


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
        except sqlite3.IntegrityError:  # good practice to define the error so that it is easier to debug
            return apology("username already taken")
        
        db.commit() # as I am not using cs50 training wheels anymore, anytime I need to commit something to server files I need to do commit()
        return redirect("/")
    else:
        # renders my register template if user did not click "register" button
        return render_template("register.html", greeting=True)


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/timeline")
@login_required
def timeline():
    CELL_WIDTH = 32   # px per day column
    LABEL_WIDTH = 140 # px for the sticky habit-name column
    db = get_db()
    user_id = session["user_id"]

    habits = [dict(r) for r in db.execute(
        "SELECT id, habit, start_date, end_date, colour FROM habits WHERE user_id = ?",
        (user_id,)
    ).fetchall()]

    logs = [dict(r) for r in db.execute(
        """SELECT habit_logs.habit_id, habit_logs.completed_date
           FROM habit_logs
           JOIN habits ON habit_logs.habit_id = habits.id
           WHERE habits.user_id = ?""",
        (user_id,)
    ).fetchall()]

    reflections = [dict(r) for r in db.execute(
        "SELECT date, title, content FROM reflections WHERE user_id = ?",
        (user_id,)
    ).fetchall()]

    if not habits:
        # Nothing to plot yet — avoid crashing on min()/max() of an empty list
        return render_template("timeline.html", habits=[], date_headers=[], reflection_row=[],
                                cell_width=CELL_WIDTH, label_width=LABEL_WIDTH)

    # Find the earliest and latest date across ALL sources, so the grid covers everything
    all_dates = []
    for h in habits:
        all_dates += [date.fromisoformat(h["start_date"]), date.fromisoformat(h["end_date"])]
    for l in logs:
        all_dates.append(date.fromisoformat(l["completed_date"]))
    for r in reflections:
        all_dates.append(date.fromisoformat(r["date"]))

    min_date, max_date = min(all_dates), max(all_dates)

    # Build one entry per calendar day, inclusive of both ends
    dates = []
    cursor = min_date
    while cursor <= max_date:
        dates.append(cursor)
        cursor += timedelta(days=1)

    print("dates found:", len(dates), "min:", min_date, "max:", max_date)

    # A set of (habit_id, date) pairs, for O(1) "was this completed?" lookups per cell
    completed_lookup = {(l["habit_id"], l["completed_date"]) for l in logs}
    reflection_lookup = {r["date"]: r for r in reflections}

    date_headers = [{
        "day": d.day,
        # Only print a month label on the 1st of the month, or the very first column —
        # avoids repeating "Jan" under every single day
        "month_label": d.strftime("%b") if d.day == 1 or d == min_date else None,
    } for d in dates]

    for h in habits:
        start = date.fromisoformat(h["start_date"])
        end = date.fromisoformat(h["end_date"])
        cells = []
        for d in dates:
            active = start <= d <= end
            completed = active and (h["id"], d.isoformat()) in completed_lookup
            cells.append({"active": active, "completed": completed})
        h["cells"] = cells  # one cell dict per day, aligned to `dates`

    reflection_row = [{
        "has_reflection": d.isoformat() in reflection_lookup,
        "title": reflection_lookup.get(d.isoformat(), {}).get("title", ""),
    } for d in dates]

    return render_template(
        "timeline.html",
        habits=habits,
        date_headers=date_headers,
        reflection_row=reflection_row,
        cell_width=CELL_WIDTH,
        label_width=LABEL_WIDTH,
    )
    

# remove this when shipping
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, port=5000)
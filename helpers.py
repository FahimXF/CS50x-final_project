from flask import redirect, render_template, request, session
from functools import wraps
from datetime import date, datetime
import json
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tracker.db")


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


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

# Custom Jinja filter to calculate the difference in days
def days_until(target_date_str):
    today = date.today()
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        delta = target_date - today
        return delta.days
    except ValueError:
        return 0
    
def get_existing_todos(user_id):
    try:
        result = db.execute("SELECT todos FROM students WHERE id = ?", user_id)
        if result and result[0]["todos"]:
            return json.loads(result[0]["todos"])
        return []
    except Exception as e:
        print(f"Error retrieving todos: {e}")
        return []
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import re

from helpers import apology, login_required

exams = ["quiz1", "quiz2", "quiz3", "quiz4", "midterm"]

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tracker.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    return render_template("index.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("id"):
            return apology("must provide id", 400)
        if not request.form.get("name"):
            return apology("must provide name", 400)
        if not request.form.get("password"):
            return apology("must provide password", 400)
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 400)
        if not request.form.get("semester"):
            return apology("must provide semester", 400)
        if not (request.form.get("id").isdigit() or request.form.get("semester").isdigit()):
            return apology("id must be a number", 400)
        
        subjects = request.form.getlist("subject[]")
        credits = request.form.getlist("credit[]")
        
        if not subjects or not credits or len(subjects) != len(credits):
            return apology("must provide subjects and credits", 400)
        
        try:
            db.execute("INSERT INTO students (id, name, hash, semester,subjects) VALUES (?, ?, ?, ?,?)", 
                       request.form.get("id"), 
                       request.form.get("name"), 
                       generate_password_hash(request.form.get("password")), 
                       request.form.get("semester"),
                       json.dumps(subjects))
        except ValueError:
            return apology("id already exists", 400)
        
        student_id = request.form.get("id")
        
        for subject, credit in zip(subjects, credits):
            sanitized_subject = re.sub(r'\W+', '_', subject)  # Replace non-alphanumeric characters with underscores
            try:
                db.execute(f"CREATE TABLE IF NOT EXISTS {sanitized_subject} (student_id INTEGER, quiz1 REAL, quiz2 REAL, quiz3 REAL, quiz4 REAL, midterm REAL, missing_attendance INTEGER DEFAULT 0, credit INTEGER, FOREIGN KEY(student_id) REFERENCES students(id))")
                db.execute(f"INSERT INTO {sanitized_subject} (student_id, credit) VALUES (?, ?)", student_id, credit)
            except ValueError:
                return apology("error creating table or inserting data", 400)
        
        rows = db.execute("SELECT * FROM students WHERE id = ?", student_id)
        session["user_id"] = rows[0]["id"]
        flash("Registration Successful")

        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure id was submitted
        if not request.form.get("id"):
            return apology("must provide id", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for id
        rows = db.execute(
            "SELECT * FROM students WHERE id = ?", request.form.get("id")
        )

        # Ensure id exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid id and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/marks", methods=["GET", "POST"])
@login_required
def marks():
    if request.method == "POST":
        student_id = session["user_id"]
        subject = request.form.get("subject")
        sanitized_subject = re.sub(r'\W+', '_', subject)
        subjects_json = db.execute("SELECT subjects FROM students WHERE id = ?", student_id)[0]["subjects"]
        subjects = json.loads(subjects_json)
        try :
            db.execute(f"UPDATE {sanitized_subject} SET {request.form.get('exam')} = ? WHERE student_id = ?", request.form.get("marks"), session["user_id"])
        except ValueError:
            return apology("error updating marks", 400)
        return render_template("marks.html", exams=exams, subjects=subjects)
    
    student_id = session["user_id"]
    subjects_json = db.execute("SELECT subjects FROM students WHERE id = ?", student_id)[0]["subjects"]
    subjects = json.loads(subjects_json)
    return render_template("marks.html", subjects=subjects,exams=exams)

@app.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():
    if request.method == "POST":
        student_id = session["user_id"]
        subject = request.form.get("subject")
        sanitized_subject = re.sub(r'\W+', '_', subject)
        subjects_json = db.execute("SELECT subjects FROM students WHERE id = ?", student_id)[0]["subjects"]
        subjects = json.loads(subjects_json)
        try :
            db.execute(f"UPDATE {sanitized_subject} SET missing_attendance = missing_attendance + ? WHERE student_id = ?", request.form.get("attendance"), session["user_id"])
        except ValueError:
            return apology("error updating attendance", 400)
        return render_template("attendance.html", subjects=subjects)
    
    student_id = session["user_id"]
    subjects_json = db.execute("SELECT subjects FROM students WHERE id = ?", student_id)[0]["subjects"]
    subjects = json.loads(subjects_json)
    return render_template("attendance.html", subjects=subjects)
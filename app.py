import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session,url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime,date
import re

from helpers import apology, login_required, days_until


exams = ["quiz1", "quiz2", "quiz3", "quiz4", "midterm"]

# Configure application
app = Flask(__name__)

# Register the custom filter with Jinja
app.jinja_env.filters['days_until'] = days_until

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
    student_id = session["user_id"]
    subjects_json = db.execute("SELECT subjects FROM students WHERE id = ?", student_id)[0]["subjects"]
    subjects = json.loads(subjects_json)
    subjects_info = []
    for subject in subjects:
        sanitized_subject = re.sub(r'\W+', '_', subject)
        subject_info = db.execute(f"SELECT quiz1, quiz2, quiz3, quiz4, midterm, missing_attendance, credit FROM {sanitized_subject} WHERE student_id = ?", student_id)[0]
        subjects_info.append({"name": subject, "info": subject_info})    

    return render_template("index.html", subjects=subjects_info)



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
                db.execute(f"CREATE TABLE IF NOT EXISTS {sanitized_subject} (student_id INTEGER, quiz1 REAL DEFAULT 0, quiz2 REAL DEFAULT 0, quiz3 REAL DEFAULT 0, quiz4 REAL DEFAULT 0, midterm REAL DEFAULT 0, missing_attendance INTEGER DEFAULT 0, credit INTEGER, FOREIGN KEY(student_id) REFERENCES students(id))")
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


@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    if request.method =="POST":
        goals = request.form.getlist("goal[]")
        times=request.form.getlist("time[]")
        if not goals or not times or len(goals) != len(times):
            return apology("must provide goals and times", 400)
        goals_times = []
        for goal, time in zip(goals, times):
            goals_times.append({"goal": goal, "time": time})
    
        # Retrieve existing goals from the database
        existing_goals_json = db.execute("SELECT goals FROM students WHERE id = ?", session["user_id"])[0]["goals"]

        if existing_goals_json:
            existing_goals = json.loads(existing_goals_json)
        else:
            existing_goals = []

        # Merge the new goals with the existing goals
        merged_goals = existing_goals + goals_times

        # Convert the merged goals back to a JSON string
        merged_goals_json = json.dumps(merged_goals)
        
    
        # Store the JSON string in the database
        try:
            db.execute("UPDATE students SET goals = ? WHERE id = ?", merged_goals_json, session["user_id"])
        except ValueError:
            return apology("error inserting goals", 400)
        
        return render_template("goals.html",goals=merged_goals)
    
    goals_json = db.execute("SELECT goals FROM students WHERE id = ?", session["user_id"])[0]["goals"]
    if goals_json:
        goals=json.loads(goals_json)
    else:
        goals=[]
    return render_template("goals.html",goals=goals)


@app.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    if request.method == "POST":
        if 'task_id' in request.form:
            task_id = int(request.form.get("task_id"))
            # Retrieve existing todos from the database
            existing_todos_json = db.execute("SELECT todos FROM students WHERE id = ?", session["user_id"])[0]["todos"]
            existing_todos = json.loads(existing_todos_json) if existing_todos_json else []
            # Remove the task with the given task_id
            existing_todos = [task for task in existing_todos if task["id"] != task_id]
            # Convert the updated todos back to a JSON string
            updated_todos_json = json.dumps(existing_todos)
            # Store the JSON string in the database
            db.execute("UPDATE students SET todos = ? WHERE id = ?", updated_todos_json, session["user_id"])
        else:
            todos = request.form.getlist("todo[]")
            time_limits = request.form.getlist("time_limit[]")
            if not todos:
                return apology("must provide todos", 400)
            if not time_limits:
                return apology("must provide time limits", 400)
            if len(todos) != len(time_limits):
                return apology("todos and time limits must be of the same length", 400)
            todos_list = []
            for todo, time_limit in zip(todos, time_limits):
                todos_list.append({"id": len(todos_list), "todo": todo, "done": False, "time_limit": time_limit})

            # Retrieve existing todos from the database
            existing_todos_json = db.execute("SELECT todos FROM students WHERE id = ?", session["user_id"])[0]["todos"]

            if existing_todos_json:
                existing_todos = json.loads(existing_todos_json)
            else:
                existing_todos = []

            # Merge the new todos with the existing todos
            merged_todos = existing_todos + todos_list

            # Convert the merged todos back to a JSON string
            merged_todos_json = json.dumps(merged_todos)

            # Store the JSON string in the database
            db.execute("UPDATE students SET todos = ? WHERE id = ?", merged_todos_json, session["user_id"])

        return redirect(url_for("todo"))

    tasks = db.execute("SELECT todos FROM students WHERE id = ?", session["user_id"])
    if tasks and tasks[0]["todos"]:
        tasks = json.loads(tasks[0]["todos"])
        # Format the time_limit to show only the date
        """for task in tasks:
            if task["time_limit"]:
                try:
                    task["time_limit"] = datetime.strptime(task["time_limit"], "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d")
                except ValueError:
                    # If the format is already %Y-%m-%d, no need to change it
                    pass"""
    else:
        tasks = []
    return render_template("todo.html", tasks=tasks)



    



        


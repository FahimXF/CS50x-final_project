import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session,url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import re

from helpers import apology, login_required, days_until, get_existing_todos
from leetcode import problems


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

    goals_json = db.execute("SELECT goals FROM students WHERE id = ?", session["user_id"])[0]["goals"]
    tasks_json = db.execute("SELECT todos FROM students WHERE id = ?", session["user_id"])   
    if goals_json:
        goals=json.loads(goals_json)
    else:
        goals=[] 

    if tasks_json and tasks_json[0]["todos"]:
        tasks = json.loads(tasks_json[0]["todos"])
    else:
        tasks = []
    

    return render_template("index.html", subjects=subjects_info, goals=goals,tasks=tasks,problems=problems)



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
            return apology("id or semester must be a number", 400)
        if request.form.get("semester") not in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            return apology("semester must be between 1 and 8", 400)
        
        
        subjects = request.form.getlist("subject[]")
        credits = request.form.getlist("credit[]")

        for credit in credits:
            if int(credit) <= 0 or int(credit) > 3 or not credit.isdigit() :
                return apology("Invalid Credit", 400)
        
        if not subjects or not credits or len(subjects) != len(credits):
            return apology("must provide subjects and credits", 400)
        
        try:
            db.execute("INSERT INTO students (id, name, hash, semester,subjects) VALUES (?, ?, ?, ?,?)", 
                       request.form.get("id"), 
                       request.form.get("name"), 
                       generate_password_hash(request.form.get("password")), 
                       request.form.get("semester"),
                       json.dumps(sorted(subjects)))
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

@app.route("/add_marks", methods=["GET", "POST"])
@login_required
def add_marks():
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
        return render_template("add_marks.html", exams=exams, subjects=subjects)
    
    student_id = session["user_id"]
    subjects_json = db.execute("SELECT subjects FROM students WHERE id = ?", student_id)[0]["subjects"]
    subjects = json.loads(subjects_json)
    return render_template("add_marks.html", subjects=subjects,exams=exams)

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
    user_id = session["user_id"]
    
    if request.method == "POST":
        goals = request.form.getlist("goal[]")
        times = request.form.getlist("time[]")
        
        # Filter out empty goals and times
        goals_times = [{"goal": goal, "time": time} for goal, time in zip(goals, times) if goal and time]
        
        if not goals_times:
            return apology("must provide valid goals and times", 400)
        
        # Retrieve existing goals from the database
        try:
            existing_goals_json = db.execute("SELECT goals FROM students WHERE id = ?", user_id)[0]["goals"]
            existing_goals = json.loads(existing_goals_json) if existing_goals_json else []
        except Exception as e:
            print(f"Error retrieving goals: {e}")
            return apology("error retrieving goals", 400)
        
        # Merge the new goals with the existing goals
        merged_goals = existing_goals + goals_times
        
        # Convert the merged goals back to a JSON string
        merged_goals_json = json.dumps(merged_goals)
        
        # Store the JSON string in the database
        try:
            db.execute("UPDATE students SET goals = ? WHERE id = ?", merged_goals_json, user_id)
        except Exception as e:
            print(f"Error updating goals: {e}")
            return apology("error inserting goals", 400)
        
        return redirect(url_for("goals"))
    
    try:
        goals_json = db.execute("SELECT goals FROM students WHERE id = ?", user_id)[0]["goals"]
        goals = json.loads(goals_json) if goals_json else []
    except Exception as e:
        print(f"Error retrieving goals: {e}")
        goals = []
    
    return render_template("goals.html", goals=goals)


@app.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    user_id = session["user_id"]
    
    if request.method == "POST":
        if 'task_id' in request.form:
            task_id = int(request.form.get("task_id"))
            existing_todos = get_existing_todos(user_id)
            existing_todos = [task for task in existing_todos if task["id"] != task_id]
            updated_todos_json = json.dumps(existing_todos)
            db.execute("UPDATE students SET todos = ? WHERE id = ?", updated_todos_json, user_id)
        else:
            todos = request.form.getlist("todo[]")
            time_limits = request.form.getlist("time_limit[]")
            if not todos:
                return apology("must provide todos", 400)
            if not time_limits:
                return apology("must provide time limits", 400)
            if len(todos) != len(time_limits):
                return apology("todos and time limits must be of the same length", 400)
            
            existing_todos = get_existing_todos(user_id)
            max_id = max([task["id"] for task in existing_todos], default=0)
            todos_list = [{"id": max_id + i + 1, "todo": todo, "done": False, "time_limit": time_limit} for i, (todo, time_limit) in enumerate(zip(todos, time_limits))]
            merged_todos = existing_todos + todos_list
            merged_todos_json = json.dumps(merged_todos)
            db.execute("UPDATE students SET todos = ? WHERE id = ?", merged_todos_json, user_id)

        return redirect(url_for("todo"))

    tasks = get_existing_todos(user_id)
    return render_template("todo.html", tasks=tasks)


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        id, old_password, new_password = request.form.get(
            "id"), request.form.get("old_password"), request.form.get("new_password")
        if not (id or old_password or new_password):
            return apology("Invalid Input")
        rows = db.execute(
            "SELECT * FROM students WHERE id = ?", request.form.get("id")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], old_password
        ):
            return apology("invalid username and/or password", 403)

        db.execute("UPDATE students SET hash = ? WHERE id =?",
                   generate_password_hash(new_password), id)
        flash("Password Change Successful")
        return redirect("/")

    return render_template("change_password.html")

@app.route("/add_subject", methods=["GET", "POST"])
@login_required
def add_subject():
    if request.method == "POST":
        if 'subject_id' in request.form:
            subject_id = int(request.form.get("subject_id"))
            student_id = session["user_id"]
            subjects_json = db.execute("SELECT subjects FROM students WHERE id = ?", student_id)[0]["subjects"]
            subjects = json.loads(subjects_json)
            subject = subjects[subject_id]
            sanitized_subject = re.sub(r'\W+', '_', subject)
            subjects.remove(subject)
            subjects.sort()
            db.execute("UPDATE students SET subjects = ? WHERE id = ?", json.dumps(subjects), student_id)
            db.execute(f"DELETE FROM {sanitized_subject} WHERE student_id = ?", student_id)
            flash("Subject Deleted Successfully")
            return redirect("/add_subject")
        else:
            student_id = session["user_id"]
            subject = request.form.get("subject")
            credit = request.form.get("credit")
            sanitized_subject = re.sub(r'\W+', '_', subject)
            try:
                db.execute(f"CREATE TABLE IF NOT EXISTS {sanitized_subject} (student_id INTEGER, quiz1 REAL DEFAULT 0, quiz2 REAL DEFAULT 0, quiz3 REAL DEFAULT 0, quiz4 REAL DEFAULT 0, midterm REAL DEFAULT 0, missing_attendance INTEGER DEFAULT 0, credit INTEGER, FOREIGN KEY(student_id) REFERENCES students(id))")
                db.execute(f"INSERT INTO {sanitized_subject} (student_id, credit) VALUES (?, ?)", student_id, credit)
            except ValueError:
                return apology("error creating table or inserting data", 400)
            
            subjects_json = db.execute("SELECT subjects FROM students WHERE id = ?", student_id)[0]["subjects"]
            subjects = json.loads(subjects_json)
            subjects.append(subject)
            subjects.sort()
            db.execute("UPDATE students SET subjects = ? WHERE id = ?", json.dumps(subjects), student_id)
            flash("Subject Added Successfully")
            return redirect("/add_subject")
    
    subjects_json = db.execute("SELECT subjects FROM students WHERE id = ?", session["user_id"])[0]["subjects"]
    subjects = json.loads(subjects_json) 
    subjects_with_ids = list(enumerate(subjects))
    
    return render_template("add_subject.html", subjects=subjects_with_ids)


    



        


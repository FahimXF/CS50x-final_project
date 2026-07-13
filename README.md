# TRACKR
#### Video Demo:  <https://youtu.be/_v_Rk44sjDA>
# TRACKR

> A personal academic tracker built specifically for students of **Islamic University of Technology (IUT)**.

TRACKR helps IUT students keep track of their academic performance, attendance, goals, and daily tasks throughout the semester. The grading calculations and attendance rules are designed according to the **IUT grading system**.

---

## Features

- 📊 Track quiz, midterm, and final exam marks
- 📈 Automatically calculate required final exam marks for an **A+**
- 📚 Manage subjects and credit hours
- ✅ Personal To-Do list with deadlines
- 🎯 Long-term Goals tracker
- ⚠ Attendance warning system
- 🔒 Secure password hashing
- 👤 Multi-user support

---

## Tech Stack

### Backend
- Python
- Flask

### Frontend
- HTML
- CSS
- Bootstrap
- JavaScript

### Database
- SQLite (`tracker.db`)

### Python Modules
- Flask
- Flask-Session
- CS50
- Werkzeug
- datetime
- json
- re

---

# Project Structure

```
TRACKR/
│
├── static/
├── templates/
├── tracker.db
├── app.py
├── helpers.py
├── requirements.txt
└── README.md
```

---

# Pages & Functionalities

## 1. Register

Allows new students to create an account by providing:

- Student ID
- Name
- Password
- Subjects
- Corresponding Credit Hours

### Features

- Register unlimited subjects
- Passwords are securely stored as hashes
- Input validation
- Prevents empty fields
- Prevents missing credit hour entries
- Error handling through the CS50 Finance apology page

All information is stored in the SQLite database.

---

## 2. Add Marks

Students can enter marks for every registered subject.

### Supported Exams

- Quiz 1
- Quiz 2
- Quiz 3
- Quiz 4
- Midterm

### Features

- Subject selection from registered courses
- Marks stored in database
- Required fields prevent empty submissions

---

## 3. Missing Attendance

Track missed classes for each course.

### Features

- Multiple submissions accumulate attendance misses
- Stores attendance records in database
- Automatically generates warnings

### Attendance Rules

| Missed Attendance | Consequence |
|------------------|-------------|
| >2 | Warning displayed |
| >3 | Attendance marks deducted |
| ≥6 | Risk of being barred from Midterm/Final |

Warnings appear on the dashboard automatically.

---

## 4. Add / Remove Subjects

Manage subjects after registration.

### Features

- Remove mistakenly added subjects
- Add new subjects
- Assign corresponding credit hours
- Useful when progressing to a new semester

---

## 5. TODO

Simple task management page.

### Features

- Add tasks
- Set due dates
- Mark tasks as completed
- Completed tasks are removed from the page and database

---

## 6. Goals

Track long-term academic goals.

### Features

- Add multiple goals
- Assign deadlines
- Goals remain until manually removed

Unlike TODOs, goals are intended for long-term planning and therefore do not include a completion checkbox.

---

## 7. Dashboard (Index)

The main dashboard combines all academic information in one place.

### Marks Section

For every subject, the dashboard displays:

- Quiz 1–4 marks
- Best 3 quiz scores (automatically selected)
- Midterm marks
- Missing attendance
- Required Final Exam marks for an **A+**

The required final mark is calculated automatically based on:

- Credit hour
- Best three quizzes
- Midterm marks
- IUT grading policy

Each subject has its own table.

### Sidebar

Displays:

- Attendance alerts
- Current TODO list
- Current Goals

---

## 8. Change Password

Allows users to securely update their password.

### Inputs

- Student ID
- Old Password
- New Password

The previous password hash is replaced with the hash of the new password after verification.

---

# Automatic Calculations

TRACKR automatically performs the following calculations:

- Selects the best **3 out of 4 quizzes**
- Calculates current obtained marks
- Calculates required Final Exam marks for an **A+**
- Tracks attendance violations
- Generates attendance warnings

---

# Database

The application stores:

- User information
- Password hashes
- Registered subjects
- Credit hours
- Quiz marks
- Midterm marks
- Attendance records
- TODO items
- Goals

SQLite is used as the database backend.

---

# Security

- Passwords are never stored in plain text.
- Password hashing is handled using **Werkzeug**.
- Server-side validation prevents invalid input.

---

# Future Improvements

- Final exam mark entry
- CGPA calculator
- Semester-wise record history
- GPA trend visualization
- Course-wise statistics
- Data export (PDF/Excel)
- Email reminders for deadlines
- Responsive mobile interface

---

# Screenshots

TODO

# Installation

```bash
git clone https://github.com/yourusername/TRACKR.git

cd TRACKR

pip install -r requirements.txt

flask run
```

---

# License

This project was developed as an academic project.

---

# Author

**Shahriar Fahim**

Electrical and Electronic Engineering (EEE)

Islamic University of Technology (IUT)

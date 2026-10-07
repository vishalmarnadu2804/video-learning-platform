"""
Video Learning Platform - Main Flask Application
College MWP (Mobile & Web Programming) Mini Project
"""

import re
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    flash,
    session
)
from werkzeug.security import generate_password_hash, check_password_hash
import database

app = Flask(__name__)
# Secret key for secure Flask session management
app.secret_key = "video_learning_platform_academic_secret_key_mwp_mini_project"


# -----------------------------------------------------------------------------
# CLI / Setup Hook: Initialize database automatically on startup
# -----------------------------------------------------------------------------
with app.app_context():
    database.init_db()


# -----------------------------------------------------------------------------
# Authentication Decorator & Context Processor
# -----------------------------------------------------------------------------

def login_required(f):
    """Decorator to protect routes from unauthenticated student access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "student_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_user():
    """Injects user authentication status and student name into all Jinja templates."""
    return {
        "is_logged_in": "student_id" in session,
        "student_id": session.get("student_id"),
        "student_name": session.get("student_name"),
        "student_email": session.get("student_email")
    }


# -----------------------------------------------------------------------------
# Authentication Routes (Sign Up, Login, Logout)
# -----------------------------------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Student Sign Up: validates form fields, prevents duplicates, hashes password."""
    if "student_id" in session:
        return redirect(url_for("lessons"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # 1. Validation
        if not name or not email or not password or not confirm_password:
            flash("All fields are required. Please fill out the entire registration form.", "danger")
            return render_template("signup.html", name=name, email=email)

        # Basic email format check
        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "danger")
            return render_template("signup.html", name=name, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("signup.html", name=name, email=email)

        if password != confirm_password:
            flash("Passwords do not match. Please verify your passwords.", "danger")
            return render_template("signup.html", name=name, email=email)

        # 2. Check for duplicate email
        existing_student = database.get_student_by_email(email)
        if existing_student:
            flash("An account with this email already exists. Please log in instead.", "danger")
            return render_template("signup.html", name=name, email=email)

        # 3. Securely hash password using Werkzeug and save student
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        database.create_student(name, email, password_hash)

        flash("Registration successful! Please log in with your credentials.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Student Login: verifies email & password_hash and establishes session."""
    if "student_id" in session:
        return redirect(url_for("lessons"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        next_page = request.args.get("next") or request.form.get("next")

        if not email or not password:
            flash("Please provide both email and password.", "danger")
            return render_template("login.html", email=email), 400

        student = database.get_student_by_email(email)
        if not student or not check_password_hash(student["password_hash"], password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html", email=email), 401

        # Establish session
        session["student_id"] = student["id"]
        session["student_name"] = student["name"]
        session["student_email"] = student["email"]

        flash(f"Welcome, {student['name']}!", "success")

        # Safely handle redirection
        if next_page and next_page.startswith("/") and not next_page.startswith("//"):
            return redirect(next_page)
        return redirect(url_for("lessons"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Destroys student session and redirects to login."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


# -----------------------------------------------------------------------------
# General & Course Routes
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    """Home page: Platform overview, Start Learning CTA, and key features."""
    return render_template("index.html")


@app.route("/lessons")
@login_required
def lessons():
    """Lessons page: Displays exactly the five foundational lessons and student progress."""
    student_id = session["student_id"]
    all_lessons = database.get_all_lessons(student_id=student_id)
    overview = database.get_student_progress_overview(student_id=student_id)
    return render_template("lessons.html", lessons=all_lessons, overview=overview)


# Backward compatibility redirects for legacy /courses endpoints
@app.route("/courses")
@login_required
def courses_redirect():
    return redirect(url_for("lessons"))


@app.route("/course/<int:course_id>")
@login_required
def course_details_redirect(course_id):
    return redirect(url_for("lessons"))


@app.route("/lesson/<int:lesson_number>")
@login_required
def lesson_view(lesson_number):
    """
    Video Lesson page: Responsive 16:9 YouTube video player, lesson info,
    Previous/Next navigation, Back to Course, and Mark as Completed button.
    """
    student_id = session["student_id"]
    lesson = database.get_lesson_by_number(lesson_number, student_id=student_id)

    if not lesson:
        return render_template(
            "404.html",
            error_title="Lesson Not Found",
            error_message=f"Lesson #{lesson_number} does not exist. The platform contains exactly 5 lessons (Lessons 1 to 5)."
        ), 404

    all_lessons = database.get_all_lessons(student_id=student_id)

    return render_template(
        "lesson.html",
        lesson=lesson,
        all_lessons=all_lessons
    )


# Backward compatibility redirect for legacy route
@app.route("/course/<int:course_id>/lesson/<int:lesson_id>")
@login_required
def legacy_lesson_redirect(course_id, lesson_id):
    # Map lesson_id safely to lesson_number 1-5
    target_number = max(1, min(5, lesson_id))
    return redirect(url_for("lesson_view", lesson_number=target_number))


@app.route("/lesson/<int:lesson_number>/complete", methods=["POST"])
@login_required
def complete_lesson_form(lesson_number):
    """
    Standard HTML Form POST submission fallback for marking/unmarking a lesson complete.
    Updates SQLite and redirects back with confirmation flash.
    """
    student_id = session["student_id"]
    res = database.toggle_lesson_completion(lesson_number, student_id=student_id)

    if not res.get("success"):
        flash("Could not update lesson progress.", "danger")
    else:
        status_text = "completed" if res["is_completed"] else "marked as incomplete"
        flash(f"Lesson {lesson_number} successfully {status_text}!", "success")

    action = request.form.get("action")
    next_num = request.form.get("next_lesson_number")
    if action == "mark_and_next" and next_num:
        return redirect(url_for("lesson_view", lesson_number=int(next_num)))

    return redirect(url_for("lesson_view", lesson_number=lesson_number))


@app.route("/api/lesson/<int:lesson_number>/toggle", methods=["POST"])
def api_toggle_lesson(lesson_number):
    """
    AJAX API endpoint to toggle lesson completion in SQLite without full page reload.
    Ensures student authentication and updates per-student progress.
    """
    if "student_id" not in session:
        return jsonify({"success": False, "error": "Authentication required. Please log in."}), 401

    student_id = session["student_id"]
    res = database.toggle_lesson_completion(lesson_number, student_id=student_id)

    if not res.get("success"):
        return jsonify(res), 404
    return jsonify(res), 200


@app.route("/progress")
@login_required
def progress():
    """My Progress page: Dynamically calculates student's completed lessons out of 5."""
    student_id = session["student_id"]
    overview = database.get_student_progress_overview(student_id=student_id)
    return render_template("progress.html", overview=overview)


@app.route("/progress/reset", methods=["POST"])
@login_required
def reset_progress():
    """Allows resetting progress data for the logged-in student (for demo/testing)."""
    student_id = session["student_id"]
    database.reset_student_progress(student_id=student_id)
    flash("Your learning progress has been reset.", "info")
    return redirect(url_for("progress"))


@app.route("/about")
def about():
    """About page: Project purpose, architecture, SQLite schema design, and viva highlights."""
    return render_template("about.html")


# -----------------------------------------------------------------------------
# Error Handlers
# -----------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        "404.html",
        error_title="Page Not Found",
        error_message="The page or resource you are looking for does not exist."
    ), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template(
        "404.html",
        error_title="Internal Server Error",
        error_message="An unexpected server error occurred. Please try again."
    ), 500


if __name__ == "__main__":
    print("Starting Video Learning Platform on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)

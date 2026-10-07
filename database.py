"""
Database configuration and data access layer for Video Learning Platform.
Uses standard Python sqlite3 with automatic schema initialization,
user authentication, and dynamic student-specific progress tracking.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "platform.db")

# The 5 core foundational lessons with verified, public, embeddable YouTube educational videos
DEFAULT_LESSONS = [
    {
        "lesson_number": 1,
        "title": "Introduction to Python",
        "description": "Learn the fundamentals of Python programming, syntax basics, variables, data types, and setting up your first Python script.",
        "video_id": "_uQrJ0TkZlc",
        "embed_url": "https://www.youtube.com/embed/_uQrJ0TkZlc",
        "duration": "15 mins",
        "summary_notes": "Python is a high-level, interpreted programming language known for clean readability. Key takeaway: whitespace and indentation define code blocks."
    },
    {
        "lesson_number": 2,
        "title": "HTML Basics",
        "description": "Master the structural backbone of the web: semantic HTML elements, headings, paragraphs, lists, forms, and document structure.",
        "video_id": "UB1O30fR-EE",
        "embed_url": "https://www.youtube.com/embed/UB1O30fR-EE",
        "duration": "20 mins",
        "summary_notes": "HTML (HyperText Markup Language) defines web page structure. Always prefer semantic elements (header, nav, main, section, footer) for accessibility."
    },
    {
        "lesson_number": 3,
        "title": "CSS Basics",
        "description": "Style modern web pages with CSS selectors, colors, typography, spacing, flexbox layouts, borders, and the CSS box model.",
        "video_id": "yfoY53QXEnI",
        "embed_url": "https://www.youtube.com/embed/yfoY53QXEnI",
        "duration": "20 mins",
        "summary_notes": "CSS (Cascading Style Sheets) controls visual presentation. The Box Model dictates layout: Content + Padding + Border + Margin."
    },
    {
        "lesson_number": 4,
        "title": "JavaScript Basics",
        "description": "Add dynamic interactivity to websites: JavaScript variables, data types, functions, DOM manipulation, and browser click event listeners.",
        "video_id": "W6NZfCO5SIk",
        "embed_url": "https://www.youtube.com/embed/W6NZfCO5SIk",
        "duration": "25 mins",
        "summary_notes": "JavaScript provides client-side interactivity by listening to browser events like 'click' and dynamically updating DOM elements without page reloads."
    },
    {
        "lesson_number": 5,
        "title": "SQL/Database Basics",
        "description": "Understand relational database management systems (RDBMS), table structures, primary/foreign keys, and essential SQL queries (SELECT, INSERT, UPDATE, DELETE).",
        "video_id": "HXV3zeQKqGY",
        "embed_url": "https://www.youtube.com/embed/HXV3zeQKqGY",
        "duration": "25 mins",
        "summary_notes": "SQL (Structured Query Language) is the standard declarative language for relational databases like SQLite. Primary keys ensure unique rows."
    }
]


def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database with row_factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """
    Initializes database tables (students, lessons, progress) and seeds
    the 5 default lessons without creating duplicates on restarts.
    Safely upgrades/replaces old incompatible schema if present.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if existing tables are from an older incompatible schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lessons'")
    lessons_table_exists = cursor.fetchone() is not None

    if lessons_table_exists:
        # Check if lessons has 'lesson_number' column
        cursor.execute("PRAGMA table_info(lessons)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "lesson_number" not in columns:
            # Old schema detected, drop outdated tables to recreate cleanly
            cursor.execute("DROP TABLE IF EXISTS progress")
            cursor.execute("DROP TABLE IF EXISTS lessons")
            cursor.execute("DROP TABLE IF EXISTS courses")

    # 1. Students Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Lessons Table (Exactly 5 lessons total)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_number INTEGER UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            video_id TEXT NOT NULL,
            embed_url TEXT NOT NULL,
            duration TEXT NOT NULL,
            summary_notes TEXT
        )
    """)

    # 3. Student Progress Table (Per-student tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            is_completed INTEGER DEFAULT 1,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, lesson_id),
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE
        )
    """)

    # 4. Seed the 5 default lessons if not already present
    for lesson in DEFAULT_LESSONS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO lessons 
            (lesson_number, title, description, video_id, embed_url, duration, summary_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lesson["lesson_number"],
                lesson["title"],
                lesson["description"],
                lesson["video_id"],
                lesson["embed_url"],
                lesson["duration"],
                lesson["summary_notes"]
            )
        )
        # Also ensure embed_url and video_id are updated in case old ones were stored
        cursor.execute(
            """
            UPDATE lessons 
            SET title = ?, description = ?, video_id = ?, embed_url = ?, duration = ?, summary_notes = ?
            WHERE lesson_number = ?
            """,
            (
                lesson["title"],
                lesson["description"],
                lesson["video_id"],
                lesson["embed_url"],
                lesson["duration"],
                lesson["summary_notes"],
                lesson["lesson_number"]
            )
        )

    conn.commit()
    conn.close()


# -------------------------------------------------------------
# Student Authentication Queries
# -------------------------------------------------------------

def get_student_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetches a student by email (case-insensitive)."""
    if not email:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT * FROM students WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))",
        (email,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_by_id(student_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a student by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_student(name: str, email: str, password_hash: str) -> int:
    """Inserts a new student record into SQLite. Returns student ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, email, password_hash) VALUES (?, ?, ?)",
        (name.strip(), email.strip().lower(), password_hash)
    )
    conn.commit()
    student_id = cursor.lastrowid
    conn.close()
    return student_id


# -------------------------------------------------------------
# Lessons & Dynamic Progress Queries
# -------------------------------------------------------------

def get_all_lessons(student_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Fetches all 5 lessons ordered by lesson_number.
    If student_id is provided, includes completion status specific to that student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if student_id:
        query = """
            SELECT 
                l.id,
                l.lesson_number,
                l.title,
                l.description,
                l.video_id,
                l.embed_url,
                l.duration,
                l.summary_notes,
                COALESCE(p.is_completed, 0) AS is_completed,
                p.completed_at
            FROM lessons l
            LEFT JOIN progress p ON l.id = p.lesson_id AND p.student_id = ?
            ORDER BY l.lesson_number ASC
        """
        rows = cursor.execute(query, (student_id,)).fetchall()
    else:
        query = """
            SELECT 
                l.id,
                l.lesson_number,
                l.title,
                l.description,
                l.video_id,
                l.embed_url,
                l.duration,
                l.summary_notes,
                0 AS is_completed,
                NULL AS completed_at
            FROM lessons l
            ORDER BY l.lesson_number ASC
        """
        rows = cursor.execute(query).fetchall()

    conn.close()
    return [dict(row) for row in rows]


def get_lesson_by_number(lesson_number: int, student_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Fetches details for a specific lesson by lesson_number (1 to 5),
    including completion status for the student, prev_lesson, and next_lesson.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if student_id:
        query = """
            SELECT 
                l.id,
                l.lesson_number,
                l.title,
                l.description,
                l.video_id,
                l.embed_url,
                l.duration,
                l.summary_notes,
                COALESCE(p.is_completed, 0) AS is_completed,
                p.completed_at
            FROM lessons l
            LEFT JOIN progress p ON l.id = p.lesson_id AND p.student_id = ?
            WHERE l.lesson_number = ?
        """
        row = cursor.execute(query, (student_id, lesson_number)).fetchone()
    else:
        query = """
            SELECT 
                l.id,
                l.lesson_number,
                l.title,
                l.description,
                l.video_id,
                l.embed_url,
                l.duration,
                l.summary_notes,
                0 AS is_completed,
                NULL AS completed_at
            FROM lessons l
            WHERE l.lesson_number = ?
        """
        row = cursor.execute(query, (lesson_number,)).fetchone()

    if not row:
        conn.close()
        return None

    lesson = dict(row)

    # Previous lesson (lesson_number - 1)
    prev_row = cursor.execute(
        "SELECT lesson_number, title FROM lessons WHERE lesson_number = ?",
        (lesson_number - 1,)
    ).fetchone()

    # Next lesson (lesson_number + 1)
    next_row = cursor.execute(
        "SELECT lesson_number, title FROM lessons WHERE lesson_number = ?",
        (lesson_number + 1,)
    ).fetchone()

    conn.close()

    lesson["prev_lesson"] = dict(prev_row) if prev_row else None
    lesson["next_lesson"] = dict(next_row) if next_row else None

    return lesson


def toggle_lesson_completion(lesson_number: int, student_id: int) -> Dict[str, Any]:
    """
    Toggles completion state of a lesson for a specific student in SQLite.
    If no record exists, inserts with is_completed = 1.
    If record exists, flips 0/1.
    Returns the new state and updated overall progress out of 5 lessons.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Look up lesson id
    lesson_row = cursor.execute(
        "SELECT id, lesson_number FROM lessons WHERE lesson_number = ?",
        (lesson_number,)
    ).fetchone()

    if not lesson_row:
        conn.close()
        return {"success": False, "error": f"Lesson {lesson_number} not found"}

    lesson_id = lesson_row["id"]

    # Check current progress record for this student
    prog = cursor.execute(
        "SELECT is_completed FROM progress WHERE student_id = ? AND lesson_id = ?",
        (student_id, lesson_id)
    ).fetchone()

    if prog is None:
        new_status = 1
        cursor.execute(
            """
            INSERT INTO progress (student_id, lesson_id, is_completed, completed_at)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            """,
            (student_id, lesson_id)
        )
    else:
        new_status = 0 if prog["is_completed"] == 1 else 1
        cursor.execute(
            """
            UPDATE progress 
            SET is_completed = ?, completed_at = CURRENT_TIMESTAMP
            WHERE student_id = ? AND lesson_id = ?
            """,
            (new_status, student_id, lesson_id)
        )

    conn.commit()

    # Calculate overall progress for this student across all 5 lessons
    total_lessons = cursor.execute("SELECT COUNT(*) AS count FROM lessons").fetchone()["count"]
    completed_lessons = cursor.execute(
        "SELECT COUNT(*) AS count FROM progress WHERE student_id = ? AND is_completed = 1",
        (student_id,)
    ).fetchone()["count"]

    conn.close()

    progress_pct = int(round((completed_lessons / total_lessons * 100))) if total_lessons > 0 else 0

    return {
        "success": True,
        "lesson_number": lesson_number,
        "is_completed": bool(new_status),
        "completed_count": completed_lessons,
        "total_count": total_lessons,
        "progress_pct": progress_pct
    }


def get_student_progress_overview(student_id: int) -> Dict[str, Any]:
    """Computes progress metrics strictly for the logged-in student."""
    lessons = get_all_lessons(student_id=student_id)
    total_lessons = len(lessons)
    completed_lessons = sum(1 for l in lessons if l["is_completed"])
    progress_pct = int(round((completed_lessons / total_lessons * 100))) if total_lessons > 0 else 0

    return {
        "lessons": lessons,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "progress_pct": progress_pct
    }


def reset_student_progress(student_id: int) -> bool:
    """Resets progress records for the given student (demo testing)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM progress WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()
    return True

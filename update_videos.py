"""
Database migration script to update video URLs to active, public educational video streams.
"""

import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "platform.db")

# Mapping of course_id and lesson_order to public educational video embeds
VIDEO_MAPPINGS = {
    # Course 1: Python Basics
    (1, 1): "https://www.youtube.com/embed/_uQrJ0TkZlc",
    (1, 2): "https://www.youtube.com/embed/cKzP61Gzf00",
    (1, 3): "https://www.youtube.com/embed/DZwmZ8Usvnk",
    (1, 4): "https://www.youtube.com/embed/6iF8Xb7Z3wQ",

    # Course 2: Web Development Basics
    (2, 1): "https://www.youtube.com/embed/pQN-pnXPaVg",
    (2, 2): "https://www.youtube.com/embed/MDLn5-zSQQI",
    (2, 3): "https://www.youtube.com/embed/1PnVor36_40",
    (2, 4): "https://www.youtube.com/embed/W6NZfCO5SIk",

    # Course 3: C++ Programming
    (3, 1): "https://www.youtube.com/embed/vLnPwxZdW4Y",
    (3, 2): "https://www.youtube.com/embed/1v_4dL82nxI",
    (3, 3): "https://www.youtube.com/embed/8jLOx1hD3_o",
    (3, 4): "https://www.youtube.com/embed/knVbybC1T_E",

    # Course 4: Database Fundamentals
    (4, 1): "https://www.youtube.com/embed/wR0JG0eQsZA",
    (4, 2): "https://www.youtube.com/embed/7S_tz1z_5bA",
    (4, 3): "https://www.youtube.com/embed/HXV3zeQKqGY",
    (4, 4): "https://www.youtube.com/embed/27axs9dO7AE",
}

def update_video_urls():
    if not os.path.exists(DB_FILE):
        print("Database file not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for (course_id, lesson_order), url in VIDEO_MAPPINGS.items():
        cursor.execute(
            "UPDATE lessons SET video_url = ? WHERE course_id = ? AND lesson_order = ?",
            (url, course_id, lesson_order)
        )
        print(f"Updated Course {course_id}, Lesson {lesson_order} -> {url}")

    conn.commit()
    conn.close()
    print("All video URLs successfully updated in platform.db!")

if __name__ == "__main__":
    update_video_urls()

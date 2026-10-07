# Video Learning Platform 🎓

A complete, clean, and working academic mini project designed for the **Mobile & Web Programming (MWP)** college teacher demonstration. Built with standard **HTML5, CSS3, JavaScript**, **Python Flask**, and **SQLite**.

---

## 📌 Project Overview
The **Video Learning Platform** is a web-based educational application where students can register, log in, watch 5 foundational computer science video lessons streamed via responsive 16:9 YouTube iframe players, and maintain their individual lesson completion progress saved persistently in an SQLite database.

### Key Features:
1. **Student Authentication**: Secure Sign Up & Login system utilizing Flask session cookies and Werkzeug cryptographic password hashing (`pbkdf2:sha256`).
2. **Exactly 5 Foundational Lessons**:
   - Lesson 1: Introduction to Python
   - Lesson 2: HTML Basics
   - Lesson 3: CSS Basics
   - Lesson 4: JavaScript Basics
   - Lesson 5: SQL/Database Basics
3. **Working YouTube Video Player**: Responsive 16:9 aspect ratio `<iframe>` embeds using verified, public, embeddable educational video tutorials.
4. **Interactive Lesson Navigation**: "Previous Lesson" (disabled on Lesson 1), "Next Lesson" (disabled on Lesson 5), and "Back to Course" buttons.
5. **Real Database Completion Tracking**: Functional "Mark as Completed" button updating SQLite via both asynchronous AJAX (`/api/lesson/<num>/toggle`) and traditional HTML POST fallback (`/lesson/<num>/complete`).
6. **Multi-Tenant User Isolation**: Progress belongs strictly to the authenticated student (`student_id`). Student A completing lessons does not affect Student B.
7. **Dynamic My Progress Page**: Computes real-time metrics (e.g. `2 / 5 lessons completed` and `40%`) with a responsive progress bar and detailed breakdown table.

---

## 🛠️ Technology Stack
| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Structure** | HTML5 | Semantic markup (`<header>`, `<nav>`, `<iframe>`, `<main>`, `<footer>`) |
| **Frontend Styling** | Vanilla CSS3 | Custom design system, Flexbox, CSS Grid, responsive 16:9 video container |
| **Frontend Logic** | Vanilla JavaScript | Asynchronous Fetch API, DOM updates, toast notifications, mobile nav toggle |
| **Backend Framework** | Python 3 + Flask | Route dispatching, session management, template rendering, RESTful API |
| **Security** | Werkzeug | Cryptographic password hashing (`generate_password_hash`, `check_password_hash`) |
| **Database** | SQLite3 | Relational database (`platform.db`) with foreign key constraints |

---

## 🗄️ Relational Database Schema (`platform.db`)

The database automatically initializes upon application launch and creates 3 relational tables:

```
+--------------------------+           +--------------------------+           +--------------------------+
|         students         |           |         lessons          |           |         progress         |
+--------------------------+           +--------------------------+           +--------------------------+
| id (INTEGER PK AUTO)     |<----1:N---| id (INTEGER PK AUTO)     |<----1:1---| id (INTEGER PK AUTO)     |
| name (TEXT NOT NULL)     |           | lesson_number (INT UNIQUE|           | student_id (INT FK)      |
| email (TEXT UNIQUE)      |           | title (TEXT NOT NULL)    |           | lesson_id (INT FK)       |
| password_hash (TEXT)     |           | description (TEXT)       |           | is_completed (INT 0/1)   |
| created_at (TIMESTAMP)   |           | video_id (TEXT)          |           | completed_at (TIMESTAMP) |
+--------------------------+           | embed_url (TEXT)         |           +--------------------------+
                                       | duration (TEXT)          |           | UNIQUE(student_id,       |
                                       | summary_notes (TEXT)     |           |        lesson_id)        |
                                       +--------------------------+           +--------------------------+
```

### The 5 Foundational Lessons & YouTube Video Embeds:
1. **Introduction to Python**
   - Video Source: `https://www.youtube.com/embed/_uQrJ0TkZlc` (Programming with Mosh)
   - Duration: 15 mins
2. **HTML Basics**
   - Video Source: `https://www.youtube.com/embed/UB1O30fR-EE` (Traversy Media)
   - Duration: 20 mins
3. **CSS Basics**
   - Video Source: `https://www.youtube.com/embed/yfoY53QXEnI` (Traversy Media)
   - Duration: 20 mins
4. **JavaScript Basics**
   - Video Source: `https://www.youtube.com/embed/W6NZfCO5SIk` (Programming with Mosh)
   - Duration: 25 mins
5. **SQL/Database Basics**
   - Video Source: `https://www.youtube.com/embed/HXV3zeQKqGY` (freeCodeCamp.org)
   - Duration: 25 mins

---

## 🚀 How to Run the Project Locally

### 1. Prerequisites
- Python 3.8+ installed on your system.

### 2. Activate Virtual Environment
```bash
# On macOS / Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Flask Web Server
```bash
python3 app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

### 5. Run Automated End-to-End Test Suite
```bash
python3 test_e2e.py
```
(Executes all 21 test suites validating registration, authentication, 5 lessons, video embed URLs, SQLite persistence, and multi-tenant user isolation.)

---

## 🔑 Test Credentials (For Teacher Demonstration)
You can create your own account via the **Sign Up** page, or use either of the verified demonstration accounts:
- **Student 1**:
  - Email: `alice@example.com`
  - Password: `password123`
- **Student 2**:
  - Email: `bob@example.com`
  - Password: `secret456`

---

## 🎓 Teacher Demonstration Walkthrough
1. **Home Page**: Navigate to `http://127.0.0.1:5000/`. Review the project title, core features, and 5-lesson curriculum overview. Click **Start Learning**.
2. **Authentication Guard**: Verify that unauthenticated visitors attempting to access lessons or progress are redirected to `/login`.
3. **Sign Up**: Register with Full Name, Email, Password, and Confirm Password. Note validation against duplicate emails and password mismatch.
4. **Login**: Log in to see **"Welcome, [Student Name]"** and **Logout** in the navigation bar.
5. **Lessons View**: Observe all 5 foundational lessons displayed with initial 0% progress.
6. **Watch Video Lesson**: Open Lesson 1. Watch the YouTube video embedded inside a responsive 16:9 iframe. Note that "Previous Lesson" is disabled on Lesson 1.
7. **Mark Completed**: Click **Mark as Completed**. The button updates immediately to **"✓ Completed"** and SQLite records the completion.
8. **Navigation**: Click **Next Lesson →** to open Lesson 2. Mark it completed.
9. **My Progress**: Click **My Progress**. See the dynamic progress bar displaying `2 / 5 lessons completed (40%)`.
10. **Persistence**: Log out, log back in. Confirm that the 40% progress remains saved in SQLite.
11. **Multi-Tenant Isolation**: Log out and log in as Student 2 (or create a new account). Confirm Student 2 starts with `0 / 5 lessons completed (0%)`.

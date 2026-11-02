import os
import sqlite3

# Get the folder where this Python project is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database folder and file
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "study.db")


def get_connection():
    """Create and return a SQLite database connection."""
    os.makedirs(DATA_DIR, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    """Create the study_sessions and weekly_goals tables if they do not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            subject TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            study_duration REAL NOT NULL,
            break_duration REAL DEFAULT 0,
            distraction_time REAL DEFAULT 0,
            study_method TEXT,
            focus_rating INTEGER,
            test_score REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_goals (
            week_start TEXT NOT NULL,
            subject TEXT NOT NULL,
            goal_hours REAL NOT NULL CHECK (goal_hours >= 0),
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (week_start, subject)
        )
    """)

    connection.commit()
    connection.close()


def add_session(
    date,
    subject,
    start_time,
    end_time,
    study_duration,
    break_duration,
    distraction_time,
    study_method,
    focus_rating,
    test_score
):
    """Add a new study session to the database."""
    create_database()
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO study_sessions (
            date, subject, start_time, end_time, study_duration,
            break_duration, distraction_time, study_method, focus_rating, test_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        date, subject, start_time, end_time, study_duration,
        break_duration, distraction_time, study_method, focus_rating, test_score
    ))

    connection.commit()
    connection.close()


def get_all_sessions():
    """Return all study sessions, newest first."""
    create_database()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM study_sessions
        ORDER BY date DESC, id DESC
    """)
    sessions = cursor.fetchall()
    connection.close()
    # Return tuples to preserve the existing app.py's expected database format.
    return [tuple(row) for row in sessions]


def get_weekly_goals(week_start):
    """Return goals for a week as dictionaries with subject and goal_hours keys."""
    create_database()
    connection = get_connection()
    rows = connection.execute(
        "SELECT subject, goal_hours FROM weekly_goals WHERE week_start = ? ORDER BY subject",
        (week_start,),
    ).fetchall()
    connection.close()
    return [{"subject": row["subject"], "goal_hours": float(row["goal_hours"])} for row in rows]


def save_weekly_goal(week_start, subject, goal_hours):
    """Insert or update a weekly goal for the given week and subject."""
    if not isinstance(goal_hours, (int, float)) or goal_hours < 0:
        raise ValueError("goal_hours must be a non-negative number")
    create_database()
    connection = get_connection()
    connection.execute("""
        INSERT INTO weekly_goals (week_start, subject, goal_hours, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(week_start, subject) DO UPDATE SET
            goal_hours = excluded.goal_hours,
            updated_at = CURRENT_TIMESTAMP
    """, (week_start, subject, float(goal_hours)))
    connection.commit()
    connection.close()


def delete_weekly_goal(week_start, subject):
    """Delete an optional subject goal for a week."""
    create_database()
    connection = get_connection()
    connection.execute(
        "DELETE FROM weekly_goals WHERE week_start = ? AND subject = ?",
        (week_start, subject),
    )
    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")
    print(f"Database location: {DATABASE_PATH}")

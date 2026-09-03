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
    return sqlite3.connect(DATABASE_PATH)


def create_database():
    """Create the study_sessions table if it does not exist."""
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

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO study_sessions (
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
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
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
    ))

    connection.commit()
    connection.close()


def get_all_sessions():
    """Return all study sessions, newest first."""

    create_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM study_sessions
        ORDER BY date DESC, id DESC
    """)

    sessions = cursor.fetchall()

    connection.close()

    return sessions


if __name__ == "__main__":
    create_database()

    print("Database created successfully!")
    print(f"Database location: {DATABASE_PATH}")
import sqlite3
import os

# Database location
DATABASE_PATH = os.path.join("data", "study.db")


def create_database():
    os.makedirs("data", exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
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
    connection = sqlite3.connect(DATABASE_PATH)
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

    print("Study session added successfully!")


def get_all_sessions():
    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM study_sessions
        ORDER BY date DESC
    """)

    sessions = cursor.fetchall()

    connection.close()

    return sessions


if __name__ == "__main__":
    create_database()

    add_session(
        "2026-09-02",
        "Python",
        "18:00",
        "20:00",
        2.0,
        15,
        10,
        "Practice",
        4,
        82
    )

    sessions = get_all_sessions()

    print("\nStudy Sessions:")
    for session in sessions:
        print(session)
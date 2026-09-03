import sqlite3
from datetime import datetime


DATABASE_PATH = "data/study.db"


# --------------------------------------------------
# SAMPLE STUDY DATA
# --------------------------------------------------

sessions = [
    ("2026-08-20", "Python", "08:00", "09:00", 1.0, 10, 5, "Practice", 5, 91),
    ("2026-08-21", "Python", "18:00", "20:00", 2.0, 15, 10, "Practice", 4, 84),
    ("2026-08-22", "Statistics", "07:30", "09:30", 2.0, 10, 5, "Reading", 5, 94),
    ("2026-08-23", "SQL", "19:00", "20:30", 1.5, 10, 15, "Practice", 4, 88),
    ("2026-08-24", "Python", "14:00", "15:00", 1.0, 15, 20, "Video", 3, 76),
    ("2026-08-25", "Statistics", "08:00", "10:30", 2.5, 15, 5, "Problem Solving", 5, 96),
    ("2026-08-26", "SQL", "18:00", "20:30", 2.5, 20, 10, "Practice", 5, 92),
    ("2026-08-27", "Python", "21:00", "22:00", 1.0, 10, 25, "Video", 2, 68),
    ("2026-08-28", "Excel", "10:00", "11:30", 1.5, 10, 5, "Practice", 4, 87),
    ("2026-08-29", "Statistics", "17:00", "18:00", 1.0, 10, 20, "Reading", 3, 79),
    ("2026-08-30", "SQL", "08:00", "10:00", 2.0, 15, 5, "Problem Solving", 5, 95),
    ("2026-08-31", "Excel", "15:00", "16:00", 1.0, 10, 15, "Video", 3, 74),
    ("2026-09-01", "Python", "18:00", "20:00", 2.0, 15, 10, "Practice", 4, 85),
    ("2026-09-02", "Python", "18:00", "20:00", 2.0, 15, 10, "Practice", 4, 82),
    ("2026-09-03", "Python", "18:00", "20:00", 2.0, 15, 10, "Practice", 4, 82),
    ("2026-09-03", "SQL", "08:00", "09:30", 1.5, 10, 5, "Practice", 5, 93),
    ("2026-09-03", "Statistics", "13:00", "14:30", 1.5, 15, 20, "Reading", 3, 78),
    ("2026-09-03", "Excel", "19:00", "20:00", 1.0, 5, 15, "Video", 3, 75),
]


# --------------------------------------------------
# INSERT DATA
# --------------------------------------------------

def insert_data():

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    query = """
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
    """

    cursor.executemany(query, sessions)

    connection.commit()

    connection.close()

    print(f"\nSuccessfully added {len(sessions)} study sessions.")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("       STUDY TIME ANALYZER - SAMPLE DATA")
    print("=" * 60)

    insert_data()

    print("\nSample data has been added to the database.")
    print("Now run: python analysis.py")
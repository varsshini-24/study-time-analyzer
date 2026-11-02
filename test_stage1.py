"""Lightweight smoke tests for the StudyFlow Stage 1 update."""
import math
import os
import pandas as pd
import plotly.express as px

from analysis import (
    clean_data, calculate_metrics, daily_analysis, subject_analysis,
    study_method_analysis, time_of_day_analysis, generate_recommendations,
)


def main():
    sample = pd.DataFrame([
        {"id": 1, "date": "2026-10-15", "subject": "python", "start_time": "09:00", "end_time": "10:00", "study_duration": 1.0, "break_duration": 5, "distraction_time": 3, "study_method": "practice", "focus_rating": 4, "test_score": 82},
        {"id": 2, "date": "2026-10-16", "subject": "sql", "start_time": "18:00", "end_time": "19:30", "study_duration": 1.5, "break_duration": 10, "distraction_time": 7, "study_method": "reading", "focus_rating": 5, "test_score": 91},
        {"id": 3, "date": "2026-10-16", "subject": "python", "start_time": "10:00", "end_time": "11:00", "study_duration": 1.0, "break_duration": 0, "distraction_time": 1, "study_method": "practice", "focus_rating": 4, "test_score": 88},
    ])
    df = clean_data(sample)
    assert len(df) == 3, "Cleaning unexpectedly removed valid sample rows"
    metrics = calculate_metrics(df)
    assert metrics["total_sessions"] == 3
    assert abs(float(metrics["total_study_hours"]) - 3.5) < 1e-9
    assert not daily_analysis(df).empty
    assert not subject_analysis(df).empty
    assert not study_method_analysis(df).empty
    assert not time_of_day_analysis(df).empty
    fig = px.area(daily_analysis(df), x="date", y="study_hours", markers=True)
    assert len(fig.data) == 1, "Plotly chart was not created"
    print("PASS: data cleaning, metrics, analytics, and Plotly smoke test")


# ── P0-1: unscored / unfocused sessions must survive clean_data ──────────────

def test_unscored_sessions_preserved():
    """Sessions without test_score or focus_rating must not be removed."""
    raw = pd.DataFrame([
        # fully scored
        {"id": 1, "date": "2026-10-15", "subject": "python", "start_time": "09:00",
         "end_time": "10:00", "study_duration": 1.0, "break_duration": 0,
         "distraction_time": 2, "study_method": "practice",
         "focus_rating": 4, "test_score": 80},
        # missing test_score only
        {"id": 2, "date": "2026-10-16", "subject": "sql", "start_time": "14:00",
         "end_time": "15:00", "study_duration": 1.0, "break_duration": 0,
         "distraction_time": 0, "study_method": "reading",
         "focus_rating": 3, "test_score": None},
        # missing focus_rating only
        {"id": 3, "date": "2026-10-17", "subject": "math", "start_time": "10:00",
         "end_time": "11:00", "study_duration": 1.0, "break_duration": 0,
         "distraction_time": 5, "study_method": "practice",
         "focus_rating": None, "test_score": 75},
        # missing both
        {"id": 4, "date": "2026-10-18", "subject": "physics", "start_time": "09:00",
         "end_time": "10:30", "study_duration": 1.5, "break_duration": 0,
         "distraction_time": 0, "study_method": "flashcards",
         "focus_rating": None, "test_score": None},
        # invalid required field – must be dropped
        {"id": 5, "date": None, "subject": "history", "start_time": "09:00",
         "end_time": "10:00", "study_duration": 1.0, "break_duration": 0,
         "distraction_time": 0, "study_method": "reading",
         "focus_rating": 5, "test_score": 90},
    ])

    df = clean_data(raw)
    assert len(df) == 4, (
        f"Expected 4 rows after cleaning (row with null date dropped), got {len(df)}"
    )
    # All four valid sessions survive
    assert set(df["id"]) == {1, 2, 3, 4}, "Unexpected session ids after cleaning"

    # Metrics must not crash even when focus/score are all NaN for some rows
    metrics = calculate_metrics(df)
    assert metrics["total_sessions"] == 4

    # calculate_metrics returns NaN for optional averages when data is partial
    # – that is acceptable; just ensure no exception is raised
    assert metrics["total_study_hours"] == pytest_approx(4.5)

    # generate_recommendations must not throw TypeError on NaN focus/score
    subj = subject_analysis(df)
    meth = study_method_analysis(df)
    tod  = time_of_day_analysis(df)
    recs = generate_recommendations(df, metrics, subj, meth, tod)
    assert isinstance(recs, list) and len(recs) > 0

    print("PASS: unscored sessions preserved and NaN-safe metrics/recommendations")


def pytest_approx(expected, rel=1e-6):
    """Tiny helper so the test file has no pytest dependency."""
    class _Approx:
        def __eq__(self, other):
            return math.isclose(float(other), expected, rel_tol=rel)
        def __repr__(self):
            return f"~{expected}"
    return _Approx()


# ── P0-2: requirements.txt must contain reportlab ────────────────────────────

def test_reportlab_in_requirements():
    """requirements.txt must list reportlab>=4.0.0."""
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_path) as fh:
        content = fh.read()
    assert "reportlab" in content, "reportlab is missing from requirements.txt"
    # Confirm minimum version is stated
    assert "4.0" in content, "reportlab entry does not specify >=4.0.0"
    print("PASS: reportlab>=4.0.0 found in requirements.txt")


if __name__ == "__main__":
    main()
    test_unscored_sessions_preserved()
    test_reportlab_in_requirements()

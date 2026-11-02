"""
Isolated tests for the improved StudyFlow recommendation engine.

Tests cover:
  R1  – best method requires >= 3 sessions
  R2  – best time requires >= 3 sessions
  R3  – missing focus_rating / test_score handled safely
  R4  – no contradictory recommendations
  R5  – recommendations reference actual data values (not hardcoded)
  R6  – insufficient data → clear explanation
  R7  – all 7 categories can be produced
  R8  – no causation language in distraction/focus recs
  R9  – full-data path (>= 3 sessions per bucket) works correctly
  R10 – streak and weekly-goal recommendations work

Run from the project root:
    venv\\Scripts\\python.exe test_recommendations.py
"""

import math
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from analysis import (
    clean_data, calculate_metrics, subject_analysis,
    study_method_analysis, time_of_day_analysis, daily_analysis,
    generate_recommendations, _MIN_SESSIONS_FOR_BEST_CLAIM,
)

# ── Tiny test helpers ─────────────────────────────────────────────────────────
_passed = []
_failed = []


def check(name, condition, detail=""):
    if condition:
        _passed.append(name)
        print(f"  PASS  {name}")
    else:
        _failed.append(name)
        print(f"  FAIL  {name}" + (f"\n        {detail}" if detail else ""))


def _make_session(
    id_, date, subject, start_time, duration, method,
    focus=4, score=80, distraction=0
):
    return {
        "id": id_, "date": date, "subject": subject,
        "start_time": start_time, "end_time": "00:00",
        "study_duration": duration, "break_duration": 0,
        "distraction_time": distraction,
        "study_method": method,
        "focus_rating": focus,
        "test_score": score,
    }


def _recs(rows, **kwargs):
    """Clean rows, compute standard inputs, call generate_recommendations."""
    df = clean_data(pd.DataFrame(rows))
    metrics = calculate_metrics(df)
    subj = subject_analysis(df)
    meth = study_method_analysis(df)
    tod = time_of_day_analysis(df)
    daily = daily_analysis(df)
    return generate_recommendations(df, metrics, subj, meth, tod, daily_data=daily, **kwargs)


# ═════════════════════════════════════════════════════════════════════════════
# R1  Best method requires >= _MIN_SESSIONS_FOR_BEST_CLAIM sessions
# ═════════════════════════════════════════════════════════════════════════════
print("\n── R1: Best method requires >=3 sessions ──")

# 1a. Fewer than MIN sessions per method → no best-method claim
rows_few = [
    _make_session(1, "2026-10-01", "Python", "09:00", 1.0, "Practice", score=80),
    _make_session(2, "2026-10-02", "Python", "09:00", 1.0, "Reading", score=70),
]
recs = _recs(rows_few)
has_best_claim = any("associated with your highest average score" in r for r in recs)
check(
    "R1a: 2 sessions → no best-method claim",
    not has_best_claim,
    f"Recs: {recs}",
)
has_need_more = any("Not enough data to identify your best study method" in r for r in recs)
check(
    "R1b: 2 sessions → insufficient-data message shown for methods",
    has_need_more,
    f"Recs: {recs}",
)

# 1c. Exactly MIN sessions for one method → claim appears
rows_min = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice", score=80+i)
    for i in range(1, _MIN_SESSIONS_FOR_BEST_CLAIM + 1)
]
recs = _recs(rows_min)
has_best_claim = any("associated with your highest average score" in r for r in recs)
check(
    f"R1c: exactly {_MIN_SESSIONS_FOR_BEST_CLAIM} sessions → best-method claim appears",
    has_best_claim,
    f"Recs: {recs}",
)

# 1d. One method has 3+ sessions, another has 1 → only the qualified method is "best"
rows_mixed = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice", score=80)
    for i in range(1, 4)
] + [
    _make_session(4, "2026-10-04", "Python", "09:00", 1.0, "Reading", score=95),
]
recs = _recs(rows_mixed)
# "Reading" has only 1 session; it should NOT appear as best even with high score
claims = [r for r in recs if "associated with your highest average score" in r]
reading_as_best = any("Reading" in r and "associated with your highest average score" in r for r in recs)
check(
    "R1d: method with 1 session not declared best even if highest score",
    not reading_as_best,
    f"Recs: {recs}",
)

# ═════════════════════════════════════════════════════════════════════════════
# R2  Best time requires >= _MIN_SESSIONS_FOR_BEST_CLAIM sessions
# ═════════════════════════════════════════════════════════════════════════════
print("\n── R2: Best time requires >=3 sessions ──")

# 2a. Only 2 Morning sessions → no best-time claim
rows_tod_few = [
    _make_session(1, "2026-10-01", "Python", "09:00", 1.0, "Practice", score=80),
    _make_session(2, "2026-10-02", "Python", "09:00", 1.0, "Practice", score=85),
]
recs = _recs(rows_tod_few)
has_time_claim = any("associated with your best average score" in r for r in recs)
check(
    "R2a: 2 Morning sessions → no best-time claim",
    not has_time_claim,
    f"Recs: {recs}",
)
has_time_need = any("Not enough data to identify your most effective study time" in r for r in recs)
check(
    "R2b: 2 sessions → insufficient-data message for time",
    has_time_need,
    f"Recs: {recs}",
)

# 2c. 3 Morning sessions → claim appears
rows_tod_ok = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice", score=80)
    for i in range(1, 4)
]
recs = _recs(rows_tod_ok)
has_time_claim = any("associated with your best average score" in r for r in recs)
check(
    "R2c: 3 Morning sessions → best-time claim appears",
    has_time_claim,
    f"Recs: {recs}",
)

# ═════════════════════════════════════════════════════════════════════════════
# R3  Missing focus_rating and test_score handled safely
# ═════════════════════════════════════════════════════════════════════════════
print("\n── R3: Missing values handled safely ──")

rows_no_score = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice", score=None)
    for i in range(1, 4)
]
try:
    recs = _recs(rows_no_score)
    check("R3a: all test_score=None → no crash", True)
    has_no_score_msg = any("No test scores recorded yet" in r for r in recs)
    check("R3b: no test_score → 'No test scores' message", has_no_score_msg, f"Recs: {recs}")
except Exception as exc:
    check("R3a: all test_score=None → no crash", False, str(exc))
    check("R3b: no test_score → 'No test scores' message", False)

rows_no_focus = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice", focus=None, score=80)
    for i in range(1, 4)
]
try:
    recs = _recs(rows_no_focus)
    check("R3c: all focus_rating=None → no crash", True)
    has_no_focus_msg = any("No focus ratings recorded yet" in r for r in recs)
    check("R3d: no focus_rating → 'No focus ratings' message", has_no_focus_msg, f"Recs: {recs}")
except Exception as exc:
    check("R3c: all focus_rating=None → no crash", False, str(exc))
    check("R3d: no focus_rating → 'No focus ratings' message", False)

rows_both_none = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice", focus=None, score=None)
    for i in range(1, 4)
]
try:
    recs = _recs(rows_both_none)
    check("R3e: focus=None AND score=None → no crash", True)
    check("R3f: result is a non-empty list", isinstance(recs, list) and len(recs) > 0, f"Recs: {recs}")
except Exception as exc:
    check("R3e: focus=None AND score=None → no crash", False, str(exc))
    check("R3f: result is a non-empty list", False)

# ═════════════════════════════════════════════════════════════════════════════
# R4  No contradictory recommendations
# ═════════════════════════════════════════════════════════════════════════════
print("\n── R4: No contradictory recommendations ──")

# High distraction (>15) AND well-controlled should not both appear
rows_high_distr = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice",
                  distraction=20, score=80)
    for i in range(1, 4)
]
recs = _recs(rows_high_distr)
high_dist_recs = [r for r in recs if "📱" in r]
has_high = any("higher than the recommended target" in r for r in high_dist_recs)
has_controlled = any("well controlled" in r for r in high_dist_recs)
check(
    "R4a: high distraction → only high-distraction message, not well-controlled",
    has_high and not has_controlled,
    f"Distraction recs: {high_dist_recs}",
)

# Low focus AND strong-focus should not both appear
rows_low_focus = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice",
                  focus=2, score=80)
    for i in range(1, 4)
]
recs = _recs(rows_low_focus)
focus_recs = [r for r in recs if "🎯" in r and "weekly" not in r.lower()]
has_low = any("shorter, distraction-free blocks" in r for r in focus_recs)
has_strong = any("Strong focus" in r for r in focus_recs)
check(
    "R4b: focus=2/5 → only low-focus message, not strong-focus",
    has_low and not has_strong,
    f"Focus recs: {focus_recs}",
)

# ═════════════════════════════════════════════════════════════════════════════
# R5  Recommendations reference actual user data values
# ═════════════════════════════════════════════════════════════════════════════
print("\n── R5: Recommendations use actual data values ──")

rows_actual = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice",
                  focus=3, score=72, distraction=5)
    for i in range(1, 4)
]
recs = _recs(rows_actual)
# Focus value 3.0 should appear in the focus rec
focus_recs = [r for r in recs if "🎯" in r and "weekly" not in r.lower()]
has_value = any("3.0/5" in r for r in focus_recs)
check(
    "R5a: actual focus value (3.0) appears in focus recommendation",
    has_value,
    f"Focus recs: {focus_recs}",
)
# Score 72.0 should appear in the overall performance rec
score_recs = [r for r in recs if "📈" in r]
has_score = any("72.0%" in r for r in score_recs)
check(
    "R5b: actual average score (72.0%) appears in performance recommendation",
    has_score,
    f"Score recs: {score_recs}",
)

# ═════════════════════════════════════════════════════════════════════════════
# R6  Insufficient data → clear explanation
# ═════════════════════════════════════════════════════════════════════════════
print("\n── R6: Insufficient data → clear explanation ──")

rows_1 = [_make_session(1, "2026-10-01", "Python", "09:00", 1.0, "Practice")]
recs = _recs(rows_1)
has_volume_warning = any("fewer than 3 study sessions" in r for r in recs)
check(
    "R6a: 1 session → data-volume warning shown",
    has_volume_warning,
    f"Recs: {recs}",
)

rows_empty = pd.DataFrame(columns=[
    "id", "date", "subject", "start_time", "end_time",
    "study_duration", "break_duration", "distraction_time",
    "study_method", "focus_rating", "test_score",
])
df_empty = clean_data(rows_empty)
metrics_empty = calculate_metrics(df_empty)
subj_e = subject_analysis(df_empty)
meth_e = study_method_analysis(df_empty)
tod_e = time_of_day_analysis(df_empty)
daily_e = daily_analysis(df_empty) if not df_empty.empty else pd.DataFrame()
try:
    recs_empty = generate_recommendations(df_empty, metrics_empty, subj_e, meth_e, tod_e)
    check("R6b: empty df → no crash", True)
    check("R6c: empty df → returns list", isinstance(recs_empty, list))
except Exception as exc:
    check("R6b: empty df → no crash", False, str(exc))
    check("R6c: empty df → returns list", False)

# ═════════════════════════════════════════════════════════════════════════════
# R7  All 7 recommendation categories can be produced with enough data
# ═════════════════════════════════════════════════════════════════════════════
print("\n── R7: All 7 categories present with sufficient data ──")

# Build a dataset with >=3 sessions per method and time period
METHODS = ["Practice", "Reading", "Revision"]
TIMES = ["09:00", "09:00", "09:00", "14:00", "14:00", "14:00", "19:00", "19:00", "19:00"]
rows_rich = []
idx = 1
for m_i, method in enumerate(METHODS):
    for t_i in range(3):
        rows_rich.append(_make_session(
            idx,
            f"2026-10-{idx:02d}",
            "Python" if m_i < 2 else "SQL",
            TIMES[m_i * 3 + t_i],
            1.5,
            method,
            focus=3 + m_i,
            score=70 + m_i * 5 + t_i * 2,
            distraction=5,
        ))
        idx += 1

recs_rich = _recs(
    rows_rich,
    streak_days=5,
    weekly_goal_hours=10.0,
    weekly_studied_hours=7.5,
)

check("R7-focus:       focus category present",
      any("🎯" in r and "focus" in r.lower() and "weekly" not in r.lower() for r in recs_rich))
check("R7-distraction: distraction category present",
      any("📱" in r for r in recs_rich))
check("R7-method:      method category present",
      any("📚" in r for r in recs_rich))
check("R7-time:        time category present",
      any("🕐" in r for r in recs_rich))
check("R7-subject:     subject category present",
      any("📖" in r for r in recs_rich))
check("R7-score:       performance category present",
      any("📈" in r for r in recs_rich))
check("R7-streak:      streak category present",
      any("🔥" in r for r in recs_rich))
check("R7-goals:       weekly goal category present",
      any("Almost there" in r or "Weekly goal" in r or "Weekly progress" in r for r in recs_rich))

# ═════════════════════════════════════════════════════════════════════════════
# R8  No causation language in distraction / focus recommendations
# ═════════════════════════════════════════════════════════════════════════════
print("\n── R8: Associative not causal language ──")

CAUSAL_PHRASES = [
    "causes", "caused by", "leads to", "results in",
    "proves", "guarantees", "will improve", "will reduce",
]

rows_corr = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice",
                  focus=4, score=80, distraction=20)
    for i in range(1, 6)
]
recs = _recs(rows_corr)
dist_focus_recs = [r for r in recs if "📱" in r or ("🎯" in r and "weekly" not in r.lower())]

for phrase in CAUSAL_PHRASES:
    has_causal = any(phrase in r.lower() for r in dist_focus_recs)
    check(
        f"R8: no '{phrase}' in distraction/focus recs",
        not has_causal,
        f"Found in: {[r for r in dist_focus_recs if phrase in r.lower()]}",
    )

# ═════════════════════════════════════════════════════════════════════════════
# R9  Full-data path works correctly (method, time, subject, score all valid)
# ═════════════════════════════════════════════════════════════════════════════
print("\n── R9: Full-data path ──")

rows_full = [
    # Practice × 3 (morning) – high scores
    _make_session(1, "2026-10-01", "Python", "09:00", 2.0, "Practice", focus=5, score=90),
    _make_session(2, "2026-10-02", "Python", "09:00", 2.0, "Practice", focus=5, score=92),
    _make_session(3, "2026-10-03", "Python", "09:00", 2.0, "Practice", focus=4, score=88),
    # Reading × 3 (afternoon) – lower scores
    _make_session(4, "2026-10-04", "SQL", "14:00", 1.5, "Reading", focus=3, score=70),
    _make_session(5, "2026-10-05", "SQL", "14:00", 1.5, "Reading", focus=3, score=72),
    _make_session(6, "2026-10-06", "SQL", "14:00", 1.5, "Reading", focus=3, score=68),
]
recs_full = _recs(rows_full)

# Practice should be best method
practice_best = any(
    "Practice" in r and "associated with your highest average score" in r
    for r in recs_full
)
check("R9a: Practice correctly identified as best method", practice_best, f"Recs: {recs_full}")

# Morning should be best time
morning_best = any(
    "Morning" in r and "associated with your best average score" in r
    for r in recs_full
)
check("R9b: Morning correctly identified as best time", morning_best, f"Recs: {recs_full}")

# SQL should be weakest subject
sql_weakest = any("SQL" in r and "lowest average score" in r for r in recs_full)
check("R9c: SQL correctly identified as weakest subject", sql_weakest, f"Recs: {recs_full}")

# Score must reference actual average (~80%)
avg_score = (90 + 92 + 88 + 70 + 72 + 68) / 6
score_recs = [r for r in recs_full if "📈" in r]
expected_val = f"{avg_score:.1f}%"
check(
    f"R9d: actual average score ({expected_val}) in performance rec",
    any(expected_val in r for r in score_recs),
    f"Score recs: {score_recs}",
)

# ═════════════════════════════════════════════════════════════════════════════
# R10 Streak and weekly goal recommendations
# ═════════════════════════════════════════════════════════════════════════════
print("\n── R10: Streak and weekly goal recommendations ──")

rows_base = [
    _make_session(i, f"2026-10-{i:02d}", "Python", "09:00", 1.0, "Practice", score=80)
    for i in range(1, 4)
]

# 10a – streak = 0 with existing data → lapsed message
recs = _recs(rows_base, streak_days=0)
has_lapsed = any("streak has lapsed" in r for r in recs)
check("R10a: streak=0 with data → streak-lapsed message", has_lapsed, f"Recs: {recs}")

# 10b – streak = 1 → "studied today" message
recs = _recs(rows_base, streak_days=1)
has_today = any("studied today" in r for r in recs)
check("R10b: streak=1 → 'studied today' message", has_today, f"Recs: {recs}")

# 10c – streak = 5 → good-momentum message
recs = _recs(rows_base, streak_days=5)
has_momentum = any("Good momentum" in r for r in recs)
check("R10c: streak=5 → 'Good momentum' message", has_momentum, f"Recs: {recs}")

# 10d – streak = 10 → excellent-consistency message
recs = _recs(rows_base, streak_days=10)
has_excellent = any("Excellent consistency" in r for r in recs)
check("R10d: streak=10 → 'Excellent consistency' message", has_excellent, f"Recs: {recs}")

# 10e – goal achieved (100%)
recs = _recs(rows_base, weekly_goal_hours=5.0, weekly_studied_hours=6.0)
has_achieved = any("Weekly goal achieved" in r for r in recs)
check("R10e: studied >= goal → 'Weekly goal achieved' message", has_achieved, f"Recs: {recs}")

# 10f – goal 70–99% complete → "almost there"
recs = _recs(rows_base, weekly_goal_hours=10.0, weekly_studied_hours=7.5)
has_almost = any("Almost there" in r for r in recs)
check("R10f: 75% of goal → 'Almost there' message", has_almost, f"Recs: {recs}")

# 10g – goal < 70% → generic progress message
recs = _recs(rows_base, weekly_goal_hours=10.0, weekly_studied_hours=2.0)
has_progress = any("Weekly progress" in r for r in recs)
check("R10g: 20% of goal → 'Weekly progress' message", has_progress, f"Recs: {recs}")

# 10h – no goal set (weekly_goal_hours=0) → no weekly rec
recs = _recs(rows_base, weekly_goal_hours=0.0)
has_weekly = any(
    "Weekly goal" in r or "Almost there" in r or "Weekly progress" in r
    for r in recs
)
check("R10h: weekly_goal_hours=0 → no weekly goal recommendation", not has_weekly, f"Recs: {recs}")

# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
total = len(_passed) + len(_failed)
print(f"RESULTS: {len(_passed)}/{total} PASS  |  {len(_failed)} FAIL")
print("=" * 60)

if _failed:
    print("\nFailed tests:")
    for name in _failed:
        print(f"  FAIL  {name}")
    sys.exit(1)
else:
    print("\nAll recommendation engine tests passed.")
    sys.exit(0)

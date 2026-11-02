import pandas as pd
import sqlite3
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "study.db")


def load_data():
    connection = sqlite3.connect(DATABASE_PATH)
    query = """
        SELECT id, date, subject, start_time, end_time,
               study_duration, break_duration, distraction_time,
               study_method, focus_rating, test_score
        FROM study_sessions
    """
    df = pd.read_sql_query(query, connection)
    connection.close()
    return df


def clean_data(df):
    if df.empty:
        return df

    df = df.copy()

    df["subject"] = (
        df["subject"].astype(str).str.strip().str.title()
    )
    df["study_method"] = (
        df["study_method"].astype(str).str.strip().str.title()
    )

    numeric_columns = [
        "study_duration", "break_duration", "distraction_time",
        "focus_rating", "test_score"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["start_time"] = df["start_time"].astype(str)

    # Only drop rows that are missing truly required fields.
    # focus_rating and test_score are optional; calculations below handle NaN.
    df = df.dropna(
        subset=["date", "subject", "study_duration"]
    )

    df["distraction_time"] = df["distraction_time"].fillna(0)
    df["break_duration"] = df["break_duration"].fillna(0)

    return df


def calculate_metrics(df):
    if df.empty:
        return {
            "total_study_hours": 0,
            "average_daily_hours": 0,
            "average_focus": 0,
            "total_distraction": 0,
            "average_score": 0,
            "total_sessions": 0,
        }

    daily_hours = df.groupby(df["date"].dt.date)["study_duration"].sum()

    return {
        "total_study_hours": df["study_duration"].sum(),
        "average_daily_hours": daily_hours.mean(),
        "average_focus": df["focus_rating"].mean(),
        "total_distraction": df["distraction_time"].sum(),
        "average_score": df["test_score"].mean(),
        "total_sessions": len(df),
    }


def subject_analysis(df):
    if df.empty:
        return pd.DataFrame()

    return (
        df.groupby("subject")
        .agg(
            total_study_hours=("study_duration", "sum"),
            average_focus=("focus_rating", "mean"),
            average_score=("test_score", "mean"),
            total_distraction=("distraction_time", "sum"),
            sessions=("id", "count"),
        )
        .reset_index()
        .round(2)
    )


def study_method_analysis(df):
    if df.empty:
        return pd.DataFrame()

    return (
        df.groupby("study_method")
        .agg(
            sessions=("id", "count"),
            total_study_hours=("study_duration", "sum"),
            average_focus=("focus_rating", "mean"),
            average_score=("test_score", "mean"),
            average_distraction=("distraction_time", "mean"),
        )
        .reset_index()
        .sort_values("average_score", ascending=False)
        .round(2)
    )


def find_best_method(method_data):
    if method_data.empty:
        return None
    return method_data.iloc[0]


def _time_period(start_time):
    try:
        hour = int(str(start_time).split(":")[0])
    except (ValueError, IndexError):
        return "Unknown"

    if 5 <= hour < 12:
        return "Morning"
    if 12 <= hour < 17:
        return "Afternoon"
    if 17 <= hour < 22:
        return "Evening"
    return "Night"


def time_of_day_analysis(df):
    if df.empty:
        return pd.DataFrame()

    data = df.copy()
    data["time_period"] = data["start_time"].apply(_time_period)

    order = ["Morning", "Afternoon", "Evening", "Night"]

    result = (
        data.groupby("time_period")
        .agg(
            sessions=("id", "count"),
            total_study_hours=("study_duration", "sum"),
            average_focus=("focus_rating", "mean"),
            average_score=("test_score", "mean"),
            average_distraction=("distraction_time", "mean"),
        )
        .reset_index()
    )

    result["time_period"] = pd.Categorical(
        result["time_period"], categories=order, ordered=True
    )
    return result.sort_values("time_period").round(2)


def find_best_time(time_data):
    if time_data.empty:
        return None
    return time_data.sort_values("average_score", ascending=False).iloc[0]


def duration_score_analysis(df):
    if df.empty:
        return pd.DataFrame()

    data = df.copy()
    bins = [0, 2, 3, np.inf]
    labels = ["1–2 hours", "2–3 hours", "3+ hours"]

    data["duration_group"] = pd.cut(
        data["study_duration"],
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=True,
    )

    result = (
        data.groupby("duration_group", observed=False)
        .agg(
            sessions=("id", "count"),
            average_study_hours=("study_duration", "mean"),
            average_score=("test_score", "mean"),
        )
        .reset_index()
    )

    return result.round(2)


def calculate_correlation(df, column1, column2):
    if df.empty or column1 not in df.columns or column2 not in df.columns:
        return 0.0

    data = df[[column1, column2]].dropna()

    if len(data) < 2 or data[column1].nunique() < 2 or data[column2].nunique() < 2:
        return 0.0

    return float(data[column1].corr(data[column2]))


def correlation_interpretation(value):
    value = float(value)

    if value >= 0.7:
        return "Strong positive relationship."
    if value >= 0.3:
        return "Moderate positive relationship."
    if value > -0.3:
        return "Weak or no clear relationship."
    if value > -0.7:
        return "Moderate negative relationship."
    return "Strong negative relationship."


def focus_score_analysis(df):
    if df.empty:
        return pd.DataFrame()

    return (
        df.groupby("focus_rating")
        .agg(
            sessions=("id", "count"),
            average_study_hours=("study_duration", "mean"),
            average_score=("test_score", "mean"),
            average_distraction=("distraction_time", "mean"),
        )
        .reset_index()
        .round(2)
    )


def distraction_score_analysis(df):
    if df.empty:
        return pd.DataFrame()

    data = df.copy()
    bins = [-np.inf, 5, 15, np.inf]
    labels = ["Low (0–5 min)", "Medium (6–15 min)", "High (16+ min)"]

    data["distraction_group"] = pd.cut(
        data["distraction_time"],
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=True,
    )

    return (
        data.groupby("distraction_group", observed=False)
        .agg(
            sessions=("id", "count"),
            average_distraction=("distraction_time", "mean"),
            average_score=("test_score", "mean"),
        )
        .reset_index()
        .round(2)
    )


def daily_analysis(df):
    result = (
        df.groupby("date")
        .agg(
            study_hours=("study_duration", "sum"),
            average_focus=("focus_rating", "mean"),
            average_score=("test_score", "mean"),
            distraction=("distraction_time", "sum"),
            sessions=("id", "count"),
        )
        .reset_index()
        .sort_values("date")
    )

    numeric_columns = [
        "study_hours",
        "average_focus",
        "average_score",
        "distraction",
        "sessions",
    ]
    result[numeric_columns] = result[numeric_columns].round(2)

    return result

def progress_analysis(df):
    daily = daily_analysis(df)

    if len(daily) < 2:
        return {
            "study_hours_change": 0.0,
            "focus_change": 0.0,
            "score_change": 0.0,
            "distraction_change": 0.0,
            "study_trend": "Insufficient data",
            "focus_trend": "Insufficient data",
            "score_trend": "Insufficient data",
            "distraction_trend": "Insufficient data",
        }

    first = daily.iloc[0]
    last = daily.iloc[-1]

    def trend(first_value, last_value, lower_is_better=False):
        change = last_value - first_value
        if abs(change) < 0.05:
            return "Stable →"
        if lower_is_better:
            return "Improving ↘" if change < 0 else "Declining ↗"
        return "Improving ↗" if change > 0 else "Declining ↘"

    return {
        "study_hours_change": last["study_hours"] - first["study_hours"],
        "focus_change": last["average_focus"] - first["average_focus"],
        "score_change": last["average_score"] - first["average_score"],
        "distraction_change": last["distraction"] - first["distraction"],
        "study_trend": trend(first["study_hours"], last["study_hours"]),
        "focus_trend": trend(first["average_focus"], last["average_focus"]),
        "score_trend": trend(first["average_score"], last["average_score"]),
        "distraction_trend": trend(
            first["distraction"], last["distraction"], lower_is_better=True
        ),
    }



# ── Minimum thresholds for "best X" claims ────────────────────────────────
_MIN_SESSIONS_FOR_BEST_CLAIM = 3   # must have ≥ this many sessions per bucket


def generate_recommendations(
    df,
    metrics,
    subject_data,
    method_data,
    time_data,
    *,
    daily_data=None,
    streak_days: int = 0,
    weekly_goal_hours: float = 0.0,
    weekly_studied_hours: float = 0.0,
):
    """
    Return a list of personalised recommendation strings derived entirely
    from the user's own recorded data.

    Parameters
    ----------
    df : DataFrame        – cleaned session data
    metrics : dict        – from calculate_metrics()
    subject_data : DataFrame – from subject_analysis()
    method_data  : DataFrame – from study_method_analysis()
    time_data    : DataFrame – from time_of_day_analysis()
    daily_data   : DataFrame | None – from daily_analysis(); used for
                   streak/consistency insights (optional, backward-compat)
    streak_days  : int    – current consecutive-day streak (optional)
    weekly_goal_hours   : float – user's overall weekly study goal
    weekly_studied_hours : float – hours studied so far this week
    """
    recommendations = []
    total_sessions = metrics["total_sessions"]
    focus = metrics["average_focus"]
    score = metrics["average_score"]
    distraction_per_session = (
        metrics["total_distraction"] / max(total_sessions, 1)
    )

    # ── 1. DATA VOLUME CHECK ─────────────────────────────────────────────────
    # Surface a gentle nudge when there is very little data overall,
    # but still generate whatever partial insights we can.
    if total_sessions < 3:
        recommendations.append(
            "📊 You have fewer than 3 study sessions recorded. "
            "Add more sessions to unlock richer, personalised insights — "
            "most recommendations need at least 3 sessions to be meaningful."
        )

    # ── 2. FOCUS RATING ──────────────────────────────────────────────────────
    if pd.isna(focus):
        recommendations.append(
            "🎯 No focus ratings recorded yet. "
            "Rate your concentration after each session (1–5) so StudyFlow "
            "can identify patterns in your study quality."
        )
    else:
        rated_sessions = int(df["focus_rating"].notna().sum())
        if focus < 3:
            recommendations.append(
                f"🎯 Your average focus is {focus:.1f}/5 across "
                f"{rated_sessions} rated session(s). "
                "Try shorter, distraction-free blocks (25–45 min) with "
                "scheduled breaks to strengthen your concentration."
            )
        elif focus < 4:
            recommendations.append(
                f"🎯 Your average focus is {focus:.1f}/5 across "
                f"{rated_sessions} rated session(s). "
                "Moderate focus — experiment with removing nearby distractions "
                "before each session to push this above 4."
            )
        else:
            recommendations.append(
                f"🎯 Strong focus: {focus:.1f}/5 average across "
                f"{rated_sessions} rated session(s). "
                "Keep protecting your distraction-free study time."
            )

    # ── 3. DISTRACTION TIME ──────────────────────────────────────────────────
    # Use associative language only — not causal.
    if distraction_per_session > 15:
        recommendations.append(
            f"📱 Average distraction is {distraction_per_session:.0f} min/session — "
            "higher than the recommended target. "
            "Sessions with lower distraction tend to coincide with better results. "
            "Try silencing notifications or using a site-blocker while studying."
        )
    elif distraction_per_session > 8:
        recommendations.append(
            f"📱 Average distraction is {distraction_per_session:.0f} min/session — "
            "moderate. Reducing interruptions further may help your study quality."
        )
    else:
        recommendations.append(
            f"📱 Distraction is well controlled "
            f"({distraction_per_session:.0f} min/session on average). "
            "Keep your current habits."
        )

    # ── 4. STUDY METHOD ──────────────────────────────────────────────────────
    # Only declare a "best method" when it has ≥ _MIN_SESSIONS_FOR_BEST_CLAIM
    # sessions AND those sessions include at least one recorded test score.
    if method_data.empty:
        recommendations.append(
            "📚 No study method data yet. "
            "Recording the method you use each session will let StudyFlow "
            "identify which approach works best for you."
        )
    else:
        qualified = method_data[
            (method_data["sessions"] >= _MIN_SESSIONS_FOR_BEST_CLAIM)
            & method_data["average_score"].notna()
        ]
        if qualified.empty:
            # Report how many sessions each method currently has
            below = method_data[method_data["sessions"] < _MIN_SESSIONS_FOR_BEST_CLAIM]
            if not below.empty:
                needed = _MIN_SESSIONS_FOR_BEST_CLAIM - int(below["sessions"].max())
                recommendations.append(
                    f"📚 Not enough data to identify your best study method yet "
                    f"(need {_MIN_SESSIONS_FOR_BEST_CLAIM} sessions per method with a recorded score). "
                    f"Add at least {max(needed, 1)} more scored session(s) to unlock this insight."
                )
            else:
                recommendations.append(
                    "📚 Study method data is available, but no test scores have been "
                    "recorded for any method yet. Add test scores to compare methods."
                )
        else:
            best = find_best_method(qualified)
            worst = qualified.sort_values("average_score").iloc[0]
            rec = (
                f"📚 Across your sessions with {_MIN_SESSIONS_FOR_BEST_CLAIM}+ results, "
                f"{best['study_method']} is associated with your highest average score "
                f"({best['average_score']:.1f}%)."
            )
            if best["study_method"] != worst["study_method"]:
                rec += (
                    f" {worst['study_method']} is currently your lowest-scoring method "
                    f"({worst['average_score']:.1f}%) — consider whether a different "
                    "approach or more practice time might help."
                )
            recommendations.append(rec)

    # ── 5. STUDY TIME (TIME OF DAY) ──────────────────────────────────────────
    if time_data.empty:
        recommendations.append(
            "🕐 No time-of-day data yet. "
            "Make sure each session has a start time recorded."
        )
    else:
        qualified_times = time_data[
            (time_data["sessions"] >= _MIN_SESSIONS_FOR_BEST_CLAIM)
            & time_data["average_score"].notna()
        ]
        if qualified_times.empty:
            # Find how close the most-studied period is to the threshold
            max_sessions = int(time_data["sessions"].max())
            still_needed = max(_MIN_SESSIONS_FOR_BEST_CLAIM - max_sessions, 1)
            recommendations.append(
                f"🕐 Not enough data to identify your most effective study time "
                f"(need {_MIN_SESSIONS_FOR_BEST_CLAIM} sessions per time period with a score). "
                f"Add {still_needed} more scored session(s) to enable this insight."
            )
        else:
            best_time = find_best_time(qualified_times)
            rec = (
                f"🕐 Based on {int(best_time['sessions'])} scored sessions, "
                f"{best_time['time_period']} is associated with your best average score "
                f"({best_time['average_score']:.1f}%). "
            )
            # Check whether sessions are actually well spread across periods
            periods_with_data = int((time_data["sessions"] >= _MIN_SESSIONS_FOR_BEST_CLAIM).sum())
            if periods_with_data == 1:
                rec += (
                    "You only have enough data for one time period so far — "
                    "try studying at different times to see how they compare."
                )
            else:
                rec += (
                    "Scheduling important study blocks in this period may help, "
                    "though other factors also influence performance."
                )
            recommendations.append(rec)

    # ── 6. SUBJECT PERFORMANCE ───────────────────────────────────────────────
    if not subject_data.empty:
        # Only compare subjects that have ≥2 sessions with scores
        scored_subjects = subject_data[
            subject_data["average_score"].notna()
            & (subject_data["sessions"] >= 2)
        ]
        if scored_subjects.empty:
            if total_sessions >= 2:
                recommendations.append(
                    "📖 Record test scores for your subjects so StudyFlow can "
                    "highlight which areas need the most attention."
                )
        elif len(scored_subjects) >= 2:
            weakest = scored_subjects.sort_values("average_score").iloc[0]
            strongest = scored_subjects.sort_values(
                "average_score", ascending=False
            ).iloc[0]
            if weakest["subject"] != strongest["subject"]:
                gap = float(strongest["average_score"]) - float(weakest["average_score"])
                recommendations.append(
                    f"📖 {weakest['subject']} has your lowest average score "
                    f"({weakest['average_score']:.1f}%) across "
                    f"{int(weakest['sessions'])} session(s). "
                    f"There is a {gap:.1f}-point gap to your strongest subject "
                    f"({strongest['subject']}, {strongest['average_score']:.1f}%). "
                    "Dedicating extra revision time to the weaker subject may help narrow this gap."
                )

    # ── 7. OVERALL TEST SCORE ────────────────────────────────────────────────
    if pd.isna(score):
        recommendations.append(
            "📈 No test scores recorded yet. "
            "Adding a score after each session lets StudyFlow track your "
            "performance trends over time."
        )
    else:
        scored_count = int(df["test_score"].notna().sum())
        if score >= 85:
            recommendations.append(
                f"📈 Strong overall performance: {score:.1f}% average across "
                f"{scored_count} scored session(s). "
                "Maintain consistency to keep this up."
            )
        elif score >= 75:
            recommendations.append(
                f"📈 Good performance: {score:.1f}% average across "
                f"{scored_count} scored session(s). "
                "Targeted practice on weaker topics could push this higher."
            )
        else:
            recommendations.append(
                f"📈 Average score is {score:.1f}% across "
                f"{scored_count} scored session(s). "
                "Prioritise active recall and practice problems over passive reading."
            )

    # ── 8. CONSISTENCY / STREAKS ─────────────────────────────────────────────
    if streak_days >= 7:
        recommendations.append(
            f"🔥 Excellent consistency! You have studied {streak_days} day(s) in a row. "
            "Maintaining a daily habit is one of the strongest predictors of "
            "long-term learning — keep it up."
        )
    elif streak_days >= 3:
        recommendations.append(
            f"🔥 Good momentum: {streak_days} consecutive study days. "
            "Aim to extend this streak — even a short 30-minute session on busy days "
            "helps preserve the habit."
        )
    elif streak_days == 1:
        recommendations.append(
            "🔥 You studied today — great start. "
            "Try to study again tomorrow to begin building a consistent streak."
        )
    elif total_sessions >= 3 and daily_data is not None and not daily_data.empty:
        # Streak is 0 but there is data — suggest restarting
        recommendations.append(
            "🔥 Your study streak has lapsed. "
            "Re-starting today is the fastest way to rebuild the habit. "
            "Even a short session counts."
        )

    # ── 9. WEEKLY GOAL PROGRESS ──────────────────────────────────────────────
    if weekly_goal_hours > 0:
        remaining = max(weekly_goal_hours - weekly_studied_hours, 0.0)
        pct = min(weekly_studied_hours / weekly_goal_hours * 100, 100)
        if weekly_studied_hours >= weekly_goal_hours:
            recommendations.append(
                f"🎯 Weekly goal achieved! You have studied "
                f"{weekly_studied_hours:.1f} h out of your "
                f"{weekly_goal_hours:.1f} h target this week. "
                "Consider setting a slightly higher goal next week to keep growing."
            )
        elif pct >= 70:
            recommendations.append(
                f"🎯 Almost there — {pct:.0f}% of your weekly goal completed "
                f"({weekly_studied_hours:.1f} / {weekly_goal_hours:.1f} h). "
                f"You need {remaining:.1f} more hour(s) to hit your target this week."
            )
        else:
            recommendations.append(
                f"🎯 Weekly progress: {pct:.0f}% "
                f"({weekly_studied_hours:.1f} / {weekly_goal_hours:.1f} h). "
                f"You still have {remaining:.1f} hour(s) to go this week."
            )

    return recommendations




if __name__ == "__main__":
    df = clean_data(load_data())

    print("\n" + "=" * 70)
    print("                     STUDY TIME ANALYZER")
    print("=" * 70)

    if df.empty:
        print("\nNo study data available.")
    else:
        metrics = calculate_metrics(df)
        subject_data = subject_analysis(df)
        method_data = study_method_analysis(df)
        time_data = time_of_day_analysis(df)
        duration_data = duration_score_analysis(df)
        focus_data = focus_score_analysis(df)
        distraction_data = distraction_score_analysis(df)
        progress = progress_analysis(df)

        print("\n===== OVERALL STUDY ANALYTICS =====")
        print(f"Total Study Hours       : {metrics['total_study_hours']:.2f}")
        print(f"Average Daily Hours     : {metrics['average_daily_hours']:.2f}")
        print(f"Average Focus Rating    : {metrics['average_focus']:.2f}/5")
        print(f"Total Distraction Time  : {metrics['total_distraction']:.2f} minutes")
        print(f"Average Test Score      : {metrics['average_score']:.2f}%")
        print(f"Total Study Sessions    : {metrics['total_sessions']}")

        print("\n===== SUBJECT ANALYSIS =====")
        print(subject_data.to_string(index=False))

        print("\n===== STUDY METHOD ANALYSIS =====")
        print(method_data.to_string(index=False))

        if not method_data.empty:
            best = find_best_method(method_data)
            print("\n===== BEST STUDY METHOD =====")
            print(f"Best Method            : {best['study_method']}")
            print(f"Average Score          : {best['average_score']:.2f}%")
            print(f"Average Focus          : {best['average_focus']:.2f}/5")

        print("\n===== TIME-OF-DAY ANALYSIS =====")
        print(time_data.to_string(index=False))

        if not time_data.empty:
            best = find_best_time(time_data)
            print("\n===== BEST TIME TO STUDY =====")
            print(f"Best Time Period       : {best['time_period']}")
            print(f"Average Score          : {best['average_score']:.2f}%")
            print(f"Average Focus          : {best['average_focus']:.2f}/5")

        print("\n===== STUDY DURATION VS TEST SCORE =====")
        print(duration_data.to_string(index=False))

        corr = calculate_correlation(df, "study_duration", "test_score")
        print("\n===== DURATION-SCORE CORRELATION =====")
        print(f"Correlation: {corr:.3f}")
        print(f"Interpretation: {correlation_interpretation(corr)}")

        print("\n===== FOCUS VS TEST SCORE =====")
        print(focus_data.to_string(index=False))

        corr = calculate_correlation(df, "focus_rating", "test_score")
        print("\n===== FOCUS-SCORE CORRELATION =====")
        print(f"Correlation: {corr:.3f}")
        print(f"Interpretation: {correlation_interpretation(corr)}")

        print("\n===== DISTRACTION VS TEST SCORE =====")
        print(distraction_data.to_string(index=False))

        corr = calculate_correlation(df, "distraction_time", "test_score")
        print("\n===== DISTRACTION-SCORE CORRELATION =====")
        print(f"Correlation: {corr:.3f}")
        print(f"Interpretation: {correlation_interpretation(corr)}")

        print("\n===== STUDY PERFORMANCE TREND =====")
        print(f"Study Hours Trend      : {progress['study_trend']}")
        print(f"Focus Trend            : {progress['focus_trend']}")
        print(f"Test Score Trend       : {progress['score_trend']}")
        print(f"Distraction Trend      : {progress['distraction_trend']}")

        print("\n===== PERSONALIZED RECOMMENDATIONS =====")
        for item in generate_recommendations(
            df, metrics, subject_data, method_data, time_data
        ):
            print("\n" + item)

    print("\n" + "=" * 70)

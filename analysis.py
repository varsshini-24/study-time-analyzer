import pandas as pd
import sqlite3
import numpy as np

DATABASE_PATH = "data/study.db"


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

    df = df.dropna(
        subset=["date", "subject", "study_duration",
                "focus_rating", "test_score"]
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


def generate_recommendations(df, metrics, subject_data, method_data, time_data):
    recommendations = []

    focus = metrics["average_focus"]
    distraction = metrics["total_distraction"] / max(metrics["total_sessions"], 1)
    score = metrics["average_score"]

    if focus < 3:
        recommendations.append("🎯 Focus is low. Use shorter distraction-free study blocks.")
    elif focus < 4:
        recommendations.append("🎯 Focus is moderate. Try reducing interruptions and using focused study blocks.")
    else:
        recommendations.append("🎯 Strong focus level. Keep protecting your distraction-free study time.")

    if distraction > 15:
        recommendations.append("📱 Distraction is high. Put your phone away or use app/site blockers during study.")
    elif distraction > 8:
        recommendations.append("📱 Distraction is moderate. Reducing interruptions can improve effectiveness.")
    else:
        recommendations.append("📱 Distraction is well controlled. Keep your current habits.")

    if not method_data.empty:
        best = find_best_method(method_data)
        recommendations.append(
            f"📚 Your strongest method is {best['study_method']} "
            f"with an average score of {best['average_score']:.1f}%."
        )

    if not time_data.empty:
        best_time = find_best_time(time_data)
        recommendations.append(
            f"🕐 Your best-performing period is {best_time['time_period']} "
            f"with an average score of {best_time['average_score']:.1f}%."
        )

    if not subject_data.empty:
        weakest = subject_data.sort_values("average_score").iloc[0]
        strongest = subject_data.sort_values("average_score", ascending=False).iloc[0]
        if weakest["subject"] != strongest["subject"]:
            recommendations.append(
                f"📖 Give extra revision time to {weakest['subject']} "
                f"(average score {weakest['average_score']:.1f}%)."
            )

    if score >= 85:
        recommendations.append("📈 Overall performance is strong. Focus on consistency to maintain it.")
    elif score >= 75:
        recommendations.append("📈 Performance is good. Improving focus and reducing distraction should help.")
    else:
        recommendations.append("📈 Test performance needs improvement. Prioritize practice and revision.")

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

import streamlit as st
import pandas as pd
from datetime import datetime, date

from database import create_database, add_session, get_all_sessions
from analysis import (
    load_data,
    clean_data,
    calculate_metrics,
    subject_analysis,
    study_method_analysis,
    find_best_method,
    time_of_day_analysis,
    find_best_time,
    duration_score_analysis,
    calculate_correlation,
    correlation_interpretation,
    focus_score_analysis,
    distraction_score_analysis,
    daily_analysis,
    progress_analysis,
    generate_recommendations,
)

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="StudyFlow | Study Time Analyzer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

create_database()

# ============================================================
# MODERN UI
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 90% 0%, rgba(124,58,237,.13), transparent 28%),
        radial-gradient(circle at 20% 100%, rgba(37,99,235,.08), transparent 30%),
        #0a0e16;
    color: #f5f7fb;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

.block-container {
    max-width: 1480px;
    padding: 30px 42px 55px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111722 0%, #0b1018 100%);
    border-right: 1px solid rgba(255,255,255,.07);
}

section[data-testid="stSidebar"] > div {
    padding: 24px 18px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 8px 25px;
}

.brand-icon {
    width: 44px;
    height: 44px;
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 23px;
    background: linear-gradient(135deg,#7c3aed,#2563eb);
    box-shadow: 0 12px 30px rgba(124,58,237,.25);
}

.brand-name {
    color: white;
    font-size: 18px;
    font-weight: 800;
}

.brand-sub {
    color: #788496;
    font-size: 9px;
    letter-spacing: 1.1px;
    margin-top: 3px;
}

.nav-label {
    color: #667386;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    margin: 4px 8px 9px;
}

.sidebar-footer {
    margin: 35px 5px 0;
    padding: 14px;
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 12px;
    color: #6f7b8d;
    font-size: 10px;
    line-height: 1.6;
}

/* Radio navigation */
div[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 5px;
}

div[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: transparent;
    border-radius: 10px;
    padding: 8px 10px;
    color: #aab4c3 !important;
}

div[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(139,92,246,.09);
    color: white !important;
}

/* Header */
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;
    margin-bottom: 28px;
}

.eyebrow {
    color: #9274f5;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.6px;
    margin-bottom: 7px;
}

.page-title {
    color: #ffffff;
    font-size: 34px;
    line-height: 1.15;
    font-weight: 800;
    letter-spacing: -.8px;
}

.page-subtitle {
    color: #7e8999;
    font-size: 13px;
    margin-top: 7px;
}

.date-pill {
    border: 1px solid rgba(255,255,255,.08);
    background: rgba(255,255,255,.025);
    border-radius: 20px;
    padding: 8px 13px;
    color: #9aa5b5;
    font-size: 11px;
}

/* Cards */
.card {
    background: linear-gradient(145deg, rgba(23,30,43,.97), rgba(15,21,31,.97));
    border: 1px solid rgba(255,255,255,.065);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,.12);
}

.card-title {
    color: #eef2f7;
    font-size: 13px;
    font-weight: 750;
}

.card-muted {
    color: #778395;
    font-size: 11px;
    line-height: 1.55;
    margin-top: 4px;
}

.kpi {
    min-height: 125px;
}

.kpi-icon {
    font-size: 19px;
    margin-bottom: 12px;
}

.kpi-value {
    color: white;
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -.5px;
}

.kpi-label {
    color: #7b8798;
    font-size: 10px;
    margin-top: 4px;
}

.section-heading {
    color: white;
    font-size: 17px;
    font-weight: 750;
    margin: 27px 0 12px;
}

.insight {
    background: linear-gradient(145deg,#151c28,#111721);
    border: 1px solid rgba(255,255,255,.065);
    border-radius: 14px;
    padding: 16px;
    min-height: 100px;
}

.insight-icon { font-size: 18px; margin-bottom: 8px; }
.insight-title { color: #e3e8ef; font-size: 12px; font-weight: 750; }
.insight-text { color: #7d8999; font-size: 11px; line-height: 1.55; margin-top: 5px; }

/* Streamlit widgets */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg,#151c28,#111721);
    border: 1px solid rgba(255,255,255,.065);
    border-radius: 14px;
    padding: 16px 18px;
}

div[data-testid="stMetricLabel"] { color: #7f8b9c; }
div[data-testid="stMetricValue"] { color: white; font-weight: 800; }

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background: #171d29 !important;
    border-color: rgba(255,255,255,.08) !important;
    border-radius: 10px !important;
}

input, textarea { color: white !important; }
label { color: #aeb8c7 !important; font-size: 11px !important; }

.stButton > button {
    border-radius: 10px;
    border: 1px solid rgba(139,92,246,.28);
    background: linear-gradient(135deg,#7c3aed,#2563eb);
    color: white;
    font-weight: 750;
    padding: 10px 18px;
    transition: all .2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 25px rgba(59,130,246,.22);
}

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,.065);
    border-radius: 12px;
    overflow: hidden;
}

.stAlert { border-radius: 12px; }
hr { border-color: rgba(255,255,255,.07); }

@media (max-width: 900px) {
    .block-container { padding: 22px 18px 40px; }
    .page-title { font-size: 26px; }
    .topbar { flex-direction: column; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================

def header(title, subtitle, icon="📚"):
    today = datetime.now().strftime("%d %b %Y")
    st.markdown(f"""
    <div class="topbar">
        <div>
            <div class="eyebrow">{icon} STUDY TIME ANALYZER</div>
            <div class="page-title">{title}</div>
            <div class="page-subtitle">{subtitle}</div>
        </div>
        <div class="date-pill">📅 {today}</div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(icon, value, label):
    st.markdown(f"""
    <div class="card kpi">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def insight_card(icon, title, text):
    st.markdown(f"""
    <div class="insight">
        <div class="insight-icon">{icon}</div>
        <div class="insight-title">{title}</div>
        <div class="insight-text">{text}</div>
    </div>
    """, unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="section-heading">{title}</div>', unsafe_allow_html=True)


def safe_corr(value):
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def clean_chart_frame(frame, columns):
    if frame.empty:
        return frame
    result = frame.copy()
    for col in columns:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")
    return result.dropna(subset=[c for c in columns if c in result.columns])


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">📚</div>
        <div>
            <div class="brand-name">StudyFlow</div>
            <div class="brand-sub">STUDY TIME ANALYZER</div>
        </div>
    </div>
    <div class="nav-label">Workspace</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "➕ Add Study Session",
            "📚 Study History",
            "📊 Analytics",
            "🎯 Focus & Distraction",
            "📈 Trends & Insights",
            "💡 Recommendations",
        ],
        label_visibility="collapsed",
    )

    st.markdown("""
    <div class="sidebar-footer">
        <b style="color:#b7c0ce;">StudyFlow</b><br>
        Personal learning analytics powered by Python, Pandas, SQLite and Streamlit.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# ADD SESSION
# ============================================================

if page == "➕ Add Study Session":
    header(
        "Add Study Session",
        "Record a session and let StudyFlow calculate the duration automatically.",
        "➕",
    )

    left, right = st.columns([1.25, 1], gap="large")

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📝 Session details")

        date_value = st.date_input("Study Date", value=date.today())
        subject = st.text_input(
            "Subject",
            placeholder="e.g. Python, SQL, Statistics"
        )

        c1, c2 = st.columns(2)
        with c1:
            start_time = st.time_input(
                "Start Time",
                value=datetime.now().time().replace(second=0, microsecond=0)
            )
        with c2:
            end_time = st.time_input(
                "End Time",
                value=datetime.now().time().replace(second=0, microsecond=0)
            )

        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute

        if end_minutes >= start_minutes:
            duration_minutes = end_minutes - start_minutes
        else:
            duration_minutes = (24 * 60 - start_minutes) + end_minutes

        study_duration = duration_minutes / 60

        st.markdown(f"""
        <div style="
            margin-top:14px;padding:15px;border-radius:11px;
            background:linear-gradient(90deg,rgba(124,58,237,.14),rgba(59,130,246,.10));
            border:1px solid rgba(139,92,246,.18);
        ">
            <span style="color:#8995a6;font-size:10px;">CALCULATED STUDY DURATION</span><br>
            <span style="color:white;font-size:23px;font-weight:800;">⏱ {study_duration:.2f} hours</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Performance details")

        break_duration = st.number_input(
            "Break Duration (minutes)", min_value=0.0, step=5.0, value=0.0
        )
        distraction_time = st.number_input(
            "Distraction Time (minutes)", min_value=0.0, step=5.0, value=0.0
        )
        study_method = st.selectbox(
            "Study Method",
            ["Reading", "Practice", "Video", "Notes", "Revision", "Problem Solving"],
        )
        focus_rating = st.slider("Focus Rating", 1, 5, 3)
        test_score = st.number_input(
            "Test Score (%)", min_value=0.0, max_value=100.0, step=1.0, value=0.0
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    if st.button("➕  Save Study Session", type="primary", width="stretch"):
        if not subject.strip():
            st.error("Please enter a subject.")
        elif study_duration <= 0:
            st.error("Study duration must be greater than 0.")
        else:
            add_session(
                str(date_value),
                subject.strip(),
                str(start_time),
                str(end_time),
                study_duration,
                break_duration,
                distraction_time,
                study_method,
                focus_rating,
                test_score,
            )
            st.success("Study session added successfully! 🎉")
            st.rerun()

# ============================================================
# HISTORY
# ============================================================

elif page == "📚 Study History":
    header(
        "Study History",
        "Review every session recorded in your learning database.",
        "📚",
    )

    sessions = get_all_sessions()

    if not sessions:
        st.markdown("""
        <div class="card" style="text-align:center;padding:55px 20px;">
            <div style="font-size:45px;">📚</div>
            <div style="font-size:22px;font-weight:800;margin-top:10px;">
                No sessions yet
            </div>
            <div class="card-muted">
                Add your first study session to start building your learning history.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        rows = []
        for session in sessions:
            (
                session_id, session_date, subject_name, start, end,
                duration, break_time, distraction, method, focus, score
            ) = session

            rows.append({
                "Date": session_date,
                "Subject": subject_name,
                "Start": start,
                "End": end,
                "Study Hours": round(float(duration), 2),
                "Break (min)": round(float(break_time or 0), 1),
                "Distraction (min)": round(float(distraction or 0), 1),
                "Method": method,
                "Focus": focus,
                "Score (%)": score,
            })

        history_df = pd.DataFrame(rows)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Sessions", len(history_df))
        c2.metric("Subjects", history_df["Subject"].nunique())
        c3.metric("Average Score", f"{history_df['Score (%)'].mean():.1f}%")

        st.write("")
        st.dataframe(history_df, width="stretch", hide_index=True)

# ============================================================
# OVERVIEW
# ============================================================

elif page == "🏠 Overview":
    df = clean_data(load_data())

    if df.empty:
        header(
            "Welcome to StudyFlow 👋",
            "Start by adding your first study session.",
            "🏠",
        )
        st.markdown("""
        <div class="card" style="text-align:center;padding:55px 20px;">
            <div style="font-size:48px;">🚀</div>
            <div style="font-size:24px;font-weight:800;margin-top:10px;">
                Your learning dashboard is ready
            </div>
            <div class="card-muted">
                Add a study session to unlock your analytics and personalized insights.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        metrics = calculate_metrics(df)
        subjects = subject_analysis(df)
        methods = study_method_analysis(df)
        times = time_of_day_analysis(df)
        daily = daily_analysis(df)
        progress = progress_analysis(df)

        header(
            "Good Evening 👋",
            "Here's your current study performance at a glance.",
            "🏠",
        )

        cols = st.columns(5)
        values = [
            ("⏱️", f"{metrics['total_study_hours']:.1f}h", "Total Study Time"),
            ("📚", str(metrics["total_sessions"]), "Study Sessions"),
            ("🎯", f"{metrics['average_focus']:.1f}/5", "Average Focus"),
            ("📈", f"{metrics['average_score']:.1f}%", "Average Score"),
            ("📱", f"{metrics['total_distraction']:.0f}m", "Distraction Time"),
        ]

        for col, (icon, value, label) in zip(cols, values):
            with col:
                kpi_card(icon, value, label)

        section("Performance Overview")

        left, right = st.columns([1.65, 1], gap="large")

        with left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**📈 Study Performance**")
            st.caption("Daily study hours")
            if not daily.empty:
                chart = clean_chart_frame(
                    daily.set_index("date"), ["study_hours"]
                )
                st.line_chart(chart[["study_hours"]], height=280)
            else:
                st.info("Not enough daily data yet.")
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**📚 Subject Performance**")
            st.caption("Average score by subject")
            if not subjects.empty:
                chart = clean_chart_frame(
                    subjects.set_index("subject"), ["average_score"]
                )
                st.bar_chart(chart[["average_score"]], height=280)
            else:
                st.info("No subject data.")
            st.markdown("</div>", unsafe_allow_html=True)

        left, right = st.columns(2, gap="large")

        with left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**🧠 Study Methods**")
            st.caption("Average score by study method")
            if not methods.empty:
                chart = clean_chart_frame(
                    methods.set_index("study_method"), ["average_score"]
                )
                st.bar_chart(chart[["average_score"]], height=230)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**🕐 Best Study Time**")
            st.caption("Average score by time of day")
            if not times.empty:
                chart = clean_chart_frame(
                    times.set_index("time_period"), ["average_score"]
                )
                st.bar_chart(chart[["average_score"]], height=230)
            st.markdown("</div>", unsafe_allow_html=True)

        section("Quick Insights")

        best_method = find_best_method(methods) if not methods.empty else None
        best_time = find_best_time(times) if not times.empty else None

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            insight_card(
                "🏆",
                "Best Study Method",
                (
                    f"{best_method['study_method']} · "
                    f"{best_method['average_score']:.1f}% average score"
                    if best_method is not None
                    else "Not enough data"
                ),
            )

        with c2:
            insight_card(
                "🌅",
                "Best Study Period",
                (
                    f"{best_time['time_period']} · "
                    f"{best_time['average_score']:.1f}% average score"
                    if best_time is not None
                    else "Not enough data"
                ),
            )

        with c3:
            insight_card(
                "🎯",
                "Focus Impact",
                f"Focus ↔ Score: {safe_corr(calculate_correlation(df, 'focus_rating', 'test_score')):.3f}",
            )

        with c4:
            insight_card(
                "📱",
                "Distraction Impact",
                f"Distraction ↔ Score: {safe_corr(calculate_correlation(df, 'distraction_time', 'test_score')):.3f}",
            )

        section("Progress Snapshot")

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Score Change", f"{progress['score_change']:+.2f}")
        p2.metric("Focus Change", f"{progress['focus_change']:+.2f}")
        p3.metric("Study Hours Change", f"{progress['study_hours_change']:+.2f}")
        p4.metric("Distraction Change", f"{progress['distraction_change']:+.2f} min")

# ============================================================
# ANALYTICS
# ============================================================

elif page == "📊 Analytics":
    df = clean_data(load_data())

    if df.empty:
        header("Analytics", "Detailed analysis of your study behavior.", "📊")
        st.info("Add study sessions to unlock analytics.")
    else:
        header(
            "Detailed Analytics",
            "Explore the relationships between your study habits and performance.",
            "📊",
        )

        metrics = calculate_metrics(df)

        cols = st.columns(5)
        kpis = [
            ("⏱️", f"{metrics['total_study_hours']:.1f}h", "Study Time"),
            ("📚", str(metrics["total_sessions"]), "Sessions"),
            ("🎯", f"{metrics['average_focus']:.1f}/5", "Focus"),
            ("📈", f"{metrics['average_score']:.1f}%", "Average Score"),
            ("📱", f"{metrics['total_distraction']:.0f}m", "Distraction"),
        ]

        for col, (icon, value, label) in zip(cols, kpis):
            with col:
                kpi_card(icon, value, label)

        st.write("")

        tabs = st.tabs([
            "📚 Subjects",
            "🧠 Methods",
            "🕐 Time",
            "⏱ Duration",
            "🎯 Focus",
            "📱 Distraction",
            "📈 Progress",
        ])

        with tabs[0]:
            data = subject_analysis(df)
            if not data.empty:
                st.dataframe(data, width="stretch", hide_index=True)
                st.bar_chart(
                    clean_chart_frame(
                        data.set_index("subject"), ["average_score"]
                    )[["average_score"]],
                    height=320,
                )

        with tabs[1]:
            data = study_method_analysis(df)
            if not data.empty:
                best = find_best_method(data)
                st.success(
                    f"🏆 Best method: {best['study_method']} · "
                    f"{best['average_score']:.1f}% average score"
                )
                st.dataframe(data, width="stretch", hide_index=True)
                st.bar_chart(
                    clean_chart_frame(
                        data.set_index("study_method"), ["average_score"]
                    )[["average_score"]],
                    height=320,
                )

        with tabs[2]:
            data = time_of_day_analysis(df)
            if not data.empty:
                best = find_best_time(data)
                st.success(
                    f"⏰ Best time: {best['time_period']} · "
                    f"{best['average_score']:.1f}% average score"
                )
                st.dataframe(data, width="stretch", hide_index=True)
                st.bar_chart(
                    clean_chart_frame(
                        data.set_index("time_period"), ["average_score"]
                    )[["average_score"]],
                    height=320,
                )

        with tabs[3]:
            data = duration_score_analysis(df)
            corr = safe_corr(
                calculate_correlation(df, "study_duration", "test_score")
            )
            st.metric("Duration ↔ Score Correlation", f"{corr:.3f}")
            st.caption(correlation_interpretation(corr))
            if not data.empty:
                st.dataframe(data, width="stretch", hide_index=True)
                chart = data.set_index("duration_group")[["average_score"]]
                st.bar_chart(chart, height=320)

        with tabs[4]:
            data = focus_score_analysis(df)
            corr = safe_corr(
                calculate_correlation(df, "focus_rating", "test_score")
            )
            st.metric("Focus ↔ Score Correlation", f"{corr:.3f}")
            st.caption(correlation_interpretation(corr))
            if not data.empty:
                st.dataframe(data, width="stretch", hide_index=True)
                st.line_chart(
                    data.set_index("focus_rating")[["average_score"]],
                    height=320,
                )

        with tabs[5]:
            data = distraction_score_analysis(df)
            corr = safe_corr(
                calculate_correlation(df, "distraction_time", "test_score")
            )
            st.metric("Distraction ↔ Score Correlation", f"{corr:.3f}")
            st.caption(correlation_interpretation(corr))
            if not data.empty:
                st.dataframe(data, width="stretch", hide_index=True)
                st.bar_chart(
                    data.set_index("distraction_group")[["average_score"]],
                    height=320,
                )

        with tabs[6]:
            progress = progress_analysis(df)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Score Change", f"{progress['score_change']:+.2f}")
            c2.metric("Focus Change", f"{progress['focus_change']:+.2f}")
            c3.metric("Study Hours Change", f"{progress['study_hours_change']:+.2f}")
            c4.metric("Distraction Change", f"{progress['distraction_change']:+.2f} min")

            st.markdown(f"""
            <div class="card">
                <div class="card-title">Performance Trends</div>
                <p class="card-muted">Study Hours: {progress['study_trend']}</p>
                <p class="card-muted">Focus: {progress['focus_trend']}</p>
                <p class="card-muted">Test Score: {progress['score_trend']}</p>
                <p class="card-muted">Distraction: {progress['distraction_trend']}</p>
            </div>
            """, unsafe_allow_html=True)

            daily = daily_analysis(df)
            if not daily.empty:
                st.line_chart(
                    daily.set_index("date")[["study_hours", "average_score"]],
                    height=330,
                )

# ============================================================
# FOCUS & DISTRACTION
# ============================================================

elif page == "🎯 Focus & Distraction":
    df = clean_data(load_data())

    if df.empty:
        header(
            "Focus & Distraction",
            "Understand what affects your performance.",
            "🎯",
        )
        st.info("Add study sessions to see this analysis.")
    else:
        header(
            "Focus & Distraction",
            "See how concentration and interruptions relate to test performance.",
            "🎯",
        )

        focus_corr = safe_corr(
            calculate_correlation(df, "focus_rating", "test_score")
        )
        distraction_corr = safe_corr(
            calculate_correlation(df, "distraction_time", "test_score")
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Average Focus", f"{df['focus_rating'].mean():.2f}/5")
        c2.metric("Focus ↔ Score", f"{focus_corr:.3f}")
        c3.metric("Distraction ↔ Score", f"{distraction_corr:.3f}")
        c4.metric("Avg Distraction", f"{df['distraction_time'].mean():.1f} min")

        section("Relationship Analysis")

        left, right = st.columns(2, gap="large")

        with left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**🎯 Focus vs Test Score**")
            st.caption("Higher focus should ideally correspond to stronger results.")
            data = focus_score_analysis(df)
            if not data.empty:
                st.line_chart(
                    data.set_index("focus_rating")[["average_score"]],
                    height=300,
                )
                st.caption(f"Correlation: {focus_corr:.3f}")
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**📱 Distraction vs Test Score**")
            st.caption("See how interruptions relate to performance.")
            data = distraction_score_analysis(df)
            if not data.empty:
                st.bar_chart(
                    data.set_index("distraction_group")[["average_score"]],
                    height=300,
                )
                st.caption(f"Correlation: {distraction_corr:.3f}")
            st.markdown("</div>", unsafe_allow_html=True)

        section("Actionable Insight")

        if focus_corr >= 0.7:
            st.success("🎯 Focus has a strong positive relationship with your test scores. Protect distraction-free study time.")
        elif focus_corr >= 0.3:
            st.info("🎯 Focus has a moderate positive relationship with your test scores. Improving concentration may help.")
        else:
            st.warning("🎯 Your current data does not show a strong focus-score relationship yet.")

        if distraction_corr <= -0.7:
            st.success("📱 Distraction has a strong negative relationship with scores. Reducing interruptions should be a priority.")
        elif distraction_corr <= -0.3:
            st.info("📱 Distraction has a moderate negative relationship with scores.")
        else:
            st.warning("📱 Your current data does not show a strong distraction-score relationship yet.")

# ============================================================
# TRENDS
# ============================================================

elif page == "📈 Trends & Insights":
    df = clean_data(load_data())

    if df.empty:
        header(
            "Trends & Insights",
            "Track how your study behavior changes over time.",
            "📈",
        )
        st.info("Add study sessions to generate trends.")
    else:
        header(
            "Trends & Insights",
            "Understand whether your study habits are improving over time.",
            "📈",
        )

        progress = progress_analysis(df)
        daily = daily_analysis(df)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Study Trend", progress["study_trend"])
        c2.metric("Focus Trend", progress["focus_trend"])
        c3.metric("Score Trend", progress["score_trend"])
        c4.metric("Distraction Trend", progress["distraction_trend"])

        section("Daily Performance")

        if not daily.empty:
            st.line_chart(
                daily.set_index("date")[
                    ["study_hours", "average_focus", "average_score"]
                ],
                height=380,
            )

        section("Latest Progress")

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Score Change", f"{progress['score_change']:+.2f}")
        p2.metric("Focus Change", f"{progress['focus_change']:+.2f}")
        p3.metric("Study Hours Change", f"{progress['study_hours_change']:+.2f}")
        p4.metric("Distraction Change", f"{progress['distraction_change']:+.2f} min")

        st.markdown(f"""
        <div class="card" style="margin-top:16px;">
            <div class="card-title">📊 Performance Summary</div>
            <p class="card-muted">Study Hours: {progress['study_trend']}</p>
            <p class="card-muted">Focus: {progress['focus_trend']}</p>
            <p class="card-muted">Test Score: {progress['score_trend']}</p>
            <p class="card-muted">Distraction: {progress['distraction_trend']}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# RECOMMENDATIONS
# ============================================================

elif page == "💡 Recommendations":
    df = clean_data(load_data())

    if df.empty:
        header(
            "Personalized Recommendations",
            "Actionable suggestions based on your study behavior.",
            "💡",
        )
        st.info("Add study sessions to generate personalized recommendations.")
    else:
        header(
            "Personalized Recommendations",
            "Actionable suggestions generated from your study behavior.",
            "💡",
        )

        metrics = calculate_metrics(df)
        subjects = subject_analysis(df)
        methods = study_method_analysis(df)
        times = time_of_day_analysis(df)

        recommendations = generate_recommendations(
            df, metrics, subjects, methods, times
        )

        for index, recommendation in enumerate(recommendations, start=1):
            parts = recommendation.split(" ", 1)
            icon = parts[0] if len(parts) > 1 else "💡"
            text = parts[1] if len(parts) > 1 else recommendation

            st.markdown(f"""
            <div class="insight" style="margin-bottom:12px;">
                <div class="insight-icon">{icon}</div>
                <div class="insight-title">Recommendation {index}</div>
                <div class="insight-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)

        st.success(
            "💡 These recommendations are based on your recorded study behavior "
            "and will become more useful as you add more sessions."
        )

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div style="
    text-align:center;
    color:#566173;
    font-size:10px;
    margin-top:40px;
    padding-top:18px;
    border-top:1px solid rgba(255,255,255,.05);
">
    StudyFlow • Personal Study Analytics • Python + Pandas + SQLite + Streamlit
</div>
""", unsafe_allow_html=True)

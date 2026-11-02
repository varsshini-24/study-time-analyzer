import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime, date, timedelta

from database import (
    create_database, add_session, get_all_sessions,
    get_weekly_goals, save_weekly_goal, delete_weekly_goal,
)
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

/* StudyFlow premium refresh: restrained glass surfaces, clearer hierarchy */
:root {
    color-scheme: dark;
    --sf-bg: #090d16;
    --sf-surface: rgba(18, 25, 39, .88);
    --sf-border: rgba(148, 163, 184, .14);
    --sf-muted: #8d9bb0;
    --sf-purple: #a78bfa;
    --sf-blue: #60a5fa;
}

.stApp {
    background:
        radial-gradient(ellipse at 82% 2%, rgba(124, 58, 237, .16), transparent 34%),
        radial-gradient(ellipse at 2% 52%, rgba(37, 99, 235, .09), transparent 30%),
        linear-gradient(145deg, #090d16 0%, #0b1120 55%, #090d16 100%);
}

.block-container { padding-top: 2.2rem; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(17, 24, 39, .98), rgba(9, 13, 22, .98));
    border-right: 1px solid var(--sf-border);
}
.brand-icon {
    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
    box-shadow: 0 8px 28px rgba(124, 58, 237, .32), inset 0 1px 0 rgba(255,255,255,.18);
}
.brand-name { letter-spacing: -.35px; }
.brand-sub { letter-spacing: 1.55px; }

.topbar {
    align-items: center;
    padding: 0 0 22px;
    border-bottom: 1px solid rgba(148, 163, 184, .12);
    margin-bottom: 25px;
}
.eyebrow { color: #a78bfa; letter-spacing: 1.8px; }
.page-title { letter-spacing: -1.2px; line-height: 1.12; }
.page-subtitle { max-width: 720px; line-height: 1.7; }
.date-pill {
    white-space: nowrap;
    background: rgba(17, 24, 39, .78);
    border-color: rgba(148, 163, 184, .16);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.025);
}

.card, .insight, div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(22, 30, 46, .94), rgba(13, 19, 31, .96));
    border: 1px solid var(--sf-border);
    box-shadow: 0 12px 34px rgba(0, 0, 0, .13), inset 0 1px 0 rgba(255,255,255,.025);
    transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease;
}
.card { border-radius: 18px; }
.insight { border-radius: 16px; }
.card:hover, .insight:hover {
    border-color: rgba(167, 139, 250, .28);
    box-shadow: 0 16px 38px rgba(0,0,0,.18), 0 0 0 1px rgba(167,139,250,.025);
}
.kpi { min-height: 138px; position: relative; overflow: hidden; }
.kpi:after {
    content: ""; position: absolute; top: -35px; right: -30px;
    width: 90px; height: 90px; border-radius: 50%;
    background: radial-gradient(circle, rgba(139,92,246,.12), transparent 72%);
    pointer-events: none;
}
.kpi-icon { margin-bottom: 15px; }
.kpi-value { font-size: clamp(22px, 2vw, 29px); letter-spacing: -1px; }
.kpi-label { font-size: 11px; letter-spacing: .15px; }
.section-heading { margin-top: 31px; margin-bottom: 14px; letter-spacing: -.25px; }
.insight { min-height: 112px; }
.insight-title { font-size: 12px; }
.insight-text { font-size: 11px; }

/* Navigation and form controls */
div[data-testid="stSidebar"] div[role="radiogroup"] label {
    border: 1px solid transparent;
    transition: background .15s ease, border-color .15s ease;
}
div[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(139, 92, 246, .11);
    border-color: rgba(139, 92, 246, .12);
}
.stButton > button, .stDownloadButton > button, button[kind="primary"] {
    min-height: 42px;
    border-radius: 11px;
    border: 1px solid rgba(167, 139, 250, .30);
    background: linear-gradient(115deg, #7c3aed, #315fce);
    box-shadow: 0 7px 20px rgba(79, 70, 229, .13);
}
.stButton > button:focus, .stDownloadButton > button:focus {
    box-shadow: 0 0 0 3px rgba(167, 139, 250, .2);
}
input, textarea { caret-color: #a78bfa; }

/* Plotly charts blend into the dashboard instead of appearing as white panels */
div[data-testid="stPlotlyChart"] {
    border-radius: 12px;
    overflow: hidden;
}
div[data-testid="stDataFrame"] { border-color: var(--sf-border); }
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom-color: var(--sf-border); }
.stTabs [data-baseweb="tab"] { border-radius: 9px 9px 0 0; padding: 9px 13px; }
.stTabs [aria-selected="true"] { color: #c4b5fd !important; }
.stAlert { border: 1px solid var(--sf-border); }
.sidebar-footer { background: rgba(255,255,255,.015); }

@media (max-width: 900px) {
    .block-container { padding: 18px 14px 32px; }
    .page-title { font-size: 27px; }
    .kpi { min-height: 118px; }
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { transition: none !important; animation: none !important; }
}

/* ============================================================
   STUDYFLOW SIDEBAR — PREMIUM NAVIGATION OVERRIDE
   Added after the existing styles so it takes priority.
============================================================ */

section[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 10% 0%, rgba(124, 58, 237, .12), transparent 34%),
        linear-gradient(180deg, #101727 0%, #0b1120 58%, #090e18 100%) !important;
    border-right: 1px solid rgba(148, 163, 184, .14) !important;
}

section[data-testid="stSidebar"] > div {
    padding: 26px 16px 22px !important;
}

/* Brand block */
section[data-testid="stSidebar"] .brand {
    gap: 13px;
    padding: 8px 8px 30px;
}

section[data-testid="stSidebar"] .brand-icon {
    width: 46px;
    height: 46px;
    flex-shrink: 0;
    border-radius: 15px;
    font-size: 22px;
    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
    box-shadow: 0 8px 25px rgba(124, 58, 237, .28),
                inset 0 1px 0 rgba(255, 255, 255, .16);
}

section[data-testid="stSidebar"] .brand-name {
    color: #f8fafc;
    font-size: 19px;
    font-weight: 800;
    letter-spacing: -.45px;
}

section[data-testid="stSidebar"] .brand-sub {
    color: #8795ad;
    font-size: 9px;
    letter-spacing: 1.5px;
    margin-top: 4px;
}

section[data-testid="stSidebar"] .nav-label {
    color: #7787a1;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.7px;
    margin: 0 10px 13px;
}

/* Navigation group */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 6px !important;
}

/* Each navigation item */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
    margin: 0 !important;
    padding: 11px 12px !important;
    border: 1px solid transparent !important;
    border-radius: 11px !important;
    background: transparent !important;
    color: #aab6ca !important;
    cursor: pointer;
    transition: background .18s ease, border-color .18s ease, color .18s ease;
}

/* Hide the radio control/circle, keeping the label clickable */
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* Let the text use the full navigation width */
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:last-child {
    width: 100% !important;
    flex: 1 1 auto !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: inherit !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    line-height: 1.45 !important;
    margin: 0 !important;
}

/* Hover state */
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(139, 92, 246, .10) !important;
    border-color: rgba(167, 139, 250, .16) !important;
    color: #f8fafc !important;
}

/* Active item */
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(
        100deg,
        rgba(124, 58, 237, .24),
        rgba(59, 130, 246, .11)
    ) !important;
    border-color: rgba(167, 139, 250, .25) !important;
    box-shadow: inset 3px 0 0 #a78bfa !important;
    color: #ffffff !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Footer card */
section[data-testid="stSidebar"] .sidebar-footer {
    margin: 32px 3px 0 !important;
    padding: 15px !important;
    border: 1px solid rgba(148, 163, 184, .13) !important;
    border-radius: 14px !important;
    background: linear-gradient(145deg, rgba(255,255,255,.035), rgba(255,255,255,.012)) !important;
    color: #8795aa !important;
    font-size: 10px !important;
    line-height: 1.75 !important;
}

section[data-testid="stSidebar"] .sidebar-footer b {
    color: #e2e8f0 !important;
    font-size: 12px !important;
}

/* Keep sidebar polished on smaller screens */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] > div {
        padding: 20px 12px !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 10px 10px !important;
    }
}
/* Remove Streamlit radio circles and their reserved space */
section[data-testid="stSidebar"]
div[data-testid="stRadio"] div[role="radiogroup"] label
> div:first-child {
    display: none !important;
}

/* Make navigation items fill the sidebar width */
section[data-testid="stSidebar"]
div[data-testid="stRadio"] div[role="radiogroup"] label {
    width: 100% !important;
    box-sizing: border-box !important;
    padding: 10px 12px !important;
    margin: 3px 0 !important;
    border-radius: 10px !important;
}

/* Keep navigation text aligned */
section[data-testid="stSidebar"]
div[data-testid="stRadio"] div[role="radiogroup"] label > div:last-child {
    margin-left: 0 !important;
    padding-left: 0 !important;
}

/* Highlight the selected page */
section[data-testid="stSidebar"]
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    background: rgba(139, 92, 246, 0.18) !important;
    border: 1px solid rgba(167, 139, 250, 0.3) !important;
    box-shadow: inset 3px 0 0 #a78bfa !important;
}
/* ===== FIX STUDYFLOW DASHBOARD WIDTH ===== */

/* Keep the sidebar at a reasonable width */
section[data-testid="stSidebar"] {
    min-width: 235px !important;
    max-width: 235px !important;
}

/* Restore the main content area */
section[data-testid="stMain"] > div {
    max-width: 100% !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}

/* Prevent dashboard metric cards from becoming too narrow */
div[data-testid="stMetric"] {
    min-width: 0 !important;
    width: 100% !important;
}

div[data-testid="stMetricValue"] {
    font-size: clamp(1.2rem, 1.8vw, 2rem) !important;
    white-space: nowrap !important;
}

/* Keep chart containers responsive */
div[data-testid="stPlotlyChart"] {
    width: 100% !important;
    min-width: 0 !important;
}

/* Avoid horizontal overflow */
.stApp {
    overflow-x: hidden;
}

/* Keep sidebar navigation tidy */
section[data-testid="stSidebar"]
div[data-testid="stRadio"] label {
    width: 100% !important;
    box-sizing: border-box !important;
}
/* ===== STUDYFLOW RESPONSIVE CHART FIX ===== */

/* Let the main content use the available width */
section[data-testid="stMain"] {
    min-width: 0 !important;
}

section[data-testid="stMain"] > div {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

/* Prevent chart columns from forcing horizontal overflow */
div[data-testid="stHorizontalBlock"] {
    width: 100% !important;
    max-width: 100% !important;
    gap: 1.25rem !important;
}

div[data-testid="column"] {
    min-width: 0 !important;
    box-sizing: border-box !important;
}

/* Keep Plotly charts within their columns */
div[data-testid="stPlotlyChart"] {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    overflow: hidden !important;
}

div[data-testid="stPlotlyChart"] iframe {
    max-width: 100% !important;
}

/* Keep chart headings readable */
div[data-testid="column"] h3,
div[data-testid="column"] h4 {
    overflow-wrap: anywhere;
}

/* Slightly reduce main content padding on smaller screens */
@media (max-width: 1100px) {
    section[data-testid="stMain"] > div {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
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


def apply_premium_chart_style(fig, height=280):
    """Apply StudyFlow's dark dashboard style to Plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        autosize=True,
        margin=dict(l=8, r=8, t=18, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#9aa8bc", size=11),
        hoverlabel=dict(bgcolor="#151d2c", bordercolor="#374151", font_color="#f8fafc"),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(148,163,184,.12)", tickfont=dict(color="#8795aa"))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,.10)", zeroline=False, linecolor="rgba(148,163,184,.10)", tickfont=dict(color="#8795aa") )
    return fig


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
            "🔥 Study Consistency",
            "🎯 Weekly Goals",
            "📄 Study Reports",
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


    with right:
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

        current_hour = datetime.now().hour
        greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 17 else "Good evening"
        header(
            f"{greeting} 👋",
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
            st.markdown("**📈 Study Performance**")
            st.caption("Daily study hours")
            if not daily.empty:
                chart = daily.copy()
                fig = px.area(
                    chart, x="date", y="study_hours",
                    labels={"date": "Study date", "study_hours": "Study hours"},
                    markers=True,
                )
                fig.update_traces(
                    line=dict(color="#a78bfa", width=3),
                    fillcolor="rgba(139,92,246,.13)",
                    marker=dict(size=6, color="#c4b5fd", line=dict(width=1, color="#111827")),
                    hovertemplate="%{x|%d %b %Y}<br><b>%{y:.2f} hours</b><extra></extra>",
                )
                fig.update_yaxes(rangemode="tozero")
                st.plotly_chart(apply_premium_chart_style(fig, 280), width="stretch", config={"displayModeBar": False, "responsive": True})
            else:
                st.info("Not enough daily data yet.")

        with right:
            st.markdown("**📚 Subject Performance**")
            st.caption("Average score by subject")
            if not subjects.empty:
                chart = subjects.sort_values("average_score", ascending=True).copy()
                chart["average_score"] = pd.to_numeric(
                    chart["average_score"], errors="coerce"
                )
                chart = chart.dropna(subset=["average_score"])

                if not chart.empty:
                    fig = px.bar(
                        chart,
                        x="average_score",
                        y="subject",
                        orientation="h",
                        labels={
                            "average_score": "Average score (%)",
                            "subject": "",
                        },
                        text="average_score",
                    )
                    fig.update_traces(
                        marker_color="#60a5fa",
                        marker_line_width=0,
                        texttemplate="%{x:.1f}%",
                        textposition="outside",
                        cliponaxis=False,
                        textfont=dict(size=11, color="#e2e8f0"),
                        hovertemplate=(
                            "<b>%{y}</b><br>"
                            "Average score: %{x:.1f}%<extra></extra>"
                        ),
                    )
                    max_score = float(chart["average_score"].max())
                    # Add enough space for score labels without squeezing the bars.
                    fig.update_xaxes(
                        range=[0, max(110, min(125, max_score + 15))],
                        title_text="Average score (%)",
                        automargin=True,
                        showgrid=True,
                        gridcolor="rgba(148,163,184,.10)",
                    )
                    fig.update_yaxes(
                        title_text="",
                        automargin=True,
                        tickfont=dict(size=10),
                    )
                    fig.update_layout(
                        height=max(280, min(360, 70 * len(chart) + 90)),
                        margin=dict(l=12, r=52, t=16, b=48),
                        bargap=0.32,
                    )
                    st.plotly_chart(
                        apply_premium_chart_style(fig, max(280, min(360, 70 * len(chart) + 90))),
                        width="stretch",
                        config={"displayModeBar": False, "responsive": True},
                    )
                else:
                    st.info("No valid subject scores available.")
            else:
                st.info("No subject data.")

        left, right = st.columns(2, gap="large")

        with left:
            st.markdown("**🧠 Study Methods**")
            st.caption("Average score by study method")
            if not methods.empty:
                chart = methods.sort_values("average_score", ascending=True).copy()
                fig = px.bar(
                    chart,
                    x="average_score",
                    y="study_method",
                    orientation="h",
                    labels={"study_method": "", "average_score": "Average score (%)"},
                    text="average_score",
                )
                fig.update_traces(
                    marker_color="#8b5cf6",
                    marker_line_width=0,
                    texttemplate="%{x:.1f}%",
                    textposition="outside",
                    cliponaxis=False,
                    textfont=dict(size=10, color="#e2e8f0"),
                    hovertemplate="<b>%{y}</b><br>Average score: %{x:.1f}%<extra></extra>",
                )
                max_score = float(chart["average_score"].max())
                fig.update_xaxes(
                    range=[0, max(110, min(125, max_score + 15))],
                    title_text="Average score (%)",
                    automargin=True,
                )
                fig.update_yaxes(title_text="", automargin=True, tickfont=dict(size=10))
                chart_height = max(240, min(340, 45 * len(chart) + 90))
                fig.update_layout(
                    height=chart_height,
                    margin=dict(l=8, r=45, t=12, b=45),
                    bargap=0.3,
                )
                st.plotly_chart(
                    apply_premium_chart_style(fig, chart_height),
                    width="stretch",
                    config={"displayModeBar": False, "responsive": True},
                )

        with right:
            st.markdown("**🕐 Best Study Time**")
            st.caption("Average score by time of day")
            if not times.empty:
                chart = times.copy()
                fig = px.bar(
                    chart, x="time_period", y="average_score",
                    labels={"time_period": "Study period", "average_score": "Average score (%)"},
                )
                fig.update_traces(
                    marker_color="#34d399", marker_line_width=0,
                    hovertemplate="<b>%{x}</b><br>Average score: %{y:.1f}%<extra></extra>",
                )
                fig.update_yaxes(rangemode="tozero", range=[0, min(110, max(100, float(chart["average_score"].max()) * 1.12))])
                st.plotly_chart(apply_premium_chart_style(fig, 230), width="stretch", config={"displayModeBar": False, "responsive": True})

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
            "Explore your study patterns with flexible filters and period comparisons.",
            "📊",
        )

        # ----------------------------------------------------
        # STAGE 3: ANALYTICS FILTERS
        # ----------------------------------------------------
        analytics_df = df.copy()
        parsed_dates = pd.to_datetime(analytics_df["date"], errors="coerce")
        valid_date_values = parsed_dates.dropna()

        if valid_date_values.empty:
            st.warning("Your study records do not contain valid dates, so date filtering is unavailable.")
            st.stop()

        min_date = valid_date_values.min().date()
        max_date = valid_date_values.max().date()

        st.markdown("### 🔎 Filter your analysis")
        filter_col1, filter_col2, filter_col3 = st.columns([1.35, 1, 1])
        with filter_col1:
            selected_dates = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="analytics_date_range",
                help="Choose the period included in the analytics below.",
            )
        with filter_col2:
            subject_options = sorted(
                analytics_df["subject"].dropna().astype(str).unique().tolist()
            )
            selected_subjects = st.multiselect(
                "Subjects",
                options=subject_options,
                default=subject_options,
                key="analytics_subject_filter",
                help="Select one or more subjects, or clear the selection to see none.",
            )
        with filter_col3:
            if "study_method" in analytics_df.columns:
                method_options = sorted(
                    analytics_df["study_method"].dropna().astype(str).unique().tolist()
                )
            else:
                method_options = []
            selected_methods = st.multiselect(
                "Study methods",
                options=method_options,
                default=method_options,
                key="analytics_method_filter",
                help="Filter analytics by the study methods you used.",
            )

        if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
            range_start, range_end = selected_dates
        elif isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 1:
            range_start = range_end = selected_dates[0]
        else:
            range_start = range_end = selected_dates

        analytics_df["_analytics_date"] = parsed_dates
        filtered_mask = (
            analytics_df["_analytics_date"].dt.date.ge(range_start)
            & analytics_df["_analytics_date"].dt.date.le(range_end)
            & analytics_df["subject"].astype(str).isin(selected_subjects)
        )
        if "study_method" in analytics_df.columns:
            # Treat missing methods as a distinct value only when selected options include it;
            # ordinary missing values are excluded by the method filter.
            filtered_mask &= analytics_df["study_method"].astype(str).isin(selected_methods)

        df = analytics_df.loc[filtered_mask].drop(columns=["_analytics_date"]).copy()

        st.caption(
            f"Showing {len(df)} of {len(analytics_df)} sessions · "
            f"{range_start.strftime('%d %b %Y')} – {range_end.strftime('%d %b %Y')}"
        )

        if df.empty:
            st.warning("No sessions match these filters. Expand the date range or select more subjects/methods.")
            st.stop()

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

        # Compare the selected period with the immediately preceding period of equal length.
        with st.expander("📊 Compare with the previous period", expanded=False):
            period_days = max(1, (range_end - range_start).days + 1)
            previous_start = range_start - pd.Timedelta(days=period_days)
            previous_end = range_start - pd.Timedelta(days=1)
            all_dates = pd.to_datetime(analytics_df["date"], errors="coerce").dt.date
            previous_mask = (
                all_dates.ge(previous_start)
                & all_dates.le(previous_end)
                & analytics_df["subject"].astype(str).isin(selected_subjects)
            )
            if "study_method" in analytics_df.columns:
                previous_mask &= analytics_df["study_method"].astype(str).isin(selected_methods)
            previous_df = analytics_df.loc[previous_mask].drop(columns=["_analytics_date"], errors="ignore").copy()

            if previous_df.empty:
                st.info(
                    f"No matching sessions were recorded in the previous period "
                    f"({previous_start.strftime('%d %b')} – {previous_end.strftime('%d %b %Y')})."
                )
            else:
                previous_metrics = calculate_metrics(previous_df)
                compare_cols = st.columns(4)
                comparisons = [
                    ("Study hours", "total_study_hours", "h"),
                    ("Sessions", "total_sessions", ""),
                    ("Average score", "average_score", "%"),
                    ("Average focus", "average_focus", "/5"),
                ]
                for col, (label, key, suffix) in zip(compare_cols, comparisons):
                    current_value = float(metrics[key])
                    previous_value = float(previous_metrics[key])
                    delta = current_value - previous_value
                    with col:
                        st.metric(
                            label,
                            f"{current_value:.1f}{suffix}" if key != "total_sessions" else str(int(current_value)),
                            delta=f"{delta:+.1f}{suffix}" if key != "total_sessions" else f"{int(delta):+d}",
                        )
                st.caption(
                    f"Current: {range_start.strftime('%d %b')} – {range_end.strftime('%d %b %Y')} · "
                    f"Previous: {previous_start.strftime('%d %b')} – {previous_end.strftime('%d %b %Y')}. "
                    "Differences describe the recorded data; they do not establish cause and effect."
                )

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
            else:
                st.info("Not enough score data for subject analysis in this filtered period.")

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
            else:
                st.info("No study-method data is available for these filters.")

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
            else:
                st.info("Not enough data for time-of-day analysis in this filtered period.")

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
            else:
                st.info("Not enough duration and score data for this period.")

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
            else:
                st.info("Not enough focus and score data for this period.")

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
            else:
                st.info("Not enough distraction and score data for this period.")

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
            else:
                st.info("Not enough daily data for a progress chart.")

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
            st.markdown("**🎯 Focus vs Test Score**")
            st.caption("Higher focus should ideally correspond to stronger results.")
            data = focus_score_analysis(df)
            if not data.empty:
                st.line_chart(
                    data.set_index("focus_rating")[["average_score"]],
                    height=300,
                )
                st.caption(f"Correlation: {focus_corr:.3f}")

        with right:
            st.markdown("**📱 Distraction vs Test Score**")
            st.caption("See how interruptions relate to performance.")
            data = distraction_score_analysis(df)
            if not data.empty:
                st.bar_chart(
                    data.set_index("distraction_group")[["average_score"]],
                    height=300,
                )
                st.caption(f"Correlation: {distraction_corr:.3f}")

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
# STUDY CONSISTENCY TRACKER
# ============================================================

elif page == "🔥 Study Consistency":
    df = clean_data(load_data())
    header(
        "Study Consistency",
        "Build a sustainable routine by tracking the days you study, not just the hours.",
        "🔥",
    )

    if df.empty:
        st.info("Add study sessions to start building your consistency calendar.")
    else:
        tracker = df.copy()
        tracker["study_day"] = pd.to_datetime(tracker["date"], errors="coerce").dt.normalize()
        tracker["study_duration"] = pd.to_numeric(tracker["study_duration"], errors="coerce").fillna(0)
        tracker = tracker.dropna(subset=["study_day"])
        tracker = tracker[tracker["study_duration"] > 0]

        if tracker.empty:
            st.info("No valid study days were found yet. Add a session with a duration greater than zero.")
        else:
            daily = tracker.groupby("study_day", as_index=False).agg(
                study_hours=("study_duration", "sum"),
                sessions=("study_duration", "size"),
            )
            active_dates = set(daily["study_day"].dt.date.tolist())
            today = pd.Timestamp(date.today()).normalize()
            today_date = today.date()
            week_start = today - pd.Timedelta(days=today.weekday())
            week_dates = [week_start + pd.Timedelta(days=i) for i in range(7)]
            this_week = daily[(daily["study_day"] >= week_start) & (daily["study_day"] <= today)]
            active_days_this_week = int(this_week["study_day"].dt.date.nunique())
            hours_this_week = float(this_week["study_hours"].sum())

            sorted_dates = sorted(active_dates)
            longest_streak = 0
            running_streak = 0
            previous = None
            for day in sorted_dates:
                if previous is not None and (day - previous).days == 1:
                    running_streak += 1
                else:
                    running_streak = 1
                longest_streak = max(longest_streak, running_streak)
                previous = day

            if today_date in active_dates:
                streak_anchor = today_date
            elif (today - pd.Timedelta(days=1)).date() in active_dates:
                streak_anchor = (today - pd.Timedelta(days=1)).date()
            else:
                streak_anchor = None

            current_streak = 0
            if streak_anchor is not None:
                cursor = streak_anchor
                while cursor in active_dates:
                    current_streak += 1
                    cursor = cursor - pd.Timedelta(days=1)
                    cursor = cursor.date() if isinstance(cursor, pd.Timestamp) else cursor

            best_day = daily.loc[daily["study_hours"].idxmax()]
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                kpi_card("🔥", f"{current_streak} day{'s' if current_streak != 1 else ''}", "Current streak")
            with m2:
                kpi_card("🏆", f"{longest_streak} day{'s' if longest_streak != 1 else ''}", "Longest streak")
            with m3:
                kpi_card("📅", f"{active_days_this_week}/7", "Active days this week")
            with m4:
                kpi_card("⏱️", f"{hours_this_week:.1f} h", "Study hours this week")

            section("This Week")
            week_labels = [d.strftime("%a") for d in week_dates]
            week_status = ["Studied" if d.date() in active_dates else "No session" for d in week_dates]
            week_frame = pd.DataFrame({
                "Day": week_labels,
                "Date": [d.strftime("%d %b") for d in week_dates],
                "Status": week_status,
            })
            cols = st.columns(7)
            for i, col in enumerate(cols):
                studied = week_status[i] == "Studied"
                with col:
                    st.markdown(f"""
                    <div class="card" style="padding:12px 6px;text-align:center;min-height:92px;">
                        <div style="color:#8996aa;font-size:11px;">{week_labels[i]}</div>
                        <div style="font-size:20px;margin:7px 0;">{'✅' if studied else '○'}</div>
                        <div style="color:{'#a78bfa' if studied else '#64748b'};font-size:10px;">{week_dates[i].strftime('%d %b')}</div>
                    </div>
                    """, unsafe_allow_html=True)

            section("Your Last 12 Weeks")
            calendar_end = today
            calendar_start = today - pd.Timedelta(days=83)
            calendar_days = pd.DataFrame({"study_day": pd.date_range(calendar_start, calendar_end, freq="D")})
            calendar_daily = calendar_days.merge(daily, on="study_day", how="left")
            calendar_daily["study_hours"] = calendar_daily["study_hours"].fillna(0)
            calendar_daily["sessions"] = calendar_daily["sessions"].fillna(0).astype(int)
            calendar_daily["week_start"] = calendar_daily["study_day"] - pd.to_timedelta(calendar_daily["study_day"].dt.weekday, unit="D")
            calendar_daily["week_label"] = calendar_daily["week_start"].dt.strftime("%d %b")
            calendar_daily["weekday"] = calendar_daily["study_day"].dt.day_name().str[:3]
            fig = px.scatter(
                calendar_daily,
                x="week_start",
                y="weekday",
                color="study_hours",
                size=calendar_daily["study_hours"].clip(lower=0.25),
                hover_name=calendar_daily["study_day"].dt.strftime("%A, %d %B %Y"),
                hover_data={"study_hours": ":.2f", "sessions": True, "week_start": False, "weekday": False},
                color_continuous_scale=["#202938", "#5b46a8", "#a78bfa"],
                labels={"week_start": "Week starting", "weekday": "Day", "study_hours": "Study hours"},
            )
            fig.update_traces(marker=dict(line=dict(width=0)))
            fig.update_layout(
                height=300,
                margin=dict(l=12, r=12, t=12, b=42),
                coloraxis_colorbar=dict(title="Hours", thickness=10, len=0.7),
            )
            fig.update_yaxes(categoryorder="array", categoryarray=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], title_text="")
            fig.update_xaxes(title_text="Week", tickformat="%d %b", dtick="M1")
            st.plotly_chart(apply_premium_chart_style(fig, 300), width="stretch", config={"displayModeBar": False, "responsive": True})

            section("Consistency Highlights")
            h1, h2 = st.columns(2, gap="large")
            with h1:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">🌟 Strongest study day</div>
                    <div style="font-size:24px;font-weight:800;color:#f8fafc;margin-top:10px;">{pd.Timestamp(best_day['study_day']).strftime('%d %b %Y')}</div>
                    <div class="card-muted">{float(best_day['study_hours']):.1f} study hours across {int(best_day['sessions'])} session(s).</div>
                </div>
                """, unsafe_allow_html=True)
            with h2:
                consistency_rate = (len(active_dates) / max(1, (today_date - min(active_dates)).days + 1)) * 100
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">📈 Study-day consistency</div>
                    <div style="font-size:24px;font-weight:800;color:#f8fafc;margin-top:10px;">{consistency_rate:.1f}%</div>
                    <div class="card-muted">Percentage of days with a recorded study session since your first recorded study day.</div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================
# WEEKLY STUDY GOALS
# ============================================================

elif page == "🎯 Weekly Goals":
    header(
        "Weekly Study Goals",
        "Set realistic targets, track your progress, and build a consistent study routine.",
        "🎯",
    )

    today = pd.Timestamp(date.today()).normalize()
    week_start = today - pd.Timedelta(days=today.weekday())
    week_end = week_start + pd.Timedelta(days=6)
    week_start_text = week_start.strftime("%Y-%m-%d")

    st.markdown(
        f"**Current week:** {week_start.strftime('%d %b %Y')} – {week_end.strftime('%d %b %Y')}"
    )
    st.caption("Goals are saved in your local SQLite database and are kept separately from study-session records.")

    goals = get_weekly_goals(week_start_text)
    overall_goal = next((g["goal_hours"] for g in goals if g["subject"] == "__OVERALL__"), 10.0)
    subject_goals = {g["subject"]: g["goal_hours"] for g in goals if g["subject"] != "__OVERALL__"}

    st.markdown("### ⚙️ Set your weekly targets")
    with st.form("weekly_goal_form"):
        overall_target = st.number_input(
            "Overall weekly study goal (hours)",
            min_value=0.5,
            max_value=168.0,
            value=float(overall_goal),
            step=0.5,
            help="Total study hours you want to complete from Monday through Sunday.",
        )

        source_df = clean_data(load_data())
        available_subjects = []
        if not source_df.empty and "subject" in source_df.columns:
            available_subjects = sorted(
                str(s).strip() for s in source_df["subject"].dropna().unique() if str(s).strip()
            )
        goal_subject_options = sorted(set(available_subjects) | set(subject_goals.keys()))
        goal_subject_options = [s for s in goal_subject_options if s != "__OVERALL__"]

        if goal_subject_options:
            goal_subject = st.selectbox("Subject for an optional subject-specific goal", goal_subject_options)
            current_subject_target = float(subject_goals.get(goal_subject, 2.0))
            subject_target = st.number_input(
                f"Weekly goal for {goal_subject} (hours)",
                min_value=0.0,
                max_value=168.0,
                value=min(current_subject_target, 168.0),
                step=0.5,
                help="Set to 0 if you do not want a target for this subject.",
            )
        else:
            goal_subject = None
            subject_target = 0.0
            st.info("Add a study session first to create subject-specific goals. You can still set your overall weekly goal.")

        save_goals = st.form_submit_button("💾 Save weekly goals", type="primary", width="stretch")

    if save_goals:
        save_weekly_goal(week_start_text, "__OVERALL__", float(overall_target))
        if goal_subject:
            if subject_target > 0:
                save_weekly_goal(week_start_text, goal_subject, float(subject_target))
            else:
                delete_weekly_goal(week_start_text, goal_subject)
        st.success("Your weekly goals have been saved.")
        st.rerun()

    df = clean_data(load_data())
    if df.empty:
        st.info("Your goals are ready. Add study sessions during this week to see your progress here.")
    else:
        goal_df = df.copy()
        goal_df["date"] = pd.to_datetime(goal_df["date"], errors="coerce")
        goal_df["study_duration"] = pd.to_numeric(goal_df["study_duration"], errors="coerce").fillna(0)
        goal_df = goal_df.dropna(subset=["date"])
        goal_df = goal_df[
            (goal_df["date"].dt.date >= week_start.date()) &
            (goal_df["date"].dt.date <= today.date())
        ]

        hours_done = float(goal_df["study_duration"].sum()) if not goal_df.empty else 0.0
        overall_goal = float(overall_goal)
        overall_progress = min(hours_done / overall_goal, 1.0) if overall_goal > 0 else 0.0
        remaining = max(overall_goal - hours_done, 0.0)

        st.markdown("### 📊 Your progress this week")
        m1, m2, m3 = st.columns(3)
        m1.metric("Hours studied", f"{hours_done:.1f} h")
        m2.metric("Weekly target", f"{overall_goal:.1f} h")
        m3.metric("Hours remaining", f"{remaining:.1f} h", delta=f"{overall_progress * 100:.0f}% complete")
        st.progress(overall_progress, text=f"Overall goal: {overall_progress * 100:.0f}% completed")

        if overall_goal > 0 and hours_done >= overall_goal:
            st.success("🎉 Weekly study goal completed! Great work — keep the routine sustainable.")
        elif remaining > 0:
            days_left_including_today = max((week_end.date() - today.date()).days + 1, 1)
            daily_needed = remaining / days_left_including_today
            st.info(f"You need about **{daily_needed:.1f} study hours per day** for the rest of this week to reach your target.")

        if subject_goals:
            st.markdown("### 📚 Subject goal progress")
            subject_rows = []
            for subject_name, target_hours in sorted(subject_goals.items()):
                subject_sessions = goal_df[goal_df["subject"].astype(str).str.strip() == subject_name]
                studied = float(subject_sessions["study_duration"].sum()) if not subject_sessions.empty else 0.0
                percent = min(studied / target_hours, 1.0) * 100 if target_hours > 0 else 0.0
                subject_rows.append({
                    "Subject": subject_name,
                    "Hours studied": round(studied, 2),
                    "Weekly target (hours)": round(float(target_hours), 2),
                    "Progress (%)": round(percent, 1),
                    "Status": "Completed 🎉" if target_hours > 0 and studied >= target_hours else "In progress",
                })
                st.markdown(f"**{subject_name}** — {studied:.1f} / {float(target_hours):.1f} hours")
                st.progress(percent / 100, text=f"{percent:.0f}% completed")
            if subject_rows:
                st.dataframe(pd.DataFrame(subject_rows), width="stretch", hide_index=True)

        st.markdown("### 🗓️ Daily study hours")
        week_days = pd.DataFrame({"date": pd.date_range(week_start, today, freq="D")})
        if not goal_df.empty:
            daily_hours = goal_df.groupby(goal_df["date"].dt.normalize())["study_duration"].sum().reset_index()
            daily_hours.columns = ["date", "study_duration"]
            week_days = week_days.merge(daily_hours, on="date", how="left")
        else:
            week_days["study_duration"] = 0.0
        week_days["study_duration"] = week_days["study_duration"].fillna(0.0)
        week_days["day"] = week_days["date"].dt.strftime("%a, %d %b")
        fig = px.bar(
            week_days,
            x="day",
            y="study_duration",
            labels={"day": "Day", "study_duration": "Study hours"},
            text="study_duration",
        )
        fig.update_traces(marker_color="#8b5cf6", texttemplate="%{text:.1f}h", textposition="outside")
        fig.update_yaxes(rangemode="tozero", title_text="Study hours")
        st.plotly_chart(apply_premium_chart_style(fig, 280), width="stretch", config={"displayModeBar": False, "responsive": True})

        st.caption("Progress is calculated from sessions dated Monday through today. Future days in the week are not counted yet.")


# ============================================================
# STUDY REPORTS
# ============================================================

elif page == "📄 Study Reports":
    header(
        "Exportable Study Reports",
        "Filter your study history and download a CSV or a printable PDF report.",
        "📄",
    )

    raw_sessions = get_all_sessions()
    report_columns = [
        "ID", "Date", "Subject", "Start Time", "End Time",
        "Study Hours", "Break Minutes", "Distraction Minutes",
        "Study Method", "Focus Rating", "Test Score (%)",
    ]

    if not raw_sessions:
        st.info("There are no study sessions to export yet. Add a study session first.")
    else:
        all_sessions_df = pd.DataFrame(raw_sessions, columns=report_columns)
        all_sessions_df["Date"] = pd.to_datetime(
            all_sessions_df["Date"], errors="coerce"
        ).dt.date
        for numeric_col in [
            "Study Hours", "Break Minutes", "Distraction Minutes",
            "Focus Rating", "Test Score (%)",
        ]:
            all_sessions_df[numeric_col] = pd.to_numeric(
                all_sessions_df[numeric_col], errors="coerce"
            )

        valid_dates = all_sessions_df["Date"].dropna()
        if valid_dates.empty:
            st.warning("The saved session dates could not be read. Check the date format in your database.")
        else:
            min_date = min(valid_dates)
            max_date = max(valid_dates)
            st.markdown("### Choose report filters")
            date_col, subject_col = st.columns([1.2, 1], gap="large")
            with date_col:
                selected_dates = st.date_input(
                    "Report date range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    help="Choose the first and last date to include in the report.",
                )
            with subject_col:
                subject_options = sorted(
                    all_sessions_df["Subject"].dropna().astype(str).unique().tolist()
                )
                selected_subjects = st.multiselect(
                    "Subjects",
                    options=subject_options,
                    default=subject_options,
                    help="Leave all subjects selected to export your full study history.",
                )

            if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
                start_date, end_date = selected_dates
            elif isinstance(selected_dates, date):
                start_date = end_date = selected_dates
            else:
                start_date, end_date = min_date, max_date

            if start_date > end_date:
                st.error("The start date must be on or before the end date.")
                report_df = all_sessions_df.iloc[0:0].copy()
            else:
                report_df = all_sessions_df[
                    all_sessions_df["Date"].between(start_date, end_date, inclusive="both")
                ].copy()
                if selected_subjects:
                    report_df = report_df[report_df["Subject"].astype(str).isin(selected_subjects)]
                else:
                    report_df = report_df.iloc[0:0]

            total_hours = float(report_df["Study Hours"].fillna(0).sum()) if not report_df.empty else 0.0
            session_count = int(len(report_df))
            average_score = report_df["Test Score (%)"].dropna().mean() if not report_df.empty else float("nan")
            average_focus = report_df["Focus Rating"].dropna().mean() if not report_df.empty else float("nan")

            metric_cols = st.columns(4)
            metric_values = [
                ("Sessions", f"{session_count}"),
                ("Study hours", f"{total_hours:.1f} h"),
                ("Average score", f"{average_score:.1f}%" if pd.notna(average_score) else "—"),
                ("Average focus", f"{average_focus:.1f}/5" if pd.notna(average_focus) else "—"),
            ]
            for metric_col, (label, value) in zip(metric_cols, metric_values):
                with metric_col:
                    st.metric(label, value)

            st.markdown("### Report preview")
            if report_df.empty:
                st.info("No sessions match these filters. Change the date range or select one or more subjects.")
            else:
                subject_summary = (
                    report_df.groupby("Subject", dropna=False)
                    .agg(
                        Sessions=("ID", "count"),
                        Study_Hours=("Study Hours", "sum"),
                        Average_Score=("Test Score (%)", "mean"),
                        Average_Focus=("Focus Rating", "mean"),
                    )
                    .reset_index()
                )
                subject_summary["Study_Hours"] = subject_summary["Study_Hours"].round(2)
                subject_summary["Average_Score"] = subject_summary["Average_Score"].round(1)
                subject_summary["Average_Focus"] = subject_summary["Average_Focus"].round(1)
                st.dataframe(
                    report_df.drop(columns=["ID"]).sort_values(["Date", "Subject"], ascending=[False, True]),
                    use_container_width=True,
                    hide_index=True,
                )
                st.markdown("#### Summary by subject")
                display_summary = subject_summary.rename(columns={
                    "Study_Hours": "Study Hours",
                    "Average_Score": "Average Score (%)",
                    "Average_Focus": "Average Focus",
                })
                st.dataframe(display_summary, use_container_width=True, hide_index=True)

                csv_buffer = io.StringIO()
                csv_export = report_df.copy()
                csv_export["Date"] = csv_export["Date"].astype(str)
                csv_export.to_csv(csv_buffer, index=False)

                export_col1, export_col2 = st.columns(2, gap="medium")
                with export_col1:
                    st.download_button(
                        "⬇️ Download CSV report",
                        data="\ufeff" + csv_buffer.getvalue(),
                        file_name=f"studyflow_report_{start_date}_{end_date}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

                with export_col2:
                    if st.button("🧾 Prepare PDF report", use_container_width=True):
                        st.session_state["studyflow_pdf_report_requested"] = True

                if st.session_state.get("studyflow_pdf_report_requested", False):
                    try:
                        from reportlab.lib import colors
                        from reportlab.lib.enums import TA_CENTER
                        from reportlab.lib.pagesizes import A4, landscape
                        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                        from reportlab.lib.units import mm
                        from reportlab.platypus import (
                            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                            PageBreak, KeepTogether,
                        )

                        pdf_buffer = io.BytesIO()
                        document = SimpleDocTemplate(
                            pdf_buffer,
                            pagesize=landscape(A4),
                            rightMargin=14 * mm,
                            leftMargin=14 * mm,
                            topMargin=13 * mm,
                            bottomMargin=13 * mm,
                            title="StudyFlow Study Report",
                            author="StudyFlow",
                        )
                        styles = getSampleStyleSheet()
                        styles.add(ParagraphStyle(
                            name="StudyFlowTitle", parent=styles["Title"],
                            alignment=TA_CENTER, textColor=colors.HexColor("#5B21B6"),
                            fontSize=20, leading=24, spaceAfter=5,
                        ))
                        styles.add(ParagraphStyle(
                            name="StudyFlowSub", parent=styles["Normal"],
                            alignment=TA_CENTER, textColor=colors.HexColor("#475569"),
                            fontSize=9, leading=12, spaceAfter=12,
                        ))
                        story = [
                            Paragraph("StudyFlow — Study Report", styles["StudyFlowTitle"]),
                            Paragraph(
                                f"Period: {start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')} | "
                                f"Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
                                styles["StudyFlowSub"],
                            ),
                        ]
                        summary_data = [
                            ["Sessions", "Total study hours", "Average score", "Average focus"],
                            [str(session_count), f"{total_hours:.1f} h",
                             f"{average_score:.1f}%" if pd.notna(average_score) else "Not recorded",
                             f"{average_focus:.1f}/5" if pd.notna(average_focus) else "Not recorded"],
                        ]
                        summary_table = Table(summary_data, colWidths=[55 * mm] * 4)
                        summary_table.setStyle(TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDE9FE")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#4C1D95")),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                            ("TOPPADDING", (0, 0), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ]))
                        story.extend([summary_table, Spacer(1, 8 * mm), Paragraph("Subject Summary", styles["Heading2"])])

                        subject_pdf_data = [["Subject", "Sessions", "Study hours", "Avg. score", "Avg. focus"]]
                        for _, row in subject_summary.iterrows():
                            subject_pdf_data.append([
                                str(row["Subject"]), str(int(row["Sessions"])),
                                f"{float(row['Study_Hours'] or 0):.2f}",
                                f"{float(row['Average_Score']):.1f}%" if pd.notna(row["Average_Score"]) else "—",
                                f"{float(row['Average_Focus']):.1f}/5" if pd.notna(row["Average_Focus"]) else "—",
                            ])
                        subject_table = Table(subject_pdf_data, repeatRows=1, colWidths=[70 * mm, 30 * mm, 35 * mm, 35 * mm, 35 * mm])
                        subject_table.setStyle(TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 8),
                            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                            ("TOPPADDING", (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ]))
                        story.extend([subject_table, Spacer(1, 8 * mm), Paragraph("Session Details", styles["Heading2"])])

                        detail_columns = ["Date", "Subject", "Start Time", "End Time", "Study Hours", "Break Minutes", "Distraction Minutes", "Study Method", "Focus Rating", "Test Score (%)"]
                        detail_data = [["Date", "Subject", "Start", "End", "Hours", "Break min", "Distr. min", "Method", "Focus", "Score %"]]
                        for _, row in report_df.sort_values(["Date", "Subject"]).iterrows():
                            detail_data.append([
                                str(row["Date"]), str(row["Subject"]), str(row["Start Time"]), str(row["End Time"]),
                                f"{float(row['Study Hours'] or 0):.2f}",
                                f"{float(row['Break Minutes'] or 0):.0f}",
                                f"{float(row['Distraction Minutes'] or 0):.0f}",
                                str(row["Study Method"] or "—"),
                                str(int(row["Focus Rating"])) if pd.notna(row["Focus Rating"]) else "—",
                                f"{float(row['Test Score (%)']):.1f}" if pd.notna(row["Test Score (%)"]) else "—",
                            ])
                        detail_table = Table(detail_data, repeatRows=1, colWidths=[24*mm, 31*mm, 18*mm, 18*mm, 18*mm, 19*mm, 20*mm, 30*mm, 15*mm, 18*mm])
                        detail_table.setStyle(TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 7),
                            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]))
                        story.append(detail_table)
                        document.build(story)
                        st.download_button(
                            "⬇️ Download PDF report",
                            data=pdf_buffer.getvalue(),
                            file_name=f"studyflow_report_{start_date}_{end_date}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="studyflow_pdf_download",
                        )
                    except ImportError:
                        st.error("PDF export needs ReportLab. Install it in your project environment with: python -m pip install reportlab")
                    except Exception as exc:
                        st.error(f"Could not create the PDF report: {exc}")


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
        daily = daily_analysis(df)

        # ── Compute streak for the recommendations engine ─────────────────
        _today = pd.Timestamp(date.today()).normalize()
        _tracker = df.copy()
        _tracker["study_day"] = pd.to_datetime(
            _tracker["date"], errors="coerce"
        ).dt.normalize()
        _tracker["study_duration"] = pd.to_numeric(
            _tracker["study_duration"], errors="coerce"
        ).fillna(0)
        _tracker = _tracker.dropna(subset=["study_day"])
        _tracker = _tracker[_tracker["study_duration"] > 0]

        _streak_days = 0
        if not _tracker.empty:
            _active_dates = set(
                _tracker.groupby("study_day").first().reset_index()["study_day"]
                .dt.date.tolist()
            )
            _anchor = (
                _today.date()
                if _today.date() in _active_dates
                else (_today - pd.Timedelta(days=1)).date()
                if (_today - pd.Timedelta(days=1)).date() in _active_dates
                else None
            )
            if _anchor is not None:
                _cursor = _anchor
                while _cursor in _active_dates:
                    _streak_days += 1
                    _cursor = (
                        pd.Timestamp(_cursor) - pd.Timedelta(days=1)
                    ).date()

        # ── Weekly goal context ───────────────────────────────────────────
        _week_start = _today - pd.Timedelta(days=_today.weekday())
        _goals = get_weekly_goals(_week_start.strftime("%Y-%m-%d"))
        _overall_goal = next(
            (g["goal_hours"] for g in _goals if g["subject"] == "__OVERALL__"),
            0.0,
        )
        _week_df = df.copy()
        _week_df["date"] = pd.to_datetime(_week_df["date"], errors="coerce")
        _week_df = _week_df[
            _week_df["date"].dt.date >= _week_start.date()
        ]
        _hours_this_week = float(
            pd.to_numeric(_week_df["study_duration"], errors="coerce")
            .fillna(0)
            .sum()
        )

        recommendations = generate_recommendations(
            df, metrics, subjects, methods, times,
            daily_data=daily,
            streak_days=_streak_days,
            weekly_goal_hours=float(_overall_goal),
            weekly_studied_hours=_hours_this_week,
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

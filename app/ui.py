import sys
import time
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from app.assets.theme import inject_css, load_css
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar
from app.database import init_db, get_history, get_user_stats

st.set_page_config(
    page_title="AI Adaptive Onboarding",
    layout="wide",
    page_icon="✨",
    initial_sidebar_state="expanded",
)

load_css()

db_init_error = None
try:
    init_db()
    st.session_state.db_available = True
except Exception as exc:
    db_init_error = exc
    st.session_state.db_available = False

inject_css()
render_sidebar()
if db_init_error:
    st.warning("Database is unavailable. You can still explore demo mode.")


def _render_logged_out() -> None:
    render_page_header(
        "Build Job-Ready Roadmaps",
        "Upload resume + JD, detect skill gaps, and generate a structured learning plan.",
        eyebrow="Welcome",
    )

    render_section_intro(
        "What You Get",
        "The platform combines skill extraction, matching, and guided upskilling in one place.",
        pills=["Resume + JD Parsing", "Gap Analysis", "Roadmap + Charts", "Reasoning Trace"],
    )
    st.write("")

    render_section_intro(
        "Account Access",
        "Use dedicated pages for login and registration from the sidebar or quick actions below.",
        pills=["Secure Login", "Create Account", "Demo Mode"],
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("Go To Login Page", use_container_width=True):
            st.switch_page("pages/login.py")
    with col2:
        if st.button("Go To Register Page", use_container_width=True):
            st.switch_page("pages/register.py")

    st.write("")
    if st.button("Try Demo Account", type="primary", use_container_width=True):
        st.session_state.logged_in = True
        st.session_state.user_id = "demo_user"
        st.session_state.username = "demo"
        st.session_state.user_email = "demo@example.com"
        st.success("Demo mode activated.")
        time.sleep(0.4)
        st.rerun()

    render_footer()


def _render_logged_in() -> None:
    username = st.session_state.get("username", "there")
    render_page_header(
        f"Welcome, {username}",
        "Start a new analysis or review your progress from recent runs.",
        eyebrow="Dashboard",
    )

    if st.session_state.get("user_id") != "demo_user" and st.session_state.get("db_available"):
        with st.spinner("Loading stats..."):
            stats = get_user_stats(st.session_state["user_id"])

        render_section_intro(
            "Performance Snapshot",
            "Live metrics based on your recent analyses.",
            pills=["Progress Tracking", "Best Score", "Recent Activity"],
        )
        col1, col2, col3, col4 = st.columns(4, gap="large")
        col1.metric("Analyses", stats.get("total_analyses", 0))
        col2.metric("Average Score", f"{stats.get('avg_score', 0):.1f}%")
        col3.metric("Best Score", f"{stats.get('best_score', 0):.1f}%")
        last = stats.get("last_analysis")
        col4.metric("Last Analysis", last.strftime("%b %d") if last else "Never")

    elif not st.session_state.get("db_available"):
        st.info("Database-backed performance snapshots are unavailable right now, but you can still explore the app safely.")

    st.write("")
    render_section_intro(
        "Quick Actions",
        "Jump directly to the core workflows.",
        pills=["Upload", "Analyze", "Roadmap", "History"],
    )
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        if st.button("New Analysis", use_container_width=True, type="primary"):
            st.switch_page("pages/upload.py")
    with col2:
        if st.button("Roadmaps", use_container_width=True):
            st.switch_page("pages/roadmap.py")
    with col3:
        if st.button("History", use_container_width=True):
            st.switch_page("pages/history.py")

    if st.session_state.get("user_id") != "demo_user" and st.session_state.get("db_available"):
        st.write("")
        st.subheader("Recent Activity")
        history = get_history(st.session_state["user_id"], days=7)

        if history:
            for item in history[:5]:
                created = item.get("created_at")
                created_label = created.strftime("%b %d, %H:%M") if created else "n/a"
                with st.expander(f"Analysis • {item.get('score', 0)}% • {created_label}"):
                    gap = item.get("gap_summary", {})
                    a, b, c = st.columns(3, gap="medium")
                    a.write(f"Matched: {gap.get('matched', 0)}")
                    b.write(f"Missing: {gap.get('missing', 0)}")
                    c.write(f"Score: {item.get('score', 0)}%")
        else:
            st.info("No recent analyses found. Start with a new upload.")
    elif st.session_state.get("user_id") != "demo_user":
        st.warning("History is temporarily unavailable because the database connection could not be established.")

    render_footer()


if not st.session_state.get("logged_in"):
    _render_logged_out()
else:
    _render_logged_in()

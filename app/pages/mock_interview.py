import sys
from pathlib import Path
from typing import Dict, List

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar
from backend.mock_interview import mock_interview_service

def init_session_state():
    """Initialize interview session state."""
    defaults = {
        "analysis_result": None,
        "interview_messages": [],
        "interview_started": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def _ask_interviewer(user_prompt: str = "") -> str:
    """Get the next response from the mock interview service."""
    history = st.session_state.interview_messages
    analysis = st.session_state.analysis_result
    
    with st.spinner("Interviewer is thinking..."):
        response = mock_interview_service.generate_response(history, analysis)
    return response

init_session_state()
inject_css()
render_sidebar()

render_page_header(
    "Mock Interview",
    "Prepare for the real thing with an adaptive, in-depth technical interview based on your profile.",
    eyebrow="Interview Prep",
)

if not st.session_state.analysis_result:
    st.warning("⚠️ No analysis data found. Please run an analysis on the Upload page first to ground your interview.")
    if st.button("Go to Upload"):
        st.switch_page("pages/upload.py")
    render_footer()
    st.stop()

render_section_intro(
    "Technical Assessment",
    "Qwen will evaluate your depth of expertise by asking probing questions based on your resume and matched skills.",
    pills=["Adaptive Questioning", "Depth Probing", "Real-World Scenarios"],
)

# Interview Flow
if not st.session_state.interview_started:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("The interviewer will focus on 'sorting out' your actual knowledge from buzzwords. Be prepared for follow-up questions if your answers are shallow.")
    with col2:
        if st.button("Start Interview", use_container_width=True, type="primary"):
            st.session_state.interview_started = True
            initial_question = _ask_interviewer()
            st.session_state.interview_messages.append({"role": "assistant", "content": initial_question})
            st.rerun()

if st.session_state.interview_started:
    # Display Chat
    for message in st.session_state.interview_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    user_input = st.chat_input("Provide your answer or ask for a follow-up...")
    if user_input:
        st.session_state.interview_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        response = _ask_interviewer(user_input)
        st.session_state.interview_messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Reset Option
    if st.sidebar.button("Restart Interview", use_container_width=True):
        st.session_state.interview_messages = []
        st.session_state.interview_started = False
        st.rerun()

st.markdown("---")
nav1, nav2 = st.columns(2, gap="large")
with nav1:
    if st.button("Back To Training Roadmap", use_container_width=True):
        st.switch_page("pages/roadmap.py")
with nav2:
    if st.button("View Skill Gap Analysis", use_container_width=True):
        st.switch_page("pages/analysis.py")

render_footer()

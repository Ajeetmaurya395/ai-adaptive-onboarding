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
        "prepared_questions": [],
        "current_question_index": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def _ask_interviewer(user_input: str = "") -> str:
    """Get the next response from the mock interview service."""
    history = st.session_state.interview_messages
    analysis = st.session_state.analysis_result
    
    questions = st.session_state.prepared_questions
    idx = st.session_state.current_question_index
    
    current_q = questions[idx] if idx < len(questions) else None
    next_q = questions[idx + 1] if idx + 1 < len(questions) else None
    
    with st.spinner("Interviewer is thinking..."):
        response = mock_interview_service.generate_response(
            history, 
            analysis, 
            current_question=current_q, 
            next_question=next_q
        )
    
    # Check if the response contains the next question to update the index
    if next_q and next_q.strip() in response:
        st.session_state.current_question_index += 1
        
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
    f"Qwen will evaluate your depth of expertise by asking 10 probing questions based on your resume and matched skills.",
    pills=["Adaptive Questioning", "Depth Probing", "Real-World Scenarios"],
)

# Interview Flow
if not st.session_state.interview_started:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("The interviewer will ask 10 distinct questions to sort out your actual knowledge. Be prepared for follow-up questions if your answers are shallow.")
    with col2:
        if st.button("Start Interview", use_container_width=True, type="primary"):
            with st.spinner("Generating interview plan..."):
                questions = mock_interview_service.generate_interview_plan(st.session_state.analysis_result)
                st.session_state.prepared_questions = questions
                st.session_state.current_question_index = 0
            
            st.session_state.interview_started = True
            initial_question = _ask_interviewer()
            st.session_state.interview_messages.append({"role": "assistant", "content": initial_question})
            st.rerun()

if st.session_state.interview_started:
    # Progress Bar and Skip Button
    col_prog, col_skip = st.columns([4, 1])
    with col_prog:
        progress = (st.session_state.current_question_index + 1) / 10
        st.progress(min(progress, 1.0), text=f"Question {st.session_state.current_question_index + 1} of 10")
    with col_skip:
        if st.button("Skip Question ⏭️", use_container_width=True, help="Force move to the next planned question."):
            if st.session_state.current_question_index < 9:
                st.session_state.current_question_index += 1
                new_q = st.session_state.prepared_questions[st.session_state.current_question_index]
                st.session_state.interview_messages.append({"role": "assistant", "content": f"Got it, let's move on. {new_q}"})
                st.rerun()
            else:
                st.info("This is the last question!")

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
        
        # Additional check to see if the AI transitioned but we missed it in _ask_interviewer
        questions = st.session_state.prepared_questions
        idx = st.session_state.current_question_index
        if idx + 1 < len(questions):
            next_q = questions[idx + 1]
            if next_q.strip() in response or response.strip().endswith(next_q.strip()):
                # This is a bit redundant with _ask_interviewer but helps robustness
                pass 

        st.rerun()

    # Reset Option
    if st.sidebar.button("Restart Interview", use_container_width=True):
        st.session_state.interview_messages = []
        st.session_state.interview_started = False
        st.session_state.prepared_questions = []
        st.session_state.current_question_index = 0
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

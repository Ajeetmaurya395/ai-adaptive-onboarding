import json
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
from services.llm_service import MODEL_NAME, llm


def init_session_state():
    defaults = {
        "analysis_result": None,
        "assistant_messages": [
            {
                "role": "assistant",
                "content": "Ask me anything about your analysis, roadmap, missing skills, interview preparation, or how to improve your fit for the target role.",
            }
        ],
        "assistant_use_analysis": True,
        "assistant_use_resume_jd": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _context_block() -> str:
    analysis = st.session_state.get("analysis_result") or {}
    if not analysis or not st.session_state.get("assistant_use_analysis", True):
        return "No structured analysis context attached."

    summary = analysis.get("summary", {})
    skills = analysis.get("skills", {})
    gap = analysis.get("gap", {})
    roadmap = analysis.get("roadmap", [])

    payload = {
        "role_detected": summary.get("role_detected"),
        "match_score": summary.get("match_score"),
        "matched_skills": gap.get("matched_skills", skills.get("matched", [])),
        "missing_skills": gap.get("missing_skills", skills.get("missing", [])),
        "roadmap": [
            {
                "skill": item.get("skill"),
                "priority": item.get("priority"),
                "duration": item.get("duration"),
                "resource": item.get("resource") or item.get("course_name"),
            }
            for item in roadmap[:6]
        ],
    }

    if st.session_state.get("assistant_use_resume_jd"):
        payload["resume_summary"] = analysis.get("resume", {}).get("summary", "")
        payload["job_role"] = analysis.get("jd", {}).get("role", "")

    return json.dumps(payload, indent=2)


def _build_messages(user_prompt: str) -> List[Dict[str, str]]:
    history = st.session_state.get("assistant_messages", [])
    context = _context_block()
    messages: List[Dict[str, str]] = []
    for item in history[-8:]:
        if item.get("role") in {"user", "assistant"}:
            messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{user_prompt}"})
    return messages


def _ask_assistant(user_prompt: str) -> str:
    system_prompt = (
        "You are Adaptive Onboarding Assistant powered by Qwen. "
        "Answer clearly and directly. Focus on career guidance, skill gaps, resumes, job descriptions, roadmaps, "
        "learning strategy, and interview preparation. When analysis context is provided, ground your answer in it. "
        "If data is missing, say so instead of inventing details. Keep answers structured, practical, and easy to follow."
    )
    return llm.chat(_build_messages(user_prompt), system_prompt=system_prompt, temperature=0.35, max_tokens=900)


init_session_state()

inject_css()
render_sidebar()

render_page_header(
    "Qwen Assistant",
    "Ask questions about your analysis, roadmap, role fit, learning plan, or anything related to the onboarding workflow.",
    eyebrow="Assistant",
)

render_section_intro(
    "Direct Qwen Workspace",
    f"Chat with `{MODEL_NAME}` using optional grounding from your latest analysis and roadmap.",
    pills=["Live Qwen Chat", "Roadmap Questions", "Resume Guidance", "Role-Fit Coaching"],
)

left, right = st.columns([1.15, 2.1], gap="large")
with left:
    st.markdown("### Context controls")
    st.checkbox("Use latest analysis context", key="assistant_use_analysis")
    st.checkbox("Include resume and role summary", key="assistant_use_resume_jd")

    st.markdown("### Suggested questions")
    quick_prompts = [
        "What are the top 3 things I should do to improve my match score fastest?",
        "Explain my missing skills in simple terms.",
        "Which roadmap step should I start with and why?",
        "Turn my current roadmap into a 30-day study plan.",
        "How should I rewrite my resume to show better evidence for this role?",
    ]
    for index, prompt in enumerate(quick_prompts):
        if st.button(prompt, key=f"assistant_prompt_{index}", use_container_width=True):
            st.session_state.assistant_messages.append({"role": "user", "content": prompt})
            answer = _ask_assistant(prompt)
            st.session_state.assistant_messages.append({"role": "assistant", "content": answer})
            st.rerun()

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.assistant_messages = [
            {
                "role": "assistant",
                "content": "Conversation cleared. Ask a fresh question about your analysis, roadmap, or learning plan.",
            }
        ]
        st.rerun()

    with st.expander("View current assistant context"):
        st.code(_context_block(), language="json")

with right:
    st.markdown("### Conversation")
    for message in st.session_state.assistant_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask about your roadmap, missing skills, role fit, study strategy, or resume improvements")
    if user_prompt:
        st.session_state.assistant_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking with Qwen..."):
                answer = _ask_assistant(user_prompt)
                st.markdown(answer)

        st.session_state.assistant_messages.append({"role": "assistant", "content": answer})

st.markdown("---")
nav1, nav2 = st.columns(2, gap="large")
with nav1:
    if st.button("Back To Analysis", use_container_width=True):
        st.switch_page("pages/analysis.py")
with nav2:
    if st.button("Open Roadmap", use_container_width=True):
        st.switch_page("pages/roadmap.py")

render_footer()

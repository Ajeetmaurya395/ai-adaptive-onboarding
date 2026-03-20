from typing import Dict, List

import streamlit as st

from backend.trace import explain_reasoning


@st.cache_data(show_spinner=False)
def _step_reasoning(resume_summary: str, jd_role: str, skill: str) -> str:
    return explain_reasoning(
        resume_summary,
        jd_role,
        {"missing_skills": [skill]},
    )


def render_timeline(roadmap: List[Dict], analysis_context: Dict | None = None) -> None:
    analysis_context = analysis_context or {}
    resume = analysis_context.get("resume", {})
    jd = analysis_context.get("jd", {})
    resume_summary = resume.get("summary", "")
    jd_role = jd.get("role", "Target Role")

    for index, step in enumerate(roadmap, start=1):
        skill = step.get("skill", "Unknown Skill")
        priority = step.get("priority", "Normal")
        resource = step.get("resource", "Learning Resource")
        duration = step.get("duration", "TBD")
        level = step.get("level", "Intermediate")

        st.markdown(
            f"""
            <div class="roadmap-step">
                <div class="roadmap-step__header">
                    <span class="roadmap-step__index">Step {index}</span>
                    <span class="roadmap-step__priority">{priority}</span>
                </div>
                <h3>{skill}</h3>
                <p class="roadmap-step__resource">{resource}</p>
                <div class="roadmap-step__meta">{duration} • {level}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"Reasoning Trace: {skill}"):
            st.write(_step_reasoning(resume_summary, jd_role, skill))

from typing import List, Dict

import streamlit as st


def render_timeline(roadmap: List[Dict]) -> None:
    for index, step in enumerate(roadmap, start=1):
        skill = step.get("skill", "Unknown Skill")
        priority = step.get("priority", "Normal")
        resource = step.get("resource", "Learning Resource")
        duration = step.get("duration", "TBD")

        st.markdown(
            f"""
            <div class="timeline-step">
                <div class="timeline-step-head">
                    <p class="timeline-step-title">Step {index}: {skill}</p>
                    <span class="timeline-chip">{priority}</span>
                </div>
                <p class="timeline-meta"><b>Resource:</b> {resource}</p>
                <p class="timeline-meta"><b>Estimated Duration:</b> {duration}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

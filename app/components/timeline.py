from typing import Dict, List
import html

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
        resource = step.get("resource") or step.get("course_name") or "Learning Resource"
        duration = step.get("duration", "TBD")
        level = step.get("level", "Intermediate")
        provider = step.get("provider", "")
        url = step.get("url", "")
        learning_resources = step.get("learning_resources", [])

        resource_label = html.escape(resource)
        if url:
            resource_html = f'<a href="{html.escape(url, quote=True)}" target="_blank">{resource_label}</a>'
        else:
            resource_html = resource_label

        meta_bits = [duration, level]
        if provider:
            meta_bits.append(provider)
        meta_text = " • ".join(bit for bit in meta_bits if bit)

        st.markdown(
            f"""
            <div class="roadmap-step">
                <div class="roadmap-step__header">
                    <span class="roadmap-step__index">Step {index}</span>
                    <span class="roadmap-step__priority">{priority}</span>
                </div>
                <h3>{skill}</h3>
                <p class="roadmap-step__resource">{resource_html}</p>
                <div class="roadmap-step__meta">{meta_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if learning_resources:
            st.caption("Learning stack")
            for resource_item in learning_resources:
                item_type = resource_item.get("type", "Resource")
                title = resource_item.get("title", "Untitled resource")
                item_url = resource_item.get("url", "")
                cost = resource_item.get("cost", "")

                if item_url:
                    line = f"**{item_type}:** [{title}]({item_url})"
                else:
                    line = f"**{item_type}:** {title}"

                if cost:
                    line = f"{line} `{cost}`"

                st.markdown(line)
                
                desc = resource_item.get("description")
                if desc:
                    st.markdown(f"*{desc}*")

        with st.expander(f"Reasoning Trace: {skill}"):
            st.write(_step_reasoning(resume_summary, jd_role, skill))

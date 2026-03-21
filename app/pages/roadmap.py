import sys
from pathlib import Path
from typing import List, Dict

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.components.cards import render_metric_card
from app.components.charts import render_roadmap_priority_chart, render_roadmap_duration_chart
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar
from app.components.timeline import render_timeline
from backend.resource_library import build_learning_resources

def init_session_state():
    """Initialize ALL required keys at startup to prevent KeyErrors."""
    defaults = {
        "analysis_result": None,
        "reasoning_trace": "No trace available. Please run an analysis first.",
        "skills": {"matched": [], "missing": []},
        "db_available": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

inject_css()
render_sidebar()


def _sample_roadmap() -> List[Dict]:
    sample_steps = [
        {
            "skill": "AWS",
            "resource": "AWS Cloud Practitioner Path",
            "duration": "3 weeks",
            "priority": "High",
        },
        {
            "skill": "Docker",
            "resource": "Hands-on Docker Project Series",
            "duration": "2 weeks",
            "priority": "High",
        },
        {
            "skill": "CI/CD",
            "resource": "GitHub Actions Deployment Labs",
            "duration": "2 weeks",
            "priority": "Medium",
        },
        {
            "skill": "Kubernetes",
            "resource": "Kubernetes Beginner Bootcamp",
            "duration": "4 weeks",
            "priority": "Medium",
        },
        {
            "skill": "Leadership",
            "resource": "Engineer-to-Stakeholder Communication",
            "duration": "1 week",
            "priority": "Low",
        },
    ]
    for step in sample_steps:
        resources = build_learning_resources(
            step["skill"],
            {"title": step["resource"], "resource": step["resource"], "url": step.get("url", "")},
        )
        step["learning_resources"] = resources
        step["resource_mix"] = ", ".join(item.get("type", "Resource") for item in resources)
        step["free_resource_count"] = sum(1 for item in resources if item.get("cost") == "Free")
        step["paid_resource_count"] = sum(1 for item in resources if item.get("cost") == "Paid")
    return sample_steps


def _resource_table_rows(roadmap: List[Dict]) -> List[Dict]:
    rows: List[Dict] = []
    for step in roadmap:
        learning_resources = step.get("learning_resources", [])
        resource_map = {item.get("type"): item for item in learning_resources}
        # Use documentation description as the 'Resource Info' for the table
        resource_info = resource_map.get("Documentation", {}).get("description", "No description available.")
        
        rows.append({
            "Step": step.get("step"),
            "Skill": step.get("skill"),
            "Priority": step.get("priority"),
            "Duration": step.get("duration"),
            "Primary Resource": step.get("resource") or step.get("course_name"),
            "Resource Info": resource_info,
            "Free Resources": step.get("free_resource_count", 0),
            "Paid Resources": step.get("paid_resource_count", 0),
        })
    return rows


render_page_header(
    "Adaptive Learning Roadmap",
    "Plan your next skills with priority and estimated effort.",
    eyebrow="Roadmap",
)

analysis_result = st.session_state.get("analysis_result") or {}
roadmap = analysis_result.get("roadmap", [])

using_sample = False
if not roadmap:
    using_sample = True
    roadmap = _sample_roadmap()
    st.info("No live analysis found. Showing a sample roadmap preview with charts.")

render_section_intro(
    "Roadmap Plan",
    "Prioritized steps to close skill gaps with estimated learning effort.",
    pills=["Timeline View", "Priority Breakdown", "Duration Forecast"],
)

col1, col2, col3, col4 = st.columns(4, gap="large")
with col1:
    render_metric_card("Roadmap Steps", len(roadmap), "🗺️")
with col2:
    render_metric_card("High Priority", sum(1 for step in roadmap if step.get("priority") == "High"), "🔥")
with col3:
    render_metric_card("Free Resources", sum(step.get("free_resource_count", 0) for step in roadmap), "📚")
with col4:
    render_metric_card("Mode", "Sample" if using_sample else "Live", "⚙️")

tab1, tab2, tab3 = st.tabs(["Timeline", "Charts", "Table"])
with tab1:
    st.subheader("Learning Timeline")
    render_timeline(roadmap, st.session_state.get("analysis_result"))

with tab2:
    left, right = st.columns(2, gap="large")
    with left:
        render_roadmap_priority_chart(roadmap)
    with right:
        render_roadmap_duration_chart(roadmap)

with tab3:
    st.dataframe(_resource_table_rows(roadmap), use_container_width=True, hide_index=True)

st.markdown("---")
if st.button("Back To Upload", use_container_width=True):
    st.switch_page("pages/upload.py")

render_footer()

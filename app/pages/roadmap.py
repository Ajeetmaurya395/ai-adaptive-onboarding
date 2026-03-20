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

inject_css()
render_sidebar()


def _sample_roadmap() -> List[Dict]:
    return [
        {
            "skill": "AWS Foundations",
            "resource": "AWS Cloud Practitioner Path",
            "duration": "3 weeks",
            "priority": "High",
        },
        {
            "skill": "Docker + Containers",
            "resource": "Hands-on Docker Project Series",
            "duration": "2 weeks",
            "priority": "High",
        },
        {
            "skill": "CI/CD Pipelines",
            "resource": "GitHub Actions Deployment Labs",
            "duration": "2 weeks",
            "priority": "Medium",
        },
        {
            "skill": "Kubernetes Basics",
            "resource": "Kubernetes Beginner Bootcamp",
            "duration": "4 weeks",
            "priority": "Medium",
        },
        {
            "skill": "Technical Communication",
            "resource": "Engineer-to-Stakeholder Communication",
            "duration": "1 week",
            "priority": "Low",
        },
    ]


render_page_header(
    "Adaptive Learning Roadmap",
    "Plan your next skills with priority and estimated effort.",
    eyebrow="Roadmap",
)

roadmap = []
if "analysis_result" in st.session_state:
    roadmap = st.session_state.analysis_result.get("roadmap", [])

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

col1, col2, col3 = st.columns(3, gap="large")
with col1:
    render_metric_card("Roadmap Steps", len(roadmap), "🗺️")
with col2:
    render_metric_card("High Priority", sum(1 for step in roadmap if step.get("priority") == "High"), "🔥")
with col3:
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
    st.dataframe(roadmap, use_container_width=True, hide_index=True)

st.markdown("---")
if st.button("Back To Upload", use_container_width=True):
    st.switch_page("pages/upload.py")

render_footer()

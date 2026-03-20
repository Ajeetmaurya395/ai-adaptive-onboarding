import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar
from backend.trace import explain_reasoning

inject_css()
render_sidebar()

render_page_header(
    "AI Reasoning Trace",
    "Understand why the system identified specific skill gaps.",
    eyebrow="Explainability",
)

if "analysis_result" not in st.session_state:
    st.warning("Run an analysis first from the Upload page.")
    render_footer()
    st.stop()

data = st.session_state.analysis_result
reasoning = explain_reasoning(
    data["resume"].get("summary", ""),
    data["jd"].get("role", ""),
    data["gap"],
)

render_section_intro(
    "Model Explanation",
    "Why the model determined this gap profile and what signals influenced it.",
    pills=["Context-Aware", "Role-Specific", "Actionable"],
)

st.markdown(
    f"""
    <div class="section-card" style="border-left: 4px solid #0891b2;">
        <h4 style="margin-top:0;">Why this gap exists</h4>
        <p style="margin-bottom:0;">{reasoning}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.subheader("Extraction Trace")
st.json(data["resume"])

st.write("")
st.subheader("Gap Snapshot")
c1, c2 = st.columns(2, gap="large")
with c1:
    st.metric("Matched Skills", len(data["gap"].get("matched_skills", [])))
with c2:
    st.metric("Missing Skills", len(data["gap"].get("missing_skills", [])))

st.markdown("---")
if st.button("Open Roadmap", use_container_width=True):
    st.switch_page("pages/roadmap.py")

render_footer()

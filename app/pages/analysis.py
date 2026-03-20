import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.components.cards import render_metric_card
from app.components.charts import render_radar_chart, render_gap_donut
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar

inject_css()
render_sidebar()

render_page_header(
    "Skill Gap Analysis",
    "A concise view of current fit versus target role expectations.",
    eyebrow="Insights",
)

if "analysis_result" not in st.session_state:
    st.warning("Please run an analysis from the Upload page first.")
    render_footer()
    st.stop()

data = st.session_state.analysis_result
gap = data["gap"]

render_section_intro(
    "Gap Overview",
    "Review your fit score and inspect where upskilling is needed.",
    pills=["Coverage Score", "Matched Skills", "Missing Skills"],
)

col1, col2, col3 = st.columns(3, gap="large")
with col1:
    render_metric_card("Match Score", f"{gap.get('match_score', 0)}%", "🎯")
with col2:
    render_metric_card("Missing Skills", len(gap["missing_skills"]), "⚠️")
with col3:
    render_metric_card("Matched Skills", len(gap["matched_skills"]), "✅")

st.write("")
chart_col1, chart_col2 = st.columns(2, gap="large")
with chart_col1:
    render_radar_chart(gap["matched_skills"], gap["missing_skills"])
with chart_col2:
    render_gap_donut(len(gap["matched_skills"]), len(gap["missing_skills"]))

st.subheader("Skill Details")
c1, c2 = st.columns(2, gap="large")

matched_html = "".join(
    [f'<span class="skill-chip match">{skill}</span>' for skill in gap["matched_skills"]]
) or '<span class="skill-chip match">None</span>'
missing_html = "".join(
    [f'<span class="skill-chip miss">{skill}</span>' for skill in gap["missing_skills"]]
) or '<span class="skill-chip miss">None</span>'

with c1:
    st.markdown(
        f"""
        <div class="section-card">
            <h4 style="margin:0 0 6px 0;">Matched Skills</h4>
            <div class="skill-chip-wrap">{matched_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""
        <div class="section-card">
            <h4 style="margin:0 0 6px 0;">Missing Skills</h4>
            <div class="skill-chip-wrap">{missing_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
go1, go2 = st.columns(2, gap="large")
with go1:
    if st.button("Open Roadmap", use_container_width=True):
        st.switch_page("pages/roadmap.py")
with go2:
    if st.button("View Reasoning Trace", use_container_width=True):
        st.switch_page("pages/reasoning.py")

render_footer()

import streamlit as st
from app.components.cards import render_metric_card
from app.components.charts import render_radar_chart

st.title("📊 Skill Gap Analysis")

if "analysis_result" not in st.session_state:
    st.warning("Please run analysis on the Upload page first.")
    st.stop()

data = st.session_state.analysis_result
gap = data["gap"]

col1, col2, col3 = st.columns(3)
with col1:
    render_metric_card("Match Score", f"{gap['match_score']}%", "🎯")
with col2:
    render_metric_card("Missing Skills", len(gap["missing_skills"]), "⚠️")
with col3:
    render_metric_card("Matched Skills", len(gap["matched_skills"]), "✅")

st.subheader("Visualization")
render_radar_chart(gap["matched_skills"], gap["missing_skills"])

st.subheader("Details")
c1, c2 = st.columns(2)
with c1:
    st.info(f"**Matched:** {', '.join(gap['matched_skills']) or 'None'}")
with c2:
    st.error(f"**Missing:** {', '.join(gap['missing_skills']) or 'None'}")
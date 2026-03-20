import streamlit as st
from app.components.timeline import render_timeline

st.title("🗺️ Adaptive Learning Roadmap")

if "analysis_result" not in st.session_state:
    st.warning("No analysis data found.")
    st.stop()

roadmap = st.session_state.analysis_result.get("roadmap", [])

if not roadmap:
    st.success("No gaps found! You are ready for this role.")
else:
    render_timeline(roadmap)
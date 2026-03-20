import streamlit as st

def render_timeline(roadmap):
    for i, step in enumerate(roadmap):
        with st.expander(f"Step {i+1}: {step.get('skill', 'Unknown')} ({step.get('priority', 'Normal')})"):
            st.write(f"**Resource:** {step.get('resource')}")
            st.write(f"**Duration:** {step.get('duration')}")
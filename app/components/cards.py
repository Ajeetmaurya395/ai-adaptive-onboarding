import streamlit as st

def render_metric_card(label, value, icon="📊"):
    st.markdown(f"""
    <div class="metric-card">
        <h3>{icon} {label}</h3>
        <h1>{value}</h1>
    </div>
    """, unsafe_allow_html=True)
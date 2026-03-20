import plotly.express as px
import streamlit as st

def render_radar_chart(matched, missing):
    labels = ['Matched', 'Missing']
    values = [len(matched), len(missing)]
    
    fig = px.bar_polar(
        r=values, 
        theta=labels,
        color=["#4CAF50", "#F44336"],
        template="plotly_dark",
        title="Skill Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)
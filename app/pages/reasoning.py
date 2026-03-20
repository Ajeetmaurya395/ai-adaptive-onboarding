import streamlit as st
from backend.trace import explain_reasoning

st.title("🧠 AI Reasoning Trace")

if "analysis_result" not in st.session_state:
    st.warning("Run analysis first.")
    st.stop()

data = st.session_state.analysis_result
reasoning = explain_reasoning(
    data["resume"].get("summary", ""),
    data["jd"].get("role", ""),
    data["gap"]
)

st.markdown(f"""
<div style="background-color: #1c1f26; padding: 20px; border-radius: 10px; border-left: 5px solid #2196F3;">
    <h3>Why this gap exists:</h3>
    <p>{reasoning}</p>
</div>
""", unsafe_allow_html=True)

st.write("### Extraction Trace")
st.json(data["resume"])
import streamlit as st
from app.database import get_history
import pandas as pd

st.title("📜 Analysis History")

if not st.session_state.get("user_id"):
    st.warning("Please login to view history.")
    st.stop()

history = get_history(st.session_state.user_id)

if history:
    df = pd.DataFrame(history, columns=["Score", "Date"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("No previous analyses found.")
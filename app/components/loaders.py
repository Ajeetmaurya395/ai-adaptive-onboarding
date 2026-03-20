import streamlit as st
import time

def loading_spinner(text="Processing..."):
    with st.spinner(text):
        time.sleep(1.5) # Simulate processing time for UX
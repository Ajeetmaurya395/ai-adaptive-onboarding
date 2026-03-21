from contextlib import contextmanager
import streamlit as st
import time

@contextmanager
def loading_spinner(text="Processing..."):
    with st.spinner(text):
        time.sleep(1.0) # UX pause
        yield
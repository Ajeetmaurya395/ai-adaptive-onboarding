import streamlit as st

def set_session_state(key, value):
    st.session_state[key] = value

def get_session_state(key, default=None):
    return st.session_state.get(key, default)

def reset_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
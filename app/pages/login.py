import sys
import time
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.auth import login
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar

inject_css()
render_sidebar()

render_page_header(
    "Welcome Back",
    "Sign in to continue your analyses, roadmap progress, and history.",
    eyebrow="Account",
)

if st.session_state.get("logged_in"):
    username = st.session_state.get("username", "user")
    st.success(f"Already logged in as {username}.")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        if st.button("Open Home", use_container_width=True):
            st.switch_page("ui.py")
    with c2:
        if st.button("Open Upload", use_container_width=True):
            st.switch_page("pages/upload.py")
    render_footer()
    st.stop()

render_section_intro(
    "Login",
    "Enter your username/email and password to access saved work.",
    pills=["Secure Session", "History Sync", "Roadmap Persistence"],
)

with st.form("login_page_form"):
    identifier = st.text_input("Username or Email", placeholder="Enter username or email")
    password = st.text_input("Password", type="password", placeholder="Enter password")
    keep_signed_in = st.checkbox("Keep me signed in on this device")
    submit = st.form_submit_button("Login", use_container_width=True)

if submit:
    if not identifier or not password:
        st.error("Please fill in both fields.")
    else:
        with st.spinner("Authenticating..."):
            success, result = login(identifier, password)
        if success:
            st.session_state.logged_in = True
            st.session_state.user_id = result["id"]
            st.session_state.username = result["username"]
            st.session_state.user_email = result["email"]
            st.session_state.keep_signed_in = keep_signed_in
            st.success(f"Welcome back, {result['username']}.")
            time.sleep(0.6)
            st.switch_page("ui.py")
        else:
            st.error("Invalid credentials. Please try again.")

st.write("")
a1, a2 = st.columns(2, gap="large")
with a1:
    if st.button("Create New Account", use_container_width=True):
        st.switch_page("pages/register.py")
with a2:
    if st.button("Try Demo Account", use_container_width=True):
        st.session_state.logged_in = True
        st.session_state.user_id = "demo_user"
        st.session_state.username = "demo"
        st.session_state.user_email = "demo@example.com"
        st.success("Demo mode activated.")
        time.sleep(0.3)
        st.switch_page("ui.py")

render_footer()

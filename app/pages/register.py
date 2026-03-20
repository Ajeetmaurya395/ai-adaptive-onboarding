import sys
import time
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.auth import register
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar

inject_css()
render_sidebar()

render_page_header(
    "Create Your Account",
    "Register once to track analyses, save roadmaps, and review progress anytime.",
    eyebrow="Account",
)

if st.session_state.get("logged_in"):
    username = st.session_state.get("username", "user")
    st.info(f"You are currently logged in as {username}.")
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
    "Register",
    "Fill in your details to create a secure account.",
    pills=["Username", "Email", "Password Rules"],
)

with st.form("register_page_form"):
    username = st.text_input("Username", placeholder="3-20 alphanumeric chars")
    email = st.text_input("Email", placeholder="you@example.com")
    password = st.text_input("Password", type="password", placeholder="Min 6 chars with letters and numbers")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
    terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
    submit = st.form_submit_button("Create Account", use_container_width=True)

if submit:
    if not all([username, email, password, confirm_password]):
        st.error("Please complete all fields.")
    elif password != confirm_password:
        st.error("Passwords do not match.")
    elif not terms:
        st.error("Please accept terms to continue.")
    else:
        with st.spinner("Creating account..."):
            success, msg = register(username, email, password)
        if success:
            st.success(msg)
            st.info("Account created successfully. Continue to Login.")
            time.sleep(0.5)
        else:
            st.error(msg)

st.write("")
if st.button("Already have an account? Login", use_container_width=True):
    st.switch_page("pages/login.py")

render_footer()

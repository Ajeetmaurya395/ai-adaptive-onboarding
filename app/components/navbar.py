import streamlit as st

def render_sidebar():
    st.sidebar.title("🚀 AI Onboarding")
    st.sidebar.markdown("---")
    
    if st.session_state.get("logged_in"):
        st.sidebar.write(f"👤 {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.rerun()
    else:
        st.sidebar.info("Please login to access history.")
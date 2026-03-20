import streamlit as st
import time
from app.assets.theme import inject_css
from app.components.navbar import render_sidebar
from app.database import init_db, create_user, verify_user, get_history, get_user_stats
from app.auth import login, register
from app.utils import reset_session

# Initialize database connection
init_db()
inject_css()

st.set_page_config(
    page_title="AI Adaptive Onboarding", 
    layout="wide", 
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

render_sidebar()

# Auth Logic
if not st.session_state.get("logged_in"):
    st.title("🔐 Welcome to AI Adaptive Onboarding")
    st.markdown("""
    ### Intelligent Career Development Platform
    
    ✨ **Features:**
    - 🧠 AI-powered resume & JD analysis
    - 📊 Skill gap visualization
    - 🗺️ Personalized learning roadmaps
    - 🔍 Explainable recommendations
    
    *Powered by Qwen2.5-7B-Instruct & MongoDB*
    """)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        with st.form("login_form"):
            identifier = st.text_input("Username or Email", placeholder="Enter username or email")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not identifier or not password:
                    st.error("Please fill in all fields")
                else:
                    with st.spinner("Authenticating..."):
                        success, result = login(identifier, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_id = result["id"]
                            st.session_state.username = result["username"]
                            st.session_state.user_email = result["email"]
                            st.success(f"Welcome back, {result['username']}! 🎉")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please try again.")
    
    with tab2:
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_user = st.text_input("Username", placeholder="3-20 alphanumeric chars")
                new_email = st.text_input("Email", placeholder="you@example.com")
            with col2:
                new_pass = st.text_input("Password", type="password", placeholder="Min 6 chars, letter + number")
                confirm_pass = st.text_input("Confirm Password", type="password")
            
            terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            submit = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit:
                if not all([new_user, new_email, new_pass, confirm_pass]):
                    st.error("Please fill in all fields")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match")
                elif not terms:
                    st.error("Please agree to the terms to continue")
                else:
                    with st.spinner("Creating account..."):
                        success, msg = register(new_user, new_email, new_pass)
                        if success:
                            st.success(msg)
                            st.info("You can now login with your credentials!")
                        else:
                            st.error(msg)
    
    # Demo access
    st.markdown("---")
    st.markdown("##### 🎮 Quick Demo")
    if st.button("Try Demo Account", use_container_width=True, type="secondary"):
        st.session_state.logged_in = True
        st.session_state.user_id = "demo_user"
        st.session_state.username = "demo"
        st.success("🎉 Demo mode activated! Explore the platform.")
        time.sleep(1)
        st.rerun()

else:
    # Logged in view
    st.title(f"👋 Welcome, {st.session_state.username}!")
    
    # User stats dashboard
    if st.session_state.user_id != "demo_user":
        with st.spinner("Loading your stats..."):
            stats = get_user_stats(st.session_state.user_id)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📈 Analyses", stats.get("total_analyses", 0))
        with col2:
            st.metric("🎯 Avg Score", f"{stats.get('avg_score', 0):.1f}%")
        with col3:
            st.metric("⭐ Best Score", f"{stats.get('best_score', 0):.1f}%")
        with col4:
            last = stats.get("last_analysis")
            if last:
                st.metric("🕐 Last Analysis", last.strftime("%b %d"))
            else:
                st.metric("🕐 Last Analysis", "Never")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 New Analysis", use_container_width=True, type="primary"):
            st.switch_page("pages/upload.py")
    
    with col2:
        if st.button("🗺️ View Roadmaps", use_container_width=True):
            st.switch_page("pages/roadmap.py")
    
    with col3:
        if st.button("📜 History", use_container_width=True):
            st.switch_page("pages/history.py")
    
    # Recent activity
    if st.session_state.user_id != "demo_user":
        st.markdown("### 📋 Recent Activity")
        history = get_history(st.session_state.user_id, days=7)
        
        if history:
            for item in history[:5]:
                with st.expander(f"📊 Analysis - {item['score']}% match ({item['created_at'].strftime('%b %d, %H:%M')})"):
                    gap = item.get("gap_summary", {})
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"✅ Matched: {gap.get('matched', 0)} skills")
                    c2.write(f"⚠️ Missing: {gap.get('missing', 0)} skills")
                    c3.write(f"🎯 Score: {item['score']}%")
        else:
            st.info("📭 No recent analyses. Start with a new analysis!")
    
    # Navigation helper
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: var(--text-muted);">
        <small>Navigate using the sidebar • 
        <a href="/upload" style="color: var(--secondary);">Start Analysis</a> • 
        <a href="/evaluation" style="color: var(--secondary);">System Metrics</a>
        </small>
    </div>
    """, unsafe_allow_html=True)    
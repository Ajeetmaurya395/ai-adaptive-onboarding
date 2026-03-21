import streamlit as st


_MAIN_NAV_ITEMS = [
    (["ui.py", "../ui.py", "app/ui.py"], "Home", "🏠"),
    (["pages/hackathon.py", "hackathon.py", "../pages/hackathon.py", "app/pages/hackathon.py"], "Hackathon", "🏆"),
    (["pages/upload.py", "upload.py", "../pages/upload.py", "app/pages/upload.py"], "Upload", "📄"),
    (["pages/analysis.py", "analysis.py", "../pages/analysis.py", "app/pages/analysis.py"], "Analysis", "📊"),
    (["pages/roadmap.py", "roadmap.py", "../pages/roadmap.py", "app/pages/roadmap.py"], "Roadmap", "🗺️"),
    (["pages/reasoning.py", "reasoning.py", "../pages/reasoning.py", "app/pages/reasoning.py"], "Reasoning", "🧠"),
    (["pages/assistant.py", "assistant.py", "../pages/assistant.py", "app/pages/assistant.py"], "Assistant", "💬"),
    (["pages/history.py", "history.py", "../pages/history.py", "app/pages/history.py"], "History", "📜"),
    (["pages/evaluation.py", "evaluation.py", "../pages/evaluation.py", "app/pages/evaluation.py"], "Evaluation", "🔎"),
]

_AUTH_NAV_ITEMS = [
    (["pages/login.py", "login.py", "../pages/login.py", "app/pages/login.py"], "Login", "🔐"),
    (["pages/register.py", "register.py", "../pages/register.py", "app/pages/register.py"], "Register", "📝"),
]


def _safe_page_link(candidates: list[str], label: str, icon: str) -> None:
    for path in candidates:
        try:
            st.sidebar.page_link(path, label=label, icon=icon)
            return
        except Exception:
            continue
    st.sidebar.write(f"{icon} {label}")


def _render_page_links(items: list[tuple[list[str], str, str]]) -> None:
    for candidates, label, icon in items:
        _safe_page_link(candidates, label, icon)


def render_sidebar() -> None:
    if "app_surface_mode" not in st.session_state:
        st.session_state.app_surface_mode = "Light"

    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">Adaptive Onboarding</div>
            <div class="sidebar-brand-sub">White + Cyan Intelligence Workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div class="theme-toggle-card">
            <div class="theme-toggle-title">Appearance</div>
            <div class="theme-toggle-sub">Keep one glass palette across the whole workspace.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.radio(
        "Workspace appearance",
        ["Light", "Dark"],
        key="app_surface_mode",
        horizontal=True,
        label_visibility="collapsed",
    )

    st.sidebar.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)
    _render_page_links(_MAIN_NAV_ITEMS)

    st.sidebar.markdown('<div class="sidebar-section">Account</div>', unsafe_allow_html=True)
    _render_page_links(_AUTH_NAV_ITEMS)

    st.sidebar.markdown('<div class="sidebar-section">Session</div>', unsafe_allow_html=True)
    if st.session_state.get("logged_in"):
        username = st.session_state.get("username", "user")
        st.sidebar.caption(f"Signed in as `{username}`")
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.user_email = None
            st.rerun()
    else:
        st.sidebar.info("Login to save analysis history and roadmap progress.")

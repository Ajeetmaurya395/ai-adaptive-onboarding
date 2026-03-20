import datetime as dt

import streamlit as st


def render_page_header(title: str, subtitle: str = "", eyebrow: str = "AI Adaptive Onboarding") -> None:
    st.markdown(
        f"""
        <section class="app-header">
            <div class="app-eyebrow">{eyebrow}</div>
            <h1 class="app-header-title">{title}</h1>
            <p class="app-header-subtitle">{subtitle}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_footer(note: str = "Built for role-fit analysis, roadmap planning, and explainable career guidance.") -> None:
    year = dt.datetime.now().year
    st.markdown(
        f"""
        <footer class="app-footer">
            {note} &nbsp;&bull;&nbsp; {year}
        </footer>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(title: str, subtitle: str = "", pills: list[str] | None = None) -> None:
    pill_html = ""
    if pills:
        rows = "".join([f'<span class="pill">{pill}</span>' for pill in pills])
        pill_html = f'<div class="pill-row">{rows}</div>'
    st.markdown(
        f"""
        <div class="section-card">
            <h3 class="section-title">{title}</h3>
            <p class="section-subtitle">{subtitle}</p>
            {pill_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

import streamlit as st


def render_metric_card(label: str, value, icon: str = "📊") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card__header">
                <span class="metric-card__icon">{icon}</span>
                <span class="metric-card__label">{label}</span>
            </div>
            <div class="metric-card__value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

from typing import List, Dict
import re

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


_CYAN = "#06b6d4"
_CYAN_DARK = "#0891b2"
_CYAN_LIGHT = "#bae6fd"
_MUTED = "#475569"


def render_radar_chart(matched: List[str], missing: List[str]) -> None:
    labels = ["Matched", "Missing"]
    values = [len(matched), len(missing)]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values + values[:1],
                theta=labels + labels[:1],
                fill="toself",
                line=dict(color=_CYAN_DARK, width=3),
                fillcolor="rgba(6,182,212,0.28)",
                name="Skill Coverage",
            )
        ]
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(values + [1]) + 1], gridcolor="#e2f3fa"),
            angularaxis=dict(gridcolor="#e2f3fa"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        title="Skill Distribution",
        font=dict(color=_MUTED),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_gap_donut(matched_count: int, missing_count: int) -> None:
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Matched", "Missing"],
                values=[matched_count, missing_count],
                hole=0.58,
                marker=dict(colors=[_CYAN_DARK, "#f97316"]),
                textinfo="label+percent",
            )
        ]
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_MUTED),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _duration_to_weeks(duration: str) -> float:
    if not duration:
        return 0.0
    match = re.search(r"(\d+(\.\d+)?)", duration)
    if not match:
        return 0.0

    value = float(match.group(1))
    duration_lower = duration.lower()
    if "month" in duration_lower:
        return value * 4
    if "day" in duration_lower:
        return value / 7
    if "hour" in duration_lower:
        return value / 40
    return value


def render_roadmap_priority_chart(roadmap: List[Dict]) -> None:
    if not roadmap:
        st.info("No roadmap data available for priority chart.")
        return

    priority_counts: Dict[str, int] = {}
    for item in roadmap:
        key = item.get("priority", "Unspecified")
        priority_counts[key] = priority_counts.get(key, 0) + 1

    fig = px.pie(
        names=list(priority_counts.keys()),
        values=list(priority_counts.values()),
        title="Roadmap by Priority",
        color=list(priority_counts.keys()),
        color_discrete_sequence=["#0891b2", "#06b6d4", "#67e8f9", "#facc15"],
        hole=0.45,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=48, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_MUTED),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_roadmap_duration_chart(roadmap: List[Dict]) -> None:
    if not roadmap:
        st.info("No roadmap data available for duration chart.")
        return

    skills = [item.get("skill", "Unknown") for item in roadmap]
    weeks = [_duration_to_weeks(item.get("duration", "")) for item in roadmap]

    fig = px.bar(
        x=skills,
        y=weeks,
        title="Estimated Effort by Skill (Weeks)",
        labels={"x": "Skill", "y": "Weeks"},
        color=weeks,
        color_continuous_scale=["#d5f5ff", "#06b6d4", "#0e7490"],
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=48, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_MUTED),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor=_CYAN_LIGHT),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_history_trend(scores: List[float], labels: List[str]) -> None:
    if not scores:
        st.info("No score trend available yet.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=scores,
            mode="lines+markers",
            line=dict(color=_CYAN_DARK, width=3),
            marker=dict(size=8, color=_CYAN),
            fill="tozeroy",
            fillcolor="rgba(6, 182, 212, 0.16)",
            name="Score",
        )
    )
    fig.update_layout(
        title="Analysis Score Trend",
        margin=dict(l=10, r=10, t=48, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor=_CYAN_LIGHT, range=[0, 100]),
        font=dict(color=_MUTED),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_metrics_comparison(metrics: Dict) -> None:
    keys = ["accuracy", "precision", "recall", "f1_score"]
    values = [float(metrics.get(k, 0)) for k in keys]
    names = ["Accuracy", "Precision", "Recall", "F1 Score"]

    fig = px.bar(
        x=names,
        y=values,
        labels={"x": "Metric", "y": "Score (%)"},
        color=values,
        color_continuous_scale=["#d5f5ff", "#06b6d4", "#0e7490"],
        title="Evaluation Metrics",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=48, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor=_CYAN_LIGHT, range=[0, 100]),
        font=dict(color=_MUTED),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

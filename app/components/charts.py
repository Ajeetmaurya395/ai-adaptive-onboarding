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


def render_match_gauge(score: int) -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=max(0, min(score, 100)),
            number={"suffix": "%", "font": {"size": 42, "color": _CYAN_DARK}},
            title={"text": "Role Fit Gauge"},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": _CYAN_LIGHT},
                "bar": {"color": _CYAN_DARK},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 40], "color": "rgba(249,115,22,0.22)"},
                    {"range": [40, 70], "color": "rgba(250,204,21,0.2)"},
                    {"range": [70, 100], "color": "rgba(6,182,212,0.2)"},
                ],
                "threshold": {
                    "line": {"color": "#0e7490", "width": 6},
                    "thickness": 0.75,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_MUTED),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_category_gap_bars(category_scores: Dict[str, int]) -> None:
    if not category_scores:
        st.info("No category comparison available yet.")
        return

    labels = list(category_scores.keys())
    values = [int(category_scores[label]) for label in labels]
    gaps = [max(0, 100 - value) for value in values]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            name="Current Coverage",
            marker=dict(color="#0891b2"),
            text=[f"{value}%" for value in values],
            textposition="inside",
        )
    )
    fig.add_trace(
        go.Bar(
            x=gaps,
            y=labels,
            orientation="h",
            name="Remaining Opportunity",
            marker=dict(color="rgba(249,115,22,0.25)"),
            text=[f"{gap}%" if gap else "" for gap in gaps],
            textposition="outside",
        )
    )
    fig.update_layout(
        barmode="stack",
        title="Category Coverage vs Remaining Opportunity",
        margin=dict(l=10, r=10, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_MUTED),
        xaxis=dict(range=[0, 100], gridcolor=_CYAN_LIGHT, title="Coverage"),
        yaxis=dict(showgrid=False),
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_skill_status_treemap(matched: List[str], missing: List[str]) -> None:
    labels = ["Skill Coverage", "Matched", "Missing"] + matched + missing
    parents = ["", "Skill Coverage", "Skill Coverage"] + (["Matched"] * len(matched)) + (["Missing"] * len(missing))
    values = [len(matched) + len(missing), len(matched), len(missing)] + ([1] * len(matched)) + ([1] * len(missing))
    colors = [
        "rgba(6,182,212,0.1)",
        "rgba(8,145,178,0.75)",
        "rgba(249,115,22,0.72)",
    ] + (["rgba(8,145,178,0.62)"] * len(matched)) + (["rgba(249,115,22,0.52)"] * len(missing))

    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=colors),
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><extra></extra>",
        )
    )
    fig.update_layout(
        title="Interactive Skill Coverage Map",
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_MUTED),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_gap_priority_matrix(roadmap: List[Dict]) -> None:
    if not roadmap:
        st.info("No roadmap data available for the gap priority matrix.")
        return

    priority_scale = {"High": 3, "Medium": 2, "Low": 1}
    labels = [item.get("skill", "Unknown") for item in roadmap]
    priorities = [priority_scale.get(item.get("priority", "Low"), 1) for item in roadmap]
    weeks = [_duration_to_weeks(item.get("duration", "")) or 1 for item in roadmap]
    resource_counts = [max(1, len(item.get("learning_resources", []))) for item in roadmap]
    colors = [item.get("priority", "Low") for item in roadmap]

    fig = px.scatter(
        x=priorities,
        y=weeks,
        size=resource_counts,
        color=colors,
        text=labels,
        color_discrete_map={"High": "#0891b2", "Medium": "#06b6d4", "Low": "#67e8f9"},
        labels={"x": "Priority Level", "y": "Estimated Effort (Weeks)", "color": "Priority"},
        title="Gap Priority Matrix",
    )
    fig.update_traces(textposition="top center", marker=dict(opacity=0.82, line=dict(width=1, color="#d8f3fb")))
    fig.update_layout(
        margin=dict(l=10, r=10, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_MUTED),
        xaxis=dict(
            tickmode="array",
            tickvals=[1, 2, 3],
            ticktext=["Low", "Medium", "High"],
            gridcolor=_CYAN_LIGHT,
        ),
        yaxis=dict(gridcolor=_CYAN_LIGHT),
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


def render_skill_radar(current_skills: Dict[str, int], required_skills: Dict[str, int]) -> None:
    """Render a radar chart comparing current skill levels against job requirements.

    Args:
        current_skills: mapping of skill name → proficiency (0-100).
        required_skills: mapping of skill name → required level (0-100).
    """
    if not required_skills:
        st.info("No skill data available for radar chart.")
        return

    categories = list(required_skills.keys())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[current_skills.get(cat, 0) for cat in categories],
        theta=categories,
        fill='toself',
        name='Your Current Level',
        line=dict(color='#4b6cb7', width=2),
        fillcolor='rgba(75,108,183,0.25)',
    ))

    fig.add_trace(go.Scatterpolar(
        r=[required_skills.get(cat, 0) for cat in categories],
        theta=categories,
        fill='toself',
        name='Job Requirements',
        line=dict(color='#00d4ff', width=2),
        fillcolor='rgba(0,212,255,0.15)',
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(6,182,212,0.2)'),
            angularaxis=dict(gridcolor='rgba(6,182,212,0.2)'),
            bgcolor='rgba(0,0,0,0)',
        ),
        showlegend=True,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=_MUTED),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

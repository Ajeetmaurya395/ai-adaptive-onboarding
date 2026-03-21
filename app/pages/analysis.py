import sys
from pathlib import Path
from typing import Dict, List

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.components.cards import render_metric_card
from app.components.charts import (
    render_category_gap_bars,
    render_gap_donut,
    render_gap_priority_matrix,
    render_match_gauge,
    render_skill_radar,
    render_skill_status_treemap,
)
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar


def init_session_state():
    """Initialize ALL required keys at startup to prevent KeyErrors."""
    defaults = {
        "analysis_result": None,
        "reasoning_trace": "No trace available. Please run an analysis first.",
        "skills": {"matched": [], "missing": []},
        "db_available": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _fit_label(score: int) -> str:
    if score >= 85:
        return "Strong fit"
    if score >= 65:
        return "Close fit"
    if score >= 40:
        return "Developing fit"
    return "Early-stage fit"


def _fit_guidance(score: int, missing_count: int) -> str:
    if missing_count == 0:
        return "Your profile already covers the core role signals. Focus on proof, polish, and stronger resume storytelling."
    if score >= 80:
        return "You are already close to the target. A few focused improvements can move you from almost-ready to interview-ready."
    if score >= 60:
        return "You have real overlap with the role. The biggest gains will come from closing the missing skills in a clear priority order."
    return "The role is still reachable, but the best approach is to strengthen the foundations first and then add stronger project evidence."


def _roadmap_lookup(roadmap: List[Dict]) -> Dict[str, Dict]:
    return {step.get("skill", ""): step for step in roadmap if step.get("skill")}


def _render_skill_chips(title: str, skills: List[str], chip_class: str) -> None:
    chip_html = "".join([f'<span class="skill-chip {chip_class}">{skill}</span>' for skill in skills])
    if not chip_html:
        chip_html = f'<span class="skill-chip {chip_class}">None</span>'
    st.markdown(
        f"""
        <div class="section-card">
            <h4 style="margin:0 0 8px 0;">{title}</h4>
            <div class="skill-chip-wrap">{chip_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_learning_stack(step: Dict) -> None:
    resources = step.get("learning_resources", [])
    if not resources:
        st.info("No learning stack was attached to this step yet.")
        return

    for item in resources:
        label = item.get("type", "Resource")
        title = item.get("title", "Untitled resource")
        url = item.get("url", "")
        cost = item.get("cost", "")
        line = f"**{label}:** [{title}]({url})" if url else f"**{label}:** {title}"
        if cost:
            line = f"{line} `{cost}`"
        st.markdown(line)


init_session_state()

inject_css()
render_sidebar()

render_page_header(
    "Skill Gap Analysis",
    "Explore the fit score, drill into skills, and understand where the biggest improvement opportunities are.",
    eyebrow="Insights",
)

if st.session_state.analysis_result is None:
    st.warning("Please run an analysis from the Upload page first.")
    render_footer()
    st.stop()

data = st.session_state.analysis_result
summary = data.get("summary", {})
skills = data.get("skills", {})
gap = data.get("gap", {})
resume = data.get("resume", {})
jd = data.get("jd", {})
roadmap = data.get("roadmap", [])

matched_skills = gap.get("matched_skills", [])
missing_skills = gap.get("missing_skills", [])
all_required = skills.get("all_required", matched_skills + missing_skills)
match_score = int(gap.get("match_score", summary.get("match_score", 0)) or 0)
fit_label = _fit_label(match_score)
role = summary.get("role_detected") or jd.get("role") or "Target Role"
roadmap_by_skill = _roadmap_lookup(roadmap)

render_section_intro(
    "Interactive Gap Overview",
    "Use the visuals to understand fit, then inspect individual skills and learning priorities in more detail.",
    pills=["Live Analysis", "Interactive Charts", "Skill Drilldown", "Action Plan"],
)

metric1, metric2, metric3, metric4 = st.columns(4, gap="large")
with metric1:
    render_metric_card("Match Score", f"{match_score}%", "🎯")
with metric2:
    render_metric_card("Fit Level", fit_label, "🧭")
with metric3:
    render_metric_card("Missing Skills", len(missing_skills), "⚠️")
with metric4:
    render_metric_card("Required Skills", len(all_required), "🧩")

st.progress(max(0, min(match_score, 100)) / 100)
st.caption(_fit_guidance(match_score, len(missing_skills)))

overview_tab, explorer_tab, strategy_tab = st.tabs(["Visual Overview", "Skill Explorer", "Strategy Board"])

with overview_tab:
    top_left, top_right = st.columns(2, gap="large")
    with top_left:
        render_match_gauge(match_score)
    with top_right:
        render_skill_status_treemap(matched_skills, missing_skills)

    bottom_left, bottom_right = st.columns(2, gap="large")
    with bottom_left:
        category_scores = gap.get("category_scores", {"Technology": 0, "Core Skills": 0, "Knowledge": 0})
        required_categories = {cat: 100 for cat in category_scores.keys()}
        render_skill_radar(category_scores, required_categories)
    with bottom_right:
        render_gap_donut(len(matched_skills), len(missing_skills))

    chip1, chip2 = st.columns(2, gap="large")
    with chip1:
        _render_skill_chips("Skills already covered", matched_skills, "match")
    with chip2:
        _render_skill_chips("Skills still missing", missing_skills, "miss")

with explorer_tab:
    st.subheader("Inspect a single skill")
    if not all_required:
        st.info("No skills were extracted into the explorer for this run yet.")
        selected_skill = None
    else:
        selected_skill = st.selectbox(
            "Choose a skill to inspect",
            all_required,
            index=all_required.index(missing_skills[0]) if missing_skills else 0,
        )
    if selected_skill:
        selected_is_missing = selected_skill in missing_skills
        selected_step = roadmap_by_skill.get(selected_skill, {})

        col1, col2 = st.columns([1, 1.05], gap="large")
        with col1:
            st.markdown(
                f"""
                <div class="section-card">
                    <h4 style="margin:0 0 10px 0;">Skill status</h4>
                    <p><strong>Skill:</strong> {selected_skill}</p>
                    <p><strong>Status:</strong> {"Missing evidence" if selected_is_missing else "Already detected"}</p>
                    <p><strong>Role context:</strong> {role}</p>
                    <p style="margin-bottom:0;"><strong>Why it matters:</strong> {"This is a visible improvement opportunity for the target role." if selected_is_missing else "This is already helping your profile align with the job."}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if selected_is_missing:
                st.info(
                    f"`{selected_skill}` is currently treated as a gap. Strengthening it and adding proof in your resume can improve the next analysis pass."
                )
            else:
                st.success(
                    f"`{selected_skill}` is already showing up in your current profile. Keep it visible with concrete project examples and impact statements."
                )

            if selected_step:
                st.markdown("### Roadmap alignment")
                st.markdown(f"**Priority:** {selected_step.get('priority', 'TBD')}")
                st.markdown(f"**Duration:** {selected_step.get('duration', 'TBD')}")
                st.markdown(f"**Primary resource:** {selected_step.get('resource', selected_step.get('course_name', 'Learning path'))}")
                st.markdown(f"**Provider:** {selected_step.get('provider', 'Curated Catalog')}")

        with col2:
            st.markdown("### Recommended learning stack")
            if selected_is_missing and selected_step:
                _render_learning_stack(selected_step)
            elif selected_is_missing:
                st.info("A learning stack has not been attached for this skill yet, but the roadmap page may still include broader next steps.")
            else:
                st.markdown(
                    "Keep this skill strong by refining project evidence, interview stories, and measurable impact statements around it."
                )

            st.markdown("### Guided next step")
            if selected_is_missing:
                st.markdown(
                    f"1. Learn the core concepts for `{selected_skill}`.\n"
                    f"2. Build one small practical example.\n"
                    f"3. Add that evidence back into your resume so the system can detect stronger proof next time."
                )
            else:
                st.markdown(
                    f"1. Keep `{selected_skill}` prominent in your resume bullets.\n"
                    f"2. Tie it to outcomes, scale, or tools used.\n"
                    f"3. Use it as a strength in interviews and project walkthroughs."
                )

with strategy_tab:
    board_left, board_right = st.columns(2, gap="large")
    with board_left:
        render_category_gap_bars(gap.get("category_scores", {}))
    with board_right:
        render_gap_priority_matrix(roadmap)

    st.subheader("Decision context")
    context1, context2 = st.columns(2, gap="large")
    with context1:
        st.markdown(
            f"""
            <div class="section-card">
                <h4 style="margin:0 0 8px 0;">Role interpretation</h4>
                <p><strong>Detected role:</strong> {role}</p>
                <p><strong>Resume parser:</strong> {summary.get('parsing_source', {}).get('resume', 'unknown')}</p>
                <p style="margin-bottom:0;"><strong>JD parser:</strong> {summary.get('parsing_source', {}).get('jd', 'unknown')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with context2:
        match_summary = summary.get("match_summary", {})
        st.markdown(
            f"""
            <div class="section-card">
                <h4 style="margin:0 0 8px 0;">Matching snapshot</h4>
                <p><strong>Overall fit:</strong> {match_summary.get('overall_fit', fit_label)}</p>
                <p><strong>Exact matches:</strong> {match_summary.get('exact_matches', len(matched_skills))}</p>
                <p style="margin-bottom:0;"><strong>Missing count:</strong> {match_summary.get('missing_count', len(missing_skills))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("View extracted resume details"):
        st.json(resume)
    with st.expander("View extracted job details"):
        st.json(jd)
    with st.expander("View raw match summary"):
        st.json(summary.get("match_summary", {}))

st.markdown("---")
go1, go2, go3 = st.columns(3, gap="large")
with go1:
    if st.button("Open Roadmap", use_container_width=True):
        st.switch_page("pages/roadmap.py")
with go2:
    if st.button("View Reasoning Trace", use_container_width=True):
        st.switch_page("pages/reasoning.py")
with go3:
    if st.button("Ask Assistant", use_container_width=True):
        st.switch_page("pages/assistant.py")

render_footer()

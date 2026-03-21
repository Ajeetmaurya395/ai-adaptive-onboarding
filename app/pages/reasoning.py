import sys
from pathlib import Path
from typing import Dict, List

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar
from backend.trace import explain_reasoning


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


@st.cache_data(show_spinner=False)
def _reasoning_text(resume_summary: str, jd_role: str, missing_skills: tuple[str, ...]) -> str:
    return explain_reasoning(
        resume_summary,
        jd_role,
        {"missing_skills": list(missing_skills)},
    )


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
        return "Your profile already lines up well with this role. The roadmap is mainly for polishing and confidence-building."
    if score >= 80:
        return "You are quite close. A small number of targeted improvements could make you a much stronger match."
    if score >= 60:
        return "You already have useful overlap. The main opportunity is to close a few specific gaps instead of starting from scratch."
    return "This role is still reachable, but it will help to build the missing foundations in a focused order."


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.9:
        return "High confidence"
    if confidence >= 0.75:
        return "Good confidence"
    if confidence >= 0.5:
        return "Moderate confidence"
    return "Low confidence"


def _roadmap_lookup(roadmap: List[Dict]) -> Dict[str, Dict]:
    return {step.get("skill", ""): step for step in roadmap if step.get("skill")}


def _simple_skill_guidance(skill: str, role: str, roadmap_step: Dict | None) -> List[str]:
    guidance = [
        f"`{skill}` appears in the target role but was not clearly found in your resume signals.",
        f"For a `{role}` role, this skill likely affects how confident the system is about day-to-day job readiness.",
    ]
    if roadmap_step:
        duration = roadmap_step.get("duration", "a short study block")
        resource = roadmap_step.get("resource") or roadmap_step.get("course_name") or "the recommended learning path"
        guidance.append(f"The roadmap suggests starting with `{resource}` and treating it as a `{duration}` focus area.")
    else:
        guidance.append("The next step is to study this skill and add practical evidence of it to your projects or resume.")
    return guidance


def _render_chip_group(title: str, skills: List[str], chip_class: str) -> None:
    chips = "".join([f'<span class="skill-chip {chip_class}">{skill}</span>' for skill in skills])
    if not chips:
        chips = f'<span class="skill-chip {chip_class}">None</span>'
    st.markdown(
        f"""
        <div class="section-card">
            <h4 style="margin:0 0 8px 0;">{title}</h4>
            <div class="skill-chip-wrap">{chips}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_learning_stack(resources: List[Dict]) -> None:
    if not resources:
        st.info("No linked learning resources were attached to this step yet.")
        return

    for item in resources:
        title = item.get("title", "Untitled resource")
        url = item.get("url", "")
        resource_type = item.get("type", "Resource")
        cost = item.get("cost", "")

        line = f"**{resource_type}**: [{title}]({url})" if url else f"**{resource_type}**: {title}"
        if cost:
            line = f"{line} `{cost}`"
        st.markdown(line)


init_session_state()

inject_css()
render_sidebar()

render_page_header(
    "Reasoning Guide",
    "See how the system interpreted your profile, why skills were flagged, and what to do next in simple terms.",
    eyebrow="Explainability",
)

if st.session_state.analysis_result is None:
    st.warning("No analysis data found. Please run an analysis from the Upload page first.")
    render_footer()
    st.stop()

data = st.session_state.analysis_result
summary = data.get("summary", {})
gap = data.get("gap", {})
resume = data.get("resume", {})
jd = data.get("jd", {})
roadmap = data.get("roadmap", [])
matched_skills = gap.get("matched_skills", [])
missing_skills = gap.get("missing_skills", [])
match_score = int(gap.get("match_score", summary.get("match_score", 0)) or 0)
role = summary.get("role_detected") or jd.get("role") or "Target Role"
confidence = float(summary.get("confidence", 0.0) or 0.0)
resume_summary = resume.get("summary", "")
roadmap_by_skill = _roadmap_lookup(roadmap)

overall_reasoning = _reasoning_text(resume_summary, role, tuple(missing_skills[:5]))
fit_label = _fit_label(match_score)

render_section_intro(
    "Guided Explanation",
    "Start with the simple summary, then explore individual skills and the decision process behind the score.",
    pills=["Plain English", "Skill Coach", "Transparent Logic"],
)

metric1, metric2, metric3, metric4 = st.columns(4, gap="large")
with metric1:
    st.metric("Match Score", f"{match_score}%")
with metric2:
    st.metric("Fit Level", fit_label)
with metric3:
    st.metric("Missing Skills", len(missing_skills))
with metric4:
    st.metric("Parsing Confidence", _confidence_label(confidence))

st.progress(max(0, min(match_score, 100)) / 100)
st.caption(_fit_guidance(match_score, len(missing_skills)))

overview_tab, coach_tab, process_tab = st.tabs(["Simple Summary", "Skill Coach", "How We Decided"])

with overview_tab:
    st.markdown(
        f"""
        <div class="section-card" style="border-left: 4px solid #0891b2;">
            <h4 style="margin-top:0;">What this means</h4>
            <p style="margin-bottom:0;">{overall_reasoning}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    quick1, quick2 = st.columns(2, gap="large")
    with quick1:
        _render_chip_group("Skills already showing up well", matched_skills, "match")
    with quick2:
        _render_chip_group("Skills that need more evidence", missing_skills, "miss")

    st.subheader("Next best move")
    if missing_skills:
        top_skill = missing_skills[0]
        top_step = roadmap_by_skill.get(top_skill, {})
        st.info(
            f"Start with `{top_skill}` first. It is currently the highest-priority gap, and the roadmap already has a focused learning path ready for it."
        )
        if top_step:
            st.markdown(
                f"Recommended starting point: **{top_step.get('resource', top_step.get('course_name', 'Learning path'))}**"
            )
    else:
        st.success("No critical gaps were found. Your next step is to refine projects, interview stories, and proof of depth.")

with coach_tab:
    if not missing_skills:
        st.success("There are no missing skills to coach through right now.")
    else:
        selected_skill = st.selectbox(
            "Choose a missing skill to understand it better",
            missing_skills,
            index=0,
        )
        selected_step = roadmap_by_skill.get(selected_skill, {})
        skill_reasoning = _reasoning_text(resume_summary, role, (selected_skill,))

        coach1, coach2 = st.columns([1.2, 1], gap="large")
        with coach1:
            st.markdown(
                f"""
                <div class="section-card">
                    <h4 style="margin-top:0;">Why this skill was flagged</h4>
                    <p>{skill_reasoning}</p>
                    <h4>In simple terms</h4>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for line in _simple_skill_guidance(selected_skill, role, selected_step):
                st.markdown(f"- {line}")

            st.markdown("### Guided action plan")
            st.markdown(f"1. Learn the basics of `{selected_skill}` from documentation or a beginner-friendly explainer.")
            st.markdown(f"2. Use the roadmap resource for `{selected_skill}` and build one small hands-on example.")
            st.markdown(f"3. Add that example back into your resume so the next analysis can detect real evidence.")

        with coach2:
            st.markdown("### Recommended learning stack")
            _render_learning_stack(selected_step.get("learning_resources", []))

            if selected_step:
                st.markdown("### Roadmap fit")
                st.markdown(f"**Priority:** {selected_step.get('priority', 'TBD')}")
                st.markdown(f"**Estimated time:** {selected_step.get('duration', 'TBD')}")
                st.markdown(f"**Primary resource:** {selected_step.get('resource', selected_step.get('course_name', 'Learning path'))}")

with process_tab:
    st.subheader("How the system reached this result")
    step1, step2, step3, step4 = st.columns(4, gap="medium")
    with step1:
        st.markdown("**1. Read inputs**")
        st.caption("The system reads your resume and the job description and extracts key skill signals.")
    with step2:
        st.markdown("**2. Normalize skills**")
        st.caption("Different terms are mapped into cleaner skill names so similar concepts can be compared fairly.")
    with step3:
        st.markdown("**3. Compare fit**")
        st.caption("Your extracted skills are matched against the role requirements to estimate overlap and missing areas.")
    with step4:
        st.markdown("**4. Build a plan**")
        st.caption("Missing skills are turned into roadmap steps with learning resources so the result is actionable.")

    details1, details2 = st.columns(2, gap="large")
    with details1:
        st.markdown("### Resume understanding")
        st.markdown(f"**Detected summary:** {resume_summary or 'No short summary was extracted.'}")
        st.markdown(f"**Resume parser source:** `{summary.get('parsing_source', {}).get('resume', 'unknown')}`")
        with st.expander("View extracted resume details"):
            st.json(resume)

    with details2:
        st.markdown("### Job understanding")
        st.markdown(f"**Detected role:** {role}")
        st.markdown(f"**JD parser source:** `{summary.get('parsing_source', {}).get('jd', 'unknown')}`")
        with st.expander("View extracted job details"):
            st.json(jd)

    st.markdown("### Match logic snapshot")
    match_summary = summary.get("match_summary", {})
    snapshot1, snapshot2, snapshot3 = st.columns(3, gap="large")
    with snapshot1:
        st.metric("Overall Fit", match_summary.get("overall_fit", fit_label))
    with snapshot2:
        st.metric("Exact Matches", match_summary.get("exact_matches", len(matched_skills)))
    with snapshot3:
        st.metric("Missing Count", match_summary.get("missing_count", len(missing_skills)))

    with st.expander("View raw match summary"):
        st.json(match_summary)

st.markdown("---")
go1, go2 = st.columns(2, gap="large")
with go1:
    if st.button("Open Roadmap", use_container_width=True):
        st.switch_page("pages/roadmap.py")
with go2:
    if st.button("Back To Analysis", use_container_width=True):
        st.switch_page("pages/analysis.py")

render_footer()

import sys
from pathlib import Path
from typing import Dict, List

import streamlit as st
from PyPDF2 import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.components.alerts import show_success, show_error
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.loaders import loading_spinner
from app.components.navbar import render_sidebar
from app.database import save_result, save_roadmap
from backend.gap_engine import calculate_gap
from backend.parser import parse_resume, parse_jd
from backend.roadmap_builder import generate_roadmap

inject_css()
render_sidebar()


def read_pdf(file) -> str:
    """Extract text from PDF file."""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        return text.strip()
    except Exception as exc:
        return f"Error reading PDF: {exc}"


def load_sample_resume() -> str:
    return """Senior Software Engineer with 5+ years of experience building scalable web applications.
Proficient in Python, Django, PostgreSQL, AWS (EC2, S3, Lambda), Docker, and Kubernetes.
Strong background in CI/CD pipelines, microservices architecture, and agile delivery.
Led a team of 4 developers to deliver cloud migration projects ahead of schedule."""


def load_sample_jd() -> str:
    return """Senior Cloud Engineer - TechCorp
We are seeking an experienced engineer to lead cloud infrastructure initiatives.

Required Skills:
- Advanced Python programming
- AWS services (EC2, S3, Lambda, RDS, CloudFormation)
- Containerization: Docker, Kubernetes
- Infrastructure as Code: Terraform or CloudFormation
- CI/CD: GitHub Actions, Jenkins
- Monitoring: CloudWatch, Prometheus

Preferred:
- Experience with microservices architecture
- Knowledge of security best practices
- Leadership and mentoring experience
"""


def sample_analysis_result() -> Dict:
    gap = {
        "match_score": 74,
        "matched_skills": ["Python", "AWS", "Docker", "Microservices"],
        "missing_skills": ["Kubernetes", "CloudFormation", "Prometheus", "Leadership"],
        "extra_skills": ["Django", "PostgreSQL"],
        "total_required": 8,
    }
    roadmap: List[Dict] = [
        {
            "skill": "Kubernetes",
            "resource": "Kubernetes Fundamentals Lab",
            "duration": "4 weeks",
            "priority": "High",
        },
        {
            "skill": "CloudFormation",
            "resource": "AWS CloudFormation in Practice",
            "duration": "3 weeks",
            "priority": "High",
        },
        {
            "skill": "Prometheus Monitoring",
            "resource": "Observability and Prometheus Playbook",
            "duration": "2 weeks",
            "priority": "Medium",
        },
        {
            "skill": "Leadership",
            "resource": "Technical Leadership Foundations",
            "duration": "2 weeks",
            "priority": "Low",
        },
    ]
    return {
        "resume": {"skills": gap["matched_skills"], "experience_years": 5, "summary": "Backend + cloud engineer"},
        "jd": {"skills": gap["matched_skills"] + gap["missing_skills"], "role": "Senior Cloud Engineer"},
        "gap": gap,
        "roadmap": roadmap,
        "resume_text": load_sample_resume()[:500] + "...",
    }


render_page_header(
    "Upload and Analyze",
    "Drop resume + JD, run gap analysis, and generate a roadmap in one flow.",
    eyebrow="Workspace",
)

render_section_intro(
    "Quick Start",
    "Use sample buttons for instant demo, or upload your own files for a real run.",
    pills=["Step 1: Provide Inputs", "Step 2: Run Analysis", "Step 3: Explore Insights"],
)

quick1, quick2, quick3 = st.columns(3, gap="large")
with quick1:
    if st.button("Load Sample Resume", use_container_width=True):
        st.session_state.resume_text = load_sample_resume()
        show_success("Sample resume loaded.")
with quick2:
    if st.button("Load Sample JD", use_container_width=True):
        st.session_state.jd_text = load_sample_jd()
        show_success("Sample JD loaded.")
with quick3:
    if st.button("Load Full Sample Analysis", use_container_width=True):
        sample = sample_analysis_result()
        st.session_state.resume_text = load_sample_resume()
        st.session_state.jd_text = load_sample_jd()
        st.session_state.analysis_result = sample
        show_success("Sample analysis loaded. Open Analysis and Roadmap pages.")

st.write("")
render_section_intro(
    "Document Inputs",
    "Upload a resume and job description. We support PDF/TXT resume and TXT JD.",
    pills=["Resume (PDF/TXT)", "JD (TXT)", "Minimum 50 characters"],
)
col1, col2 = st.columns(2, gap="large")
with col1:
    st.markdown('<div class="upload-panel">', unsafe_allow_html=True)
    st.subheader("Resume")
    st.caption("Upload Resume (PDF/TXT)")
    resume_file = st.file_uploader(
        "Upload Resume (PDF/TXT)",
        type=["pdf", "txt"],
        key="resume_uploader",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)
with col2:
    st.markdown('<div class="upload-panel">', unsafe_allow_html=True)
    st.subheader("Job Description")
    st.caption("Upload JD (TXT)")
    jd_file = st.file_uploader(
        "Upload JD (TXT)",
        type=["txt"],
        key="jd_uploader",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
if st.button("Analyze Skill Gap", type="primary", use_container_width=True):
    resume_text = st.session_state.get("resume_text") or ""
    jd_text = st.session_state.get("jd_text") or ""

    if not resume_text and resume_file:
        if resume_file.type == "application/pdf":
            resume_text = read_pdf(resume_file)
        else:
            resume_text = resume_file.read().decode("utf-8")
        st.session_state.resume_text = resume_text

    if not jd_text and jd_file:
        jd_text = jd_file.read().decode("utf-8")
        st.session_state.jd_text = jd_text

    if not resume_text or len(resume_text) < 50:
        show_error("Please provide a valid resume (minimum 50 characters).")
        st.stop()

    if not jd_text or len(jd_text) < 50:
        show_error("Please provide a valid job description (minimum 50 characters).")
        st.stop()

    with loading_spinner("AI is analyzing your documents..."):
        try:
            resume_data = parse_resume(resume_text)
            jd_data = parse_jd(jd_text)

            if not resume_data.get("skills"):
                show_error("Could not extract skills from resume. Please try another file.")
                st.stop()

            gap_result = calculate_gap(
                resume_data.get("skills", []),
                jd_data.get("skills", []),
            )

            roadmap = generate_roadmap(
                gap_result["missing_skills"],
                jd_data.get("role", "Target Role"),
            )

            user_id = st.session_state.get("user_id")
            if user_id:
                save_result(user_id, gap_result["match_score"])
                if roadmap:
                    save_roadmap(user_id, roadmap)

            st.session_state.analysis_result = {
                "resume": resume_data,
                "jd": jd_data,
                "gap": gap_result,
                "roadmap": roadmap,
                "resume_text": resume_text[:500] + "...",
            }

            show_success("Analysis complete. Navigate to Analysis and Roadmap.")

            with st.expander("Quick Results Preview", expanded=True):
                c1, c2, c3 = st.columns(3, gap="medium")
                c1.metric("Match Score", f"{gap_result['match_score']}%")
                c2.metric("Skills Matched", len(gap_result["matched_skills"]))
                c3.metric("Skills to Learn", len(gap_result["missing_skills"]))

            st.markdown("---")
            nav1, nav2 = st.columns(2, gap="large")
            with nav1:
                if st.button("Open Analysis Page", use_container_width=True):
                    st.switch_page("pages/analysis.py")
            with nav2:
                if st.button("Open Roadmap Page", use_container_width=True):
                    st.switch_page("pages/roadmap.py")

        except Exception as exc:
            show_error(f"Analysis failed: {exc}")
            st.exception(exc)

render_footer()

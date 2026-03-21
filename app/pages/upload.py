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
from app.components.navbar import render_sidebar
from backend.gap_engine import GapEngine
from app.database_sqlite import save_analysis_history

inject_css()
render_sidebar()

SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
SAMPLE_LIBRARY = {
    "cloud_engineer": {
        "label": "Cloud Engineer",
        "domain": "Technical",
        "resume_path": SAMPLES_DIR / "resumes" / "resume1.txt",
        "jd_path": SAMPLES_DIR / "jds" / "jd1.txt",
        "description": "Cloud-native engineering flow with AWS, CI/CD, Docker, Kubernetes, and infrastructure gaps.",
    },
    "data_analyst": {
        "label": "Data Analyst",
        "domain": "Desk / Analytics",
        "resume_path": SAMPLES_DIR / "resumes" / "resume2.txt",
        "jd_path": SAMPLES_DIR / "jds" / "jd2.txt",
        "description": "Analytics path with SQL, Excel, Tableau, Power BI, Python, and stakeholder communication.",
    },
    "operations_manager": {
        "label": "Operations Manager",
        "domain": "Operational / Business",
        "resume_path": SAMPLES_DIR / "resumes" / "resume3.txt",
        "jd_path": SAMPLES_DIR / "jds" / "jd3.txt",
        "description": "Operational leadership scenario with supply chain, project management, negotiation, and process improvement.",
    },
}


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


def init_input_state() -> None:
    st.session_state.setdefault("resume_text", "")
    st.session_state.setdefault("jd_text", "")
    st.session_state.setdefault("resume_source_hint", "")
    st.session_state.setdefault("jd_source_hint", "")
    st.session_state.setdefault("input_status_message", "")
    st.session_state.setdefault("run_sample_analysis", False)
    st.session_state.setdefault("last_uploaded_resume_text", "")
    st.session_state.setdefault("last_uploaded_jd_text", "")
    st.session_state.setdefault("selected_sample_key", "cloud_engineer")


def read_text_file(path: Path, fallback: str = "") -> str:
    try:
        text = path.read_text(encoding="utf-8").strip()
        return text or fallback
    except Exception:
        return fallback


def summarize_input_source(text_value: str, uploaded_file, source_hint: str = "") -> Dict[str, str]:
    cleaned = (text_value or "").strip()
    if cleaned and source_hint:
        return {"source": source_hint, "detail": f"{len(cleaned)} characters"}
    if cleaned:
        return {"source": "Pasted Text", "detail": f"{len(cleaned)} characters"}
    if uploaded_file is not None:
        return {"source": "Uploaded File", "detail": uploaded_file.name}
    return {"source": "Missing", "detail": "Add text or upload a file"}


def render_document_panel(
    title: str,
    text_key: str,
    uploader_key: str,
    uploader_label: str,
    file_types: List[str],
    placeholder: str,
    helper_text: str,
):
    st.markdown(
        f"""
        <div class="input-panel">
            <div class="input-panel__title">{title}</div>
            <div class="input-panel__copy">{helper_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    paste_tab, upload_tab = st.tabs(["Paste Text", "Upload File"])

    with paste_tab:
        st.text_area(
            f"{title} Text",
            key=text_key,
            height=260,
            placeholder=placeholder,
            label_visibility="collapsed",
        )
        current_text = (st.session_state.get(text_key) or "").strip()
        st.caption(
            f"{len(current_text)} characters ready. Pasted text takes priority over uploaded files."
            if current_text
            else "Paste raw text here if you don’t want to upload a file."
        )
        if current_text:
            with st.expander("Preview Text", expanded=False):
                st.write(current_text[:1500] + ("..." if len(current_text) > 1500 else ""))

    with upload_tab:
        uploaded_file = st.file_uploader(
            uploader_label,
            type=file_types,
            key=uploader_key,
            label_visibility="collapsed",
        )
        st.caption("PDF/TXT is best for resumes. TXT is best for job descriptions.")
        return uploaded_file


def _selected_sample() -> Dict:
    return SAMPLE_LIBRARY.get(st.session_state.get("selected_sample_key", "cloud_engineer"), SAMPLE_LIBRARY["cloud_engineer"])


def load_sample_resume() -> str:
    sample = _selected_sample()
    return read_text_file(
        sample["resume_path"],
        """Senior Software Engineer with 5+ years of experience building scalable web applications.
Proficient in Python, Django, PostgreSQL, AWS (EC2, S3, Lambda), Docker, and Kubernetes.
Strong background in CI/CD pipelines, microservices architecture, and agile delivery.
Led a team of 4 developers to deliver cloud migration projects ahead of schedule.""",
    )


def load_sample_jd() -> str:
    sample = _selected_sample()
    return read_text_file(
        sample["jd_path"],
        """Senior Cloud Engineer - TechCorp
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
""",
    )


def sample_analysis_result() -> Dict:
    return {
        "resume_text": load_sample_resume(),
        "jd_text": load_sample_jd(),
    }


init_input_state()


def set_status_message(message: str) -> None:
    st.session_state.input_status_message = message


def load_sample_resume_into_state() -> None:
    sample = _selected_sample()
    st.session_state.resume_text = load_sample_resume()
    st.session_state.resume_source_hint = f"Sample Dataset ({sample['resume_path'].name})"
    set_status_message(f"Loaded sample resume for {sample['label']} from {sample['resume_path']}.")


def load_sample_jd_into_state() -> None:
    sample = _selected_sample()
    st.session_state.jd_text = load_sample_jd()
    st.session_state.jd_source_hint = f"Sample Dataset ({sample['jd_path'].name})"
    set_status_message(f"Loaded sample job description for {sample['label']} from {sample['jd_path']}.")

render_page_header(
    "Upload and Analyze",
    "Drop resume + JD, run gap analysis, and generate a roadmap in one flow.",
    eyebrow="Workspace",
)

render_section_intro(
    "Quick Start",
    "Use sample buttons for instant demo, or upload your own files for a real run.",
    pills=["Step 1: Provide Inputs", "Step 2: Run Analysis", "Step 3: Explore Insights", "Cross-Domain Samples"],
)

sample_key = st.selectbox(
    "Demo scenario",
    options=list(SAMPLE_LIBRARY.keys()),
    format_func=lambda key: f"{SAMPLE_LIBRARY[key]['label']} · {SAMPLE_LIBRARY[key]['domain']}",
    key="selected_sample_key",
)
sample_meta = SAMPLE_LIBRARY[sample_key]
st.caption(sample_meta["description"])

quick1, quick2, quick3 = st.columns(3, gap="large")
with quick1:
    if st.button("Load Sample Resume", use_container_width=True):
        load_sample_resume_into_state()
with quick2:
    if st.button("Load Sample JD", use_container_width=True):
        load_sample_jd_into_state()
with quick3:
    if st.button("Load Full Sample Analysis", use_container_width=True):
        sample = sample_analysis_result()
        st.session_state.resume_text = sample["resume_text"]
        st.session_state.jd_text = sample["jd_text"]
        st.session_state.resume_source_hint = f"Sample Dataset ({sample_meta['resume_path'].name})"
        st.session_state.jd_source_hint = f"Sample Dataset ({sample_meta['jd_path'].name})"
        set_status_message(f"Loaded {sample_meta['label']} sample inputs. Running sample analysis now...")
        st.session_state.run_sample_analysis = True

if st.session_state.get("input_status_message"):
    show_success(st.session_state.input_status_message)
    st.session_state.input_status_message = ""

st.write("")
render_section_intro(
    "Document Inputs",
    "Paste text directly or upload files. The analyzer will use pasted text first and fall back to uploaded files when needed.",
    pills=["Paste or Upload", "Resume (PDF/TXT)", "JD (TXT)", "Minimum 50 characters"],
)
col1, col2 = st.columns(2, gap="large")
with col1:
    resume_file = render_document_panel(
        "Resume",
        "resume_text",
        "resume_uploader",
        "Upload Resume (PDF/TXT)",
        ["pdf", "txt"],
        """Paste the full resume text here.

Include summary, experience, tools, cloud platforms, frameworks, projects, and leadership signals if available.""",
        "Choose the faster path: paste plain text for quick iteration or upload the source file for a more realistic run.",
    )
with col2:
    jd_file = render_document_panel(
        "Job Description",
        "jd_text",
        "jd_uploader",
        "Upload JD (TXT)",
        ["txt"],
        """Paste the full job description here.

Include required skills, preferred skills, title, seniority, tooling, cloud stack, and expectations.""",
        "Use the full hiring brief when possible so the gap engine has enough context to prioritize the roadmap well.",
    )

if st.session_state.get("resume_source_hint") and st.session_state.get("resume_text", "").strip() != load_sample_resume().strip():
    st.session_state.resume_source_hint = ""
if st.session_state.get("jd_source_hint") and st.session_state.get("jd_text", "").strip() != load_sample_jd().strip():
    st.session_state.jd_source_hint = ""

resume_summary = summarize_input_source(
    st.session_state.get("resume_text", ""),
    resume_file,
    st.session_state.get("resume_source_hint", ""),
)
jd_summary = summarize_input_source(
    st.session_state.get("jd_text", ""),
    jd_file,
    st.session_state.get("jd_source_hint", ""),
)

st.markdown(
    """
    <div class="readiness-strip">
        <div class="readiness-item">
            <div class="readiness-item__label">Resume Source</div>
            <div class="readiness-item__value">{resume_source}</div>
            <div class="readiness-item__meta">{resume_detail}</div>
        </div>
        <div class="readiness-item">
            <div class="readiness-item__label">JD Source</div>
            <div class="readiness-item__value">{jd_source}</div>
            <div class="readiness-item__meta">{jd_detail}</div>
        </div>
        <div class="readiness-item">
            <div class="readiness-item__label">Analysis Mode</div>
            <div class="readiness-item__value">Grounded Flow</div>
            <div class="readiness-item__meta">O*NET normalization + course roadmap orchestration</div>
        </div>
    </div>
    """.format(
        resume_source=resume_summary["source"],
        resume_detail=resume_summary["detail"],
        jd_source=jd_summary["source"],
        jd_detail=jd_summary["detail"],
    ),
    unsafe_allow_html=True,
)

# Initialize the bridge engine
engine = GapEngine()

def run_analysis_flow(resume_text: str, jd_text: str, switch_page: bool = True):
    """The functional bridge connecting backend to UI."""
    with st.spinner("🚀 Running real O*NET + ChromaDB-backed analysis..."):
        try:
            # 1. Run the real logic
            analysis = engine.process(resume_text, jd_text)
            
            # 2. Map to the Unified Schema (Section 1 + Section 3 requirements)
            st.session_state.analysis_result = {
                "summary": analysis["summary"],
                "skills": analysis["skills"],
                "gap": {
                    "matched_skills": analysis["skills"]["matched"],
                    "missing_skills": analysis["skills"]["missing"],
                    "match_score": analysis["summary"]["match_score"],
                    "category_scores": analysis.get("gap", {}).get(
                        "category_scores",
                        {"Technology": 85, "Core Skills": 75, "Knowledge": 70},
                    ),
                },
                "roadmap": analysis["roadmap"],
                "raw_text": analysis["raw_text"],
                "resume": analysis.get("resume", {}),
                "jd": analysis.get("jd", {}),
                "db_available": True
            }
            
            # 3. Persist to SQLite History
            user_id = st.session_state.get("user_id", "anonymous")
            save_analysis_history(
                user_id,
                analysis["summary"]["match_score"],
                analysis["skills"]["matched"],
                analysis["skills"]["missing"],
                analysis["roadmap"]
            )
            
            show_success("Real-time analysis complete using the grounded sample-aware roadmap flow.")
            
            if switch_page:
                st.switch_page("pages/analysis.py")
            
        except Exception as exc:
            show_error(f"Analysis failed: {exc}")
            st.exception(exc)


if st.session_state.get("run_sample_analysis"):
    st.session_state.run_sample_analysis = False
    run_analysis_flow(
        st.session_state.get("resume_text", ""),
        st.session_state.get("jd_text", ""),
        switch_page=False,
    )

st.write("")
if st.button("Analyze Skill Gap", type="primary", use_container_width=True):
    resume_text = (st.session_state.get("resume_text") or "").strip()
    jd_text = (st.session_state.get("jd_text") or "").strip()

    if not resume_text and resume_file:
        if resume_file.type == "application/pdf":
            resume_text = read_pdf(resume_file)
        else:
            resume_text = resume_file.read().decode("utf-8")
        st.session_state.last_uploaded_resume_text = resume_text
        st.session_state.resume_source_hint = f"Uploaded File ({resume_file.name})"

    if not jd_text and jd_file:
        jd_text = jd_file.read().decode("utf-8")
        st.session_state.last_uploaded_jd_text = jd_text
        st.session_state.jd_source_hint = f"Uploaded File ({jd_file.name})"

    if not resume_text or len(resume_text) < 50:
        show_error("Please provide a valid resume (minimum 50 characters).")
        st.stop()

    if not jd_text or len(jd_text) < 50:
        show_error("Please provide a valid job description (minimum 50 characters).")
        st.stop()

    run_analysis_flow(resume_text, jd_text)

analysis_result = st.session_state.get("analysis_result")
if analysis_result:
    gap_preview = analysis_result.get("gap", {})
    with st.expander("Latest Analysis Preview", expanded=True):
        metric1, metric2, metric3 = st.columns(3, gap="medium")
        metric1.metric("Match Score", f"{gap_preview.get('match_score', 0)}%")
        metric2.metric("Matched Skills", len(gap_preview.get("matched_skills", [])))
        metric3.metric("Roadmap Steps", len(analysis_result.get("roadmap", [])))

        nav1, nav2 = st.columns(2, gap="large")
        with nav1:
            if st.button("Open Analysis Page", use_container_width=True):
                st.switch_page("pages/analysis.py")
        with nav2:
            if st.button("Open Roadmap Page", use_container_width=True):
                st.switch_page("pages/roadmap.py")

render_footer()

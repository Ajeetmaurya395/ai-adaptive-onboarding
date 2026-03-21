import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.components.charts import render_metrics_comparison
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar
from backend.parser import parse_jd, parse_resume
from evaluation.metrics import compute_metrics

inject_css()
render_sidebar()

render_page_header(
    "System Evaluation",
    "Compare extracted outputs with sample ground truth.",
    eyebrow="Quality Check",
)

st.markdown("Run a quick benchmark using sample resume extraction output.")
render_section_intro(
    "Evaluation Setup",
    "Compares extracted skill signals with expected outputs from sample data.",
    pills=["Accuracy", "Precision", "Recall", "F1 Score", "Grounded Validation"],
)

st.markdown(
    """
    <div class="section-card">
        <h4 style="margin:0 0 8px 0;">Benchmark Inputs</h4>
        <p style="margin:0 0 6px 0;"><strong>Sample Pair:</strong> `resume1.txt` + `jd1.txt` from the local sample dataset</p>
        <p style="margin:0 0 6px 0;"><strong>Ground Truth:</strong> `data/samples/expected_outputs.json`</p>
        <p style="margin:0;"><strong>Metrics:</strong> Accuracy, match score, precision, recall, and F1 from the evaluation utility.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("Run Evaluation", use_container_width=True):
    with open("data/samples/expected_outputs.json", "r", encoding="utf-8") as file:
        expected = json.load(file)

    resume_sample_path = PROJECT_ROOT / "data" / "samples" / "resumes" / "resume1.txt"
    jd_sample_path = PROJECT_ROOT / "data" / "samples" / "jds" / "jd1.txt"
    resume_text = resume_sample_path.read_text(encoding="utf-8").strip() if resume_sample_path.exists() else ""
    jd_text = jd_sample_path.read_text(encoding="utf-8").strip() if jd_sample_path.exists() else ""

    with st.spinner("🔍 Running live dataset-backed evaluation..."):
        resume_extract = parse_resume(resume_text)
        jd_extract = parse_jd(jd_text)

    resume_metrics = compute_metrics(resume_extract, expected.get("resume1", {}))
    jd_metrics = compute_metrics(jd_extract, expected.get("jd1", {}))
    metrics = {
        key: round((resume_metrics.get(key, 0) + jd_metrics.get(key, 0)) / 2, 2)
        for key in ["accuracy", "match_score", "precision", "recall", "f1_score"]
    }
    metrics["skills_found"] = resume_metrics.get("skills_found", 0) + jd_metrics.get("skills_found", 0)
    metrics["skills_expected"] = resume_metrics.get("skills_expected", 0) + jd_metrics.get("skills_expected", 0)
    metrics["skills_extracted"] = resume_metrics.get("skills_extracted", 0) + jd_metrics.get("skills_extracted", 0)

    c1, c2 = st.columns(2, gap="large")
    c1.metric("Extraction Accuracy", f"{metrics['accuracy']}%")
    c2.metric("Skill Match", f"{metrics['match_score']}%")

    c3, c4 = st.columns(2, gap="large")
    c3.metric("Precision", f"{metrics['precision']}%")
    c4.metric("Recall", f"{metrics['recall']}%")

    render_metrics_comparison(metrics)

    st.subheader("Detailed Metrics")
    st.json(metrics)

    ref1, ref2 = st.columns(2, gap="large")
    with ref1:
        st.markdown(
            """
            ### Dataset Disclosure
            - O*NET grounded normalization powers canonical skill mapping.
            - Local sample resume and JD files are used for repeatable evaluation.
            - Expected outputs are stored in the repository for transparent benchmarking.
            """
        )
    with ref2:
        st.markdown(
            """
            ### Reliability Notes
            - Parsing is grounded against local skill vocabularies before comparison.
            - Sample evaluation helps expose extraction regressions early.
            - The roadmap engine uses catalog-grounded primary course recommendations.
            """
        )

    with st.expander("Per-Dataset Breakdown", expanded=False):
        st.write("Resume Sample")
        st.json({"extract": resume_extract, "metrics": resume_metrics})
        st.write("JD Sample")
        st.json({"extract": jd_extract, "metrics": jd_metrics})

render_footer()

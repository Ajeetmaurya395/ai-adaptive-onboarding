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
    pills=["Accuracy", "Precision", "Recall", "F1 Score"],
)

if st.button("Run Evaluation", use_container_width=True):
    with open("data/samples/expected_outputs.json", "r", encoding="utf-8") as file:
        expected = json.load(file)

    current_extract = {
        "skills": ["Python", "SQL", "Communication"],
        "experience_years": 3,
    }
    metrics = compute_metrics(current_extract, expected["resume1"])

    c1, c2 = st.columns(2, gap="large")
    c1.metric("Extraction Accuracy", f"{metrics['accuracy']}%")
    c2.metric("Skill Match", f"{metrics['match_score']}%")

    c3, c4 = st.columns(2, gap="large")
    c3.metric("Precision", f"{metrics['precision']}%")
    c4.metric("Recall", f"{metrics['recall']}%")

    render_metrics_comparison(metrics)

    st.subheader("Detailed Metrics")
    st.json(metrics)

render_footer()

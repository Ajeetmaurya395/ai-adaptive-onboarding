import streamlit as st
import json
import os
from evaluation.metrics import compute_metrics

st.title("🔍 System Evaluation")

st.markdown("Compare extracted skills against ground truth for sample data.")

if st.button("Run Evaluation"):
    # Load expected
    with open("data/samples/expected_outputs.json", "r") as f:
        expected = json.load(f)
    
    # Mock current extraction for demo (In real app, run parser on sample files)
    # Here we simulate the parser output based on the prompt logic
    current_extract = {
        "skills": ["Python", "SQL", "Communication"], 
        "experience_years": 3
    }
    
    metrics = compute_metrics(current_extract, expected["resume1"])
    
    st.metric("Extraction Accuracy", f"{metrics['accuracy']}%")
    st.metric("Skill Match", f"{metrics['match_score']}%")
    
    st.write("### Detailed Metrics")
    st.json(metrics)
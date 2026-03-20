import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.components.charts import render_history_trend
from app.components.layout import render_page_header, render_footer, render_section_intro
from app.components.navbar import render_sidebar
from app.database import get_history

inject_css()
render_sidebar()

render_page_header(
    "Analysis History",
    "Track previous runs, scores, and recent progress trends.",
    eyebrow="History",
)

if not st.session_state.get("user_id"):
    st.warning("Please login to view history.")
    render_footer()
    st.stop()

history = get_history(st.session_state.user_id)

if history:
    render_section_intro(
        "History Overview",
        "Track consistency and progress across your recent analyses.",
        pills=["Trend", "Performance", "Gap Progress"],
    )

    rows = []
    scores = []
    labels = []
    for item in history:
        created = item.get("created_at")
        gap = item.get("gap_summary", {})
        score = item.get("score", 0)
        scores.append(score)
        labels.append(created.strftime("%b %d") if created else "n/a")
        rows.append(
            {
                "Score": score,
                "Date": created.strftime("%Y-%m-%d %H:%M") if created else "n/a",
                "Matched Skills": gap.get("matched", 0),
                "Missing Skills": gap.get("missing", 0),
            }
        )

    top1, top2, top3 = st.columns(3, gap="large")
    top1.metric("Total Analyses", len(rows))
    top2.metric("Average Score", f"{sum(scores)/len(scores):.1f}%")
    top3.metric("Best Score", f"{max(scores):.1f}%")

    render_history_trend(list(reversed(scores)), list(reversed(labels)))
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No previous analyses found.")

render_footer()

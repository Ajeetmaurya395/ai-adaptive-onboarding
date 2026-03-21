import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.theme import inject_css
from app.components.layout import render_footer, render_page_header, render_section_intro
from app.components.navbar import render_sidebar


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _download_asset(label: str, path: Path, mime: str = "text/markdown") -> None:
    if not path.exists():
        st.warning(f"Missing asset: {path.name}")
        return
    st.download_button(label, data=path.read_text(encoding="utf-8"), file_name=path.name, mime=mime, use_container_width=True)


inject_css()
render_sidebar()

render_page_header(
    "Hackathon Readiness",
    "A judge-facing overview of how the product maps to the challenge, the evaluation criteria, and the required submission assets.",
    eyebrow="Hackathon",
)

render_section_intro(
    "Challenge Fit",
    "The product parses new-hire capability, identifies role-specific gaps, and generates adaptive learning pathways rather than one-size-fits-all onboarding.",
    pills=["Intelligent Parsing", "Dynamic Mapping", "Reasoning Trace", "Grounded Roadmaps", "Cross-Domain Samples"],
)

check1, check2, check3 = st.columns(3, gap="large")
with check1:
    st.success("Eligible Feature: Intelligent parsing of resume + JD with skill extraction, role detection, and confidence scoring.")
with check2:
    st.success("Eligible Feature: Dynamic adaptive pathing that turns missing skills into prioritized roadmap steps.")
with check3:
    st.success("Eligible Feature: Functional Streamlit UI for upload, analysis, roadmap, reasoning, evaluation, and Qwen assistant.")

overview_tab, architecture_tab, metrics_tab, assets_tab = st.tabs(
    ["Solution Overview", "Architecture & Workflow", "Datasets & Metrics", "Submission Assets"]
)

with overview_tab:
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            """
            ### Value Proposition
            This system reduces redundant onboarding by skipping what the candidate already knows and focusing only on what they still need for target-role competency.

            ### Product Impact
            - avoids static learning paths
            - prioritizes missing skills instead of relearning matched ones
            - explains every recommendation in simple terms
            - supports multiple job domains through shared grounded skill normalization
            """
        )
    with right:
        st.markdown(
            """
            ### In-App Experience
            - `Upload`: paste or upload Resume/JD
            - `Analysis`: interactive skill-gap visuals
            - `Roadmap`: prioritized training steps with docs, videos, books, and practice
            - `Reasoning`: explanation of why the gaps matter
            - `Assistant`: direct Qwen chat for follow-up queries
            - `Evaluation`: benchmark page for extraction quality
            """
        )

    st.markdown(
        """
        ### Cross-Domain Demo Coverage
        - `Cloud Engineer`: technical onboarding with cloud, DevOps, and infrastructure skills
        - `Data Analyst`: desk-role onboarding with analytics, BI, and stakeholder communication
        - `Operations Manager`: operational/business onboarding with supply chain, leadership, and execution skills
        """
    )

with architecture_tab:
    st.markdown("### System Workflow")
    st.code(
        """Resume/JD Input
    -> LLM + dataset-grounded parsing
    -> O*NET / taxonomy normalization
    -> skill matching and gap scoring
    -> adaptive roadmap graph
    -> reasoning trace + assistant Q&A
    -> evaluation + history""",
        language="text",
    )

    a1, a2 = st.columns(2, gap="large")
    with a1:
        st.markdown(
            """
            ### Tech Stack & Models
            - Frontend: Streamlit
            - Visualization: Plotly
            - LLM: `Qwen/Qwen2.5-7B-Instruct` via Hugging Face router
            - Embeddings / retrieval: ChromaDB + sentence-transformers local embedding workflow
            - Data layer: JSON datasets, O*NET-derived skill maps, optional MongoDB, local SQLite history
            - Orchestration: custom adaptive pathing graph in `backend/roadmap_graph.py`
            """
        )
    with a2:
        st.markdown(
            """
            ### Original Adaptive Logic
            - parse resume and JD separately
            - normalize skills against local grounded vocabularies
            - compare candidate vs required skills
            - preserve missing-skill order for priority
            - generate roadmap steps with catalog-grounded primary learning items
            - enrich each step with docs, free video, books, and practice links
            """
        )

    st.markdown("### UI / UX Logic")
    st.markdown(
        """
        - Sample scenarios make live demos fast and repeatable.
        - Interactive analysis visuals help judges inspect fit rather than just read text.
        - Reasoning and assistant pages improve transparency and user trust.
        - Light/dark glass mode improves presentation polish without changing the structure.
        """
    )

with metrics_tab:
    expected_outputs = _read_text(PROJECT_ROOT / "data" / "samples" / "expected_outputs.json")
    course_catalog = json.loads((PROJECT_ROOT / "data" / "course_catalog.json").read_text(encoding="utf-8"))

    st.markdown("### Public Datasets and Sources")
    st.markdown(
        """
        - O*NET data releases: [https://www.onetcenter.org/db_releases.html](https://www.onetcenter.org/db_releases.html)
        - Resume dataset inspiration: [https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data)
        - Job description dataset inspiration: [https://www.kaggle.com/datasets/kshitizregmi/jobs-and-job-description](https://www.kaggle.com/datasets/kshitizregmi/jobs-and-job-description)
        - Local course catalog citation: real public course URLs, curated in `data/course_catalog.json`
        """
    )

    stat1, stat2, stat3 = st.columns(3, gap="large")
    with stat1:
        st.metric("Catalog Skills", len({course.get("skill") for course in course_catalog.get("courses", [])}))
    with stat2:
        st.metric("Catalog Courses", len(course_catalog.get("courses", [])))
    with stat3:
        st.metric("Expected Output Samples", len(json.loads(expected_outputs)) if expected_outputs else 0)

    st.markdown("### Internal Validation Story")
    st.markdown(
        """
        - live evaluation page benchmarks parsing against expected sample outputs
        - match score, accuracy, precision, recall, and F1 are surfaced in the UI
        - reasoning trace shows why a skill gap exists
        - roadmap keeps paid recommendations anchored to the local course catalog
        """
    )

    e1, e2 = st.columns(2, gap="large")
    with e1:
        if st.button("Open Evaluation Page", use_container_width=True):
            st.switch_page("pages/evaluation.py")
    with e2:
        if st.button("Open Upload Playground", use_container_width=True):
            st.switch_page("pages/upload.py")

with assets_tab:
    st.markdown("### Submission Deliverables")
    st.info("The repository and documentation artifacts can be generated locally. The actual 2–3 minute demo video still needs to be recorded by the team.")

    asset1, asset2, asset3 = st.columns(3, gap="large")
    with asset1:
        _download_asset("Download README", PROJECT_ROOT / "README.md")
    with asset2:
        _download_asset("Download Demo Script", PROJECT_ROOT / "docs" / "demo_video_script.md")
    with asset3:
        _download_asset("Download 5-Slide Deck Outline", PROJECT_ROOT / "docs" / "five_slide_deck.md")

    st.markdown("### Recommended Demo Flow")
    st.markdown(
        """
        1. Open `Hackathon` page and briefly frame the problem.
        2. Go to `Upload` and load different sample scenarios.
        3. Show how `Analysis`, `Roadmap`, and `Reasoning` adapt to the new role.
        4. Ask the `Assistant` a follow-up question about the roadmap.
        5. Finish on `Evaluation` to show reliability and metrics.
        """
    )

render_footer("Built to satisfy the AI-Adaptive Onboarding Engine hackathon challenge with adaptive logic, transparent reasoning, and judge-ready assets.")

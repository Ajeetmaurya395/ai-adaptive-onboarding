# AI-Adaptive Onboarding Engine

An AI-driven onboarding workspace that parses a new hire's current capability, compares it against a target role, and generates a grounded, personalized learning pathway instead of a static curriculum.

## Hackathon Fit

This project is built for the **AI-Adaptive Onboarding Engine** challenge.

It covers the minimum required features:

- **Intelligent Parsing**: extracts skills, role signals, and experience context from Resume and Job Description inputs.
- **Dynamic Mapping**: computes the skill gap and generates an adaptive roadmap for only the missing skills.
- **Functional Interface**: ships with a multi-page Streamlit UI for upload, analysis, roadmap, reasoning, evaluation, and Qwen-based assistance.

It also strengthens several judging criteria:

- grounded recommendations via local datasets and course catalog
- reasoning trace for explainability
- interactive visual analysis
- cross-domain sample scenarios for technical, analytics, and operational roles
- documentation assets for README, demo script, and 5-slide deck outline

## Core Value Proposition

Traditional onboarding usually assumes every hire needs the same training path. This engine avoids redundant learning by:

1. parsing what the candidate already knows
2. comparing that against a target role
3. identifying only the missing capabilities
4. generating a focused roadmap to close those gaps

That makes onboarding more efficient for experienced hires while keeping it structured and safer for beginners.

## Product Features

- Resume and JD parsing with dataset-grounded skill extraction
- O*NET-informed normalization and skill comparison
- adaptive roadmap generation through a custom graph workflow
- reasoning trace in simple language
- Qwen assistant page for follow-up questions and coaching
- evaluation page with accuracy, precision, recall, F1, and match score
- light/dark glass UI mode across the full app
- sample demo scenarios for:
  - Cloud Engineer
  - Data Analyst
  - Operations Manager

## High-Level Workflow

```text
Resume / JD Input
    -> dataset-grounded parsing
    -> skill normalization
    -> candidate vs role matching
    -> missing-skill prioritization
    -> adaptive roadmap graph
    -> reasoning trace + assistant Q&A
    -> evaluation + history
```

## Adaptive Logic

The adaptive pathing logic is original to this project.

It works like this:

1. `backend/parser.py`
   Extracts structured signals from Resume and JD using Qwen plus local grounded candidate skill sets.
2. `services/vector_service.py`
   Normalizes skills against local skill lookup data, O*NET-derived terms, and Chroma or JSON fallback search.
3. `backend/gap_engine.py`
   Compares candidate and target skills, computes match score, and preserves missing-skill order.
4. `backend/roadmap_graph.py`
   Runs a graph-based adaptive pathing flow that searches the course catalog, falls back by category if needed, and compiles roadmap steps.
5. `backend/resource_library.py`
   Enriches each roadmap step with documentation, free video, book/study material, and practice resources.

## Tech Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Backend**: Python
- **LLM**: `Qwen/Qwen2.5-7B-Instruct` through the Hugging Face router
- **Embeddings / retrieval**: ChromaDB + local dataset grounding
- **Persistence**:
  - local SQLite history for analysis artifacts
  - optional MongoDB-backed user and history flows already present in the app
- **Evaluation**: custom metrics utility in `evaluation/metrics.py`

## Datasets and Sources

All datasets and model usage should be disclosed in the final presentation and demo.

This project uses or is designed around the following public sources:

- **O*NET data releases**
  - https://www.onetcenter.org/db_releases.html
- **Resume dataset inspiration**
  - https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data
- **Job description dataset inspiration**
  - https://www.kaggle.com/datasets/kshitizregmi/jobs-and-job-description

Repository data assets:

- `data/skill_lookup.json`
- `data/skill_taxonomy.json`
- `data/onet_occupations.json`
- `data/onet_tech_skills.json`
- `data/course_catalog.json`
- `data/samples/`

Notes:

- the local course catalog is curated and used as the grounded source for primary course recommendations
- roadmap enrichment adds supplemental docs, free video, study, and practice links on top of that catalog-grounded base

## Repository Structure

```text
ai-adaptive-onboarding-remote/
├── app/
│   ├── assets/
│   ├── components/
│   ├── pages/
│   │   ├── assistant.py
│   │   ├── analysis.py
│   │   ├── evaluation.py
│   │   ├── hackathon.py
│   │   ├── reasoning.py
│   │   ├── roadmap.py
│   │   └── upload.py
│   ├── database.py
│   ├── database_sqlite.py
│   └── ui.py
├── backend/
│   ├── gap_engine.py
│   ├── parser.py
│   ├── resource_library.py
│   ├── roadmap_builder.py
│   ├── roadmap_graph.py
│   ├── skill_extractor.py
│   └── trace.py
├── data/
│   ├── course_catalog.json
│   ├── onet_occupations.json
│   ├── onet_tech_skills.json
│   ├── skill_lookup.json
│   ├── skill_taxonomy.json
│   └── samples/
├── docs/
│   ├── demo_video_script.md
│   └── five_slide_deck.md
├── evaluation/
├── prompts/
├── services/
├── tests/
├── Dockerfile
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- Hugging Face API token
- optional MongoDB if you want the original DB-backed flows

### Environment Variables

Create `.env` in the project root:

```env
HF_TOKEN=your_hugging_face_token
MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=ai_onboarding
```

### Local Run

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app/ui.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app/ui.py
```

Open:

- `http://localhost:8501`

## Docker

Build:

```bash
docker build -t ai-adaptive-onboarding .
```

Run:

```bash
docker run --rm -p 8501:8501 --env-file .env ai-adaptive-onboarding
```

## Typical Demo Flow

1. Open the `Hackathon` page.
2. Move to `Upload`.
3. Choose one of the sample scenarios or upload your own Resume/JD.
4. Run analysis.
5. Show:
   - `Analysis` for interactive fit visuals
   - `Roadmap` for adaptive learning path
   - `Reasoning` for explainability
   - `Assistant` for live Qwen follow-up questions
   - `Evaluation` for metrics

## Validation and Testing

Useful checks:

```bash
python -m py_compile app/pages/*.py app/components/*.py services/*.py backend/*.py
PYTHONPATH=. ./.venv/bin/python tests/verify_bridge.py
PYTHONPATH=. ./.venv/bin/python backend/test_parser_fix.py
```

## Submission Support Assets

The repository includes helper artifacts for the remaining hackathon deliverables:

- `docs/demo_video_script.md`
- `docs/five_slide_deck.md`
- `app/pages/hackathon.py`

Important note:

- the actual 2–3 minute demo video still needs to be recorded by the team
- the slide deck still needs to be designed in presentation software, but the 5-slide structure and content are prepared

## Troubleshooting

### No analysis data appears

- verify Resume and JD both contain enough text
- use the sample scenarios to confirm the pipeline end-to-end

### MongoDB warnings appear

- the app can still run without MongoDB for local demo use
- check `MONGODB_URI` only if you want the original DB-backed user flows

### LLM API is unavailable

- verify `HF_TOKEN`
- the app falls back to lightweight local mock behavior in some paths, but the best demo uses the live API

## License

Add your preferred license before public submission.

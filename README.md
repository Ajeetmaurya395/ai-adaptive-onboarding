# AI Adaptive Onboarding

An end-to-end Streamlit application that analyzes a candidate resume against a job description, identifies skill gaps, and generates an adaptive learning roadmap with visual insights.

## What This Project Does

- Parses resume and JD text with an LLM workflow.
- Calculates matched vs missing skills.
- Generates a prioritized learning roadmap.
- Stores user accounts, analysis history, and roadmap artifacts in MongoDB.
- Provides explainability and evaluation pages for transparency and quality checks.

## Key Features

- Modern white + cyan UI with dashboard navigation.
- Authentication with user history tracking.
- Upload pipeline for PDF/TXT resume + TXT JD.
- Sample demo mode and one-click sample analysis.
- Roadmap timeline + charts (priority split and duration effort).
- CLI diagnostics, DB seeding, and stats commands.

## Tech Stack

- Frontend: Streamlit
- Backend logic: Python modules (`backend/`, `services/`)
- LLM provider: Hugging Face Inference API (configurable via env)
- Database: MongoDB (local or Atlas)
- Visualization: Plotly

## Project Structure

```text
ai-adaptive-onboarding/
├── .example .env
├── .gitignore
├── Dockerfile
├── README.md
├── main.py
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── ui.py
│   ├── utils.py
│   ├── assets/
│   │   ├── __init__.py
│   │   ├── styles.css
│   │   └── theme.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── alerts.py
│   │   ├── cards.py
│   │   ├── charts.py
│   │   ├── layout.py
│   │   ├── loaders.py
│   │   ├── navbar.py
│   │   └── timeline.py
│   └── pages/
│       ├── __init__.py
│       ├── analysis.py
│       ├── evaluation.py
│       ├── history.py
│       ├── reasoning.py
│       ├── roadmap.py
│       └── upload.py
├── backend/
│   ├── __init__.py
│   ├── gap_engine.py
│   ├── parser.py
│   ├── roadmap_builder.py
│   ├── schemas.py
│   ├── skill_extractor.py
│   └── trace.py
├── data/
│   ├── course_catalog.json
│   ├── skill_taxonomy.json
│   └── samples/
│       ├── expected_outputs.json
│       ├── jds/
│       │   ├── jd1.txt
│       │   ├── jd2.txt
│       │   └── jd3.txt
│       └── resumes/
│           ├── resume1.pdf
│           ├── resume2.pdf
│           └── resume3.pdf
├── evaluation/
│   ├── __init__.py
│   └── metrics.py
├── prompts/
│   ├── build_roadmap.txt
│   ├── explain_trace.txt
│   ├── extract_jd.txt
│   ├── extract_resume.txt
│   └── match_skills.txt
├── services/
│   ├── __init__.py
│   └── llm_service.py
├── outputs/            # generated artifacts (reports/exports)
└── tests/              # test suite (add tests here)
```

## Prerequisites

- Python 3.11+ (3.12 also works)
- MongoDB instance
  - Local: `mongodb://localhost:27017`
  - or Atlas connection URI
- Hugging Face API token

## Quick Start (Windows PowerShell)

1. Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Configure environment variables (`.env`)

Create `./.env` with:

```env
HF_TOKEN=your_hugging_face_token
MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
HF_API_URL=https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=ai_onboarding
```

4. Start MongoDB

- Local MongoDB service should be running before app launch.

5. Run the app

```powershell
streamlit run app/ui.py
```

Open `http://localhost:8501`.

## Quick Start (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app/ui.py
```

## CLI Utilities

Use `main.py` for diagnostics and data operations:

```bash
python main.py --check   # dependency + env + DB checks
python main.py --seed    # seed demo user + sample results
python main.py --stats   # show DB collection stats
python main.py           # launch app through main entrypoint
```

## Typical User Flow

1. Open **Upload** page.
2. Upload Resume + JD (or load sample data).
3. Click **Analyze Skill Gap**.
4. Review:
   - **Analysis** page for metrics/charts
   - **Roadmap** page for timeline + effort charts
   - **Reasoning** page for explainability
   - **History** page for previous runs

## Docker

Build and run:

```bash
docker build -t ai-adaptive-onboarding .
docker run --rm -p 8501:8501 --env-file .env ai-adaptive-onboarding
```

## Troubleshooting

### 1) `ModuleNotFoundError: No module named 'app'`

Run from project root with:

```bash
streamlit run app/ui.py
```

### 2) `ImportError: email-validator is not installed`

Install dependency:

```bash
pip install email-validator
```

(`email-validator` is already listed in `requirements.txt`.)

### 3) MongoDB connection errors

- Verify MongoDB is running.
- Verify `MONGODB_URI` and `MONGODB_DB`.
- For Atlas, ensure IP/network access and credentials are valid.

### 4) Repeated DB initialization logs on rerun

The app now initializes DB indexes once per process. If you still see old behavior, restart Streamlit to pick up latest code.

### 5) `.env` warnings in `python main.py --check`

`--check` expects required vars to be explicitly set. Add them in `.env` even if local defaults exist.

## Security Notes

- Never commit real API tokens or DB credentials.
- `.env` is gitignored; keep secrets there.
- Rotate any token that was accidentally exposed.

## Development Notes

- Main UI entry: `app/ui.py`
- Page modules live under `app/pages/`
- Styling is centralized in `app/assets/theme.py`
- If you change prompts, keep JSON response format strict for parser reliability.

## License

Add your preferred license (MIT/Apache-2.0/etc.) in a `LICENSE` file.

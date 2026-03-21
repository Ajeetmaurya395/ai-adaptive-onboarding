# 5-Slide Deck Outline

## Slide 1: Solution Overview

Title:

`AI-Adaptive Onboarding Engine`

Key points:

- Static onboarding wastes time for experienced hires and overwhelms beginners.
- Our engine parses current capability and generates a personalized learning path.
- Output is grounded, explainable, and role-specific.

## Slide 2: Architecture & Workflow

Key points:

- Resume and JD enter the Streamlit UI.
- Parser extracts skills using Qwen plus local grounded vocabularies.
- Vector normalization maps skills into canonical forms.
- Gap engine computes matched vs missing skills.
- Roadmap graph compiles adaptive learning steps.
- Reasoning, evaluation, and assistant layers provide transparency and interaction.

Suggested diagram:

`Input -> Parsing -> Normalization -> Gap Engine -> Adaptive Roadmap -> Reasoning / Evaluation / Assistant`

## Slide 3: Tech Stack & Models

Key points:

- Streamlit for UI
- Python backend
- Plotly for interactive visuals
- Qwen/Qwen2.5-7B-Instruct via Hugging Face router
- ChromaDB plus local JSON datasets for grounded matching
- SQLite local history and optional MongoDB-backed flows

## Slide 4: Algorithms & Training

Key points:

- dataset-grounded skill extraction from Resume and JD
- fuzzy + logical skill matching
- O*NET-aligned normalization
- original adaptive pathing logic in roadmap graph
- category fallback when a direct skill-course match is weak
- reasoning trace for explainability

Message for judges:

> Pretrained models are used for extraction and reasoning, but the adaptive pathing logic and orchestration are our own implementation.

## Slide 5: Datasets & Metrics

Key points:

- O*NET skill data
- resume dataset inspiration from Kaggle
- job description dataset inspiration from Kaggle
- curated local course catalog
- evaluation metrics: accuracy, precision, recall, F1, match score
- product impact: adaptive roadmap focuses only on missing skills

Close with:

> The system is built to reduce redundant onboarding time while preserving role-specific competency and transparent decision-making.

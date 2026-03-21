# Deployment Strategy: AI-Adaptive Onboarding Engine

This guide outlines how to move the adaptive learning engine from local development to a production server.

## 1. Environment Configuration

The application requires several environment variables and secrets:

| Variable | Description | Source |
|----------|-------------|--------|
| `HF_TOKEN` | Hugging Face API Token | [Hugging Face Settings](https://huggingface.co/settings/tokens) |
| `MODEL_NAME` | LLM Model ID | e.g., `Qwen/Qwen2.5-7B-Instruct` |
| `MONGODB_URI` | Connection string for results persistence | MongoDB Atlas |
| `API_BASE_URL` | Streamlit-to-API base URL | `http://onboarding-api:8000` in Docker |
| `DATA_SOURCE` | `local` or `cloud` asset resolution mode | deployment env |
| `HF_DATASET_REPO` | Hugging Face dataset repo that stores JSON assets | Hugging Face Hub |
| `CACHE_DIR` | Writable local cache for downloaded assets | e.g. `/tmp/ai_onboarding/data` |
| `VECTOR_BACKEND` | `auto`, `atlas`, or `local` vector retrieval mode | deployment env |
| `ATLAS_*_COLLECTION` / `ATLAS_*_INDEX` | Atlas Vector Search collection and index names | Atlas configuration |

Copy the checked-in template first:

```bash
cp .env.example .env
```

Then fill in at minimum:

- `HF_TOKEN`
- `MONGODB_URI`
- `HF_DATASET_REPO`

## 2. Data Persistence (Critical)

The backend now resolves datasets through `backend/data_loader.py`. For deployment you can either ship local data files or let the API cache remote assets from Hugging Face Hub into `/tmp`.

- **Option A (Local Mode)**: Keep `DATA_SOURCE=local` and include the required files in `data/`.
- **Option B (Cloud Mode)**: Set `DATA_SOURCE=cloud` and `HF_DATASET_REPO=<username/repo>`. Missing files will be downloaded with `huggingface_hub` into `CACHE_DIR`.
- **Recommended Production Mode**: `DATA_SOURCE=cloud` and `VECTOR_BACKEND=atlas`.
- **Vector Search Mode**: Point the `ATLAS_*` env vars at your Atlas Vector Search collections and indexes.
- **Cloud Ingestion**: Use `python scripts/index_data_atlas.py` to read local/HF-managed assets, generate embeddings, and upsert documents into your Atlas vector collections.
- **Index Creation**: Use `python scripts/create_atlas_vector_indexes.py` to request the three Atlas Vector Search indexes.
- **Verification**: Use `python scripts/verify_atlas_vector_search.py` to list index status and run sample nearest-neighbor queries.
- **Optional Full Vector Setup**: Run the bootstrap scripts during the build or deployment phase if you want ChromaDB collections available:
    ```bash
    python scripts/download_onet.py
    python scripts/build_taxonomy.py
    python scripts/index_data_chroma.py
    ```
- **Required Files for Operation**:
    - `data/skill_lookup.json`
    - `data/onet_occupations.json`
    - `data/onet_tech_skills.json`
    - `data/course_catalog.json`
    - `data/skill_taxonomy.json`
    - `data/chroma_db/` (optional vector index)

## 3. Containerization (Docker)

The repository now ships with:

- a multi-stage `Dockerfile` that keeps build tooling out of the final image
- a `docker-compose.yml` that runs API and UI as separate services
- a `.dockerignore` that avoids copying `.env`, `.venv`, logs, and local vector artifacts into the image

To start both services:

```bash
docker compose up --build
```

Service behavior:

- `onboarding-api` serves FastAPI on port `8000`
- `onboarding-ui` serves Streamlit on port `8501`
- the UI waits for the API health check
- Hugging Face asset downloads are cached in the named `hf-cache` volume
- local bind mounts are no longer required for production

## 4. Deployment Platforms

### Option A: Docker Host / VPS (Recommended)
1. Provision any small VM or container host with Docker.
2. Copy `.env.example` to `.env` and fill in Atlas + Hugging Face values.
3. Run `docker compose up --build -d`.
4. Put Nginx, Caddy, or your platform proxy in front of ports `8000` and `8501`.

### Option B: Streamlit Community Cloud + External API
1. Host the FastAPI service separately on a Docker-capable target.
2. Deploy the Streamlit app to [Streamlit Cloud](https://share.streamlit.io/).
3. Set `API_BASE_URL` in Streamlit secrets to the public API URL.
4. Add `HF_TOKEN`, `MONGODB_URI`, `HF_DATASET_REPO`, and Atlas index env vars to secrets.

### Option C: Render Blueprint
The repository now includes a [render.yaml](/Users/ajeetmaurya/ai-adaptive-onboarding-remote/render.yaml) blueprint for a two-service Render deploy:

- `ai-onboarding-api`
- `ai-onboarding-ui`

How to launch it:

1. Push the latest repo changes to GitHub.
2. In Render, choose `New +` -> `Blueprint`.
3. Select this repository and branch.
4. Render will detect `render.yaml` and prepare both services.
5. Enter these secret values when prompted:
   - `HF_TOKEN`
   - `MONGODB_URI`
   - `HF_DATASET_REPO`
6. Confirm the default Atlas collection/index names unless you changed them.
7. Deploy the blueprint.

Notes:

- The UI uses Render private-network service discovery through `API_HOST` and `API_PORT`, so you do not need to hardcode a public API URL.
- The API service exposes `/health`.
- The UI service uses Streamlit’s `/_stcore/health` endpoint for health checks.

## 5. Scaling Considerations
- **LLM API**: The current implementation uses the serverless Inference API. For high volumes, consider **Inference Endpoints** (dedicated GPUs) on Hugging Face.
- **Database**: Ensure MongoDB Atlas has proper indexing on `user_id` and `timestamp`.
- **Frontend/API split**: The Streamlit app is now a client of the FastAPI backend, which keeps long-running analysis work out of the UI thread.
- **Atlas Vector Search**: All three vector indexes should remain queryable before switching fully to `VECTOR_BACKEND=atlas`.

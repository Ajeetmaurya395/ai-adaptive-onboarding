# Deployment Strategy: AI-Adaptive Onboarding Engine

This guide outlines how to move the adaptive learning engine from local development to a production server.

## 1. Environment Configuration

The application requires several environment variables and secrets:

| Variable | Description | Source |
|----------|-------------|--------|
| `HF_TOKEN` | Hugging Face API Token | [Hugging Face Settings](https://huggingface.co/settings/tokens) |
| `MODEL_NAME` | LLM Model ID | e.g., `Qwen/Qwen2.5-7B-Instruct` |
| `MONGODB_URI` | Connection string for results persistence | MongoDB Atlas or Local |

## 2. Data Persistence (Critical)

The O*NET taxonomy and search indices are stored as JSON files in the `data/` directory. Since these are now excluded from the git repository to keep it lightweight, you must ensure they are persistent:

- **Option A (Self-Bootstrapping)**: Run the bootstrap scripts during the build or deployment phase:
    ```bash
    python scripts/download_onet.py
    python scripts/build_taxonomy.py
    python scripts/index_data_chroma.py
    ```
- **Option B (Persistent Volume)**: If deploying to a VPS/Cloud, volume-mount a persistent directory to `/app/data` where these files are stored.
- **Required Files for Operation**:
    - `data/skill_lookup.json`
    - `data/onet_occupations.json`
    - `data/onet_tech_skills.json`
    - `data/course_catalog.json`
    - `data/chroma_db/` (Vector index)

## 3. Containerization (Docker)

Create a `Dockerfile` in the root directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and pre-generated data
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app/ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 4. Deployment Platforms

### Option A: Streamlit Community Cloud (Easiest)
1. Push code to GitHub.
2. Connect repository to [Streamlit Cloud](https://share.streamlit.io/).
3. Add `HF_TOKEN` and `MONGODB_URI` to "Secrets".

### Option B: Cloud VPS (AWS/GCP/DigitalOcean)
1. Deploy via Docker Compose.
2. Use **Nginx** as a reverse proxy with SSL (Certbot/Let's Encrypt).
3. Ensure port 8501 is restricted to the proxy.

## 5. Scaling Considerations
- **LLM API**: The current implementation uses the serverless Inference API. For high volumes, consider **Inference Endpoints** (dedicated GPUs) on Hugging Face.
- **Database**: Ensure MongoDB has proper indexing on `user_id` and `timestamp`.

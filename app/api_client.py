import os
from typing import Dict, Optional

import requests


def _resolve_api_base_url() -> str:
    explicit_base_url = (os.getenv("API_BASE_URL") or "").strip()
    if explicit_base_url:
        return explicit_base_url.rstrip("/")

    api_host = (os.getenv("API_HOST") or "localhost").strip()
    api_port = (os.getenv("API_PORT") or "8000").strip()
    return f"http://{api_host}:{api_port}".rstrip("/")


API_BASE_URL = _resolve_api_base_url()
ANALYZE_URL = f"{API_BASE_URL}/analyze"
HEALTHCHECK_URL = f"{API_BASE_URL}/health"


def analyze_resume_jd(resume_text: str, jd_text: str, user_id: Optional[str] = None, timeout: int = 180) -> Dict:
    payload = {
        "resume_text": resume_text,
        "jd_text": jd_text,
        "user_id": user_id,
    }
    response = requests.post(ANALYZE_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def is_api_available(timeout: int = 3) -> bool:
    try:
        response = requests.get(HEALTHCHECK_URL, timeout=timeout)
        return response.ok
    except requests.RequestException:
        return False

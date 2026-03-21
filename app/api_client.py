import os
from typing import Dict, Optional

import requests


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
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

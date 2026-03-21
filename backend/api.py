import os
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.database import save_result, save_roadmap
from backend.gap_engine import gap_engine


app = FastAPI(title="AI-Adaptive Onboarding API", version="1.0.0")


class AnalysisRequest(BaseModel):
    resume_text: str = Field(..., min_length=50)
    jd_text: str = Field(..., min_length=50)
    user_id: Optional[str] = None


class AnalysisResponse(BaseModel):
    summary: Dict
    skills: Dict
    gap: Dict
    roadmap: List[Dict]
    raw_text: Dict
    resume: Dict
    jd: Dict
    trace_steps: List[Dict]
    persistence: Dict


@app.get("/health")
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_onboarding(request: AnalysisRequest) -> Dict:
    trace_steps: List[Dict] = []

    try:
        result = gap_engine.process(
            request.resume_text,
            request.jd_text,
            trace_callback=trace_steps.append,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    persistence = {"saved": False, "backend": "none"}
    user_id = (request.user_id or "").strip()
    if user_id and user_id != "demo_user":
        gap_payload = {
            "matched_skills": result.get("skills", {}).get("matched", []),
            "missing_skills": result.get("skills", {}).get("missing", []),
        }
        save_ok, result_id = save_result(
            user_id=user_id,
            score=result.get("summary", {}).get("match_score", 0),
            gap_data=gap_payload,
            metadata={"source": "api"},
        )
        roadmap_ok, roadmap_id = save_roadmap(
            user_id=user_id,
            roadmap_data={
                "target_role": result.get("summary", {}).get("role_detected", "Target Role"),
                "items": result.get("roadmap", []),
            },
            metadata={"source": "api"},
        )
        persistence = {
            "saved": bool(save_ok and roadmap_ok),
            "backend": "mongodb",
            "result_id": result_id if save_ok else None,
            "roadmap_id": roadmap_id if roadmap_ok else None,
        }

    result["trace_steps"] = trace_steps
    result["persistence"] = persistence
    return result


if __name__ == "__main__":
    uvicorn.run(
        "backend.api:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=False,
    )

import os
import re
from difflib import SequenceMatcher
from services.llm_service import llm
from backend.skill_extractor import skill_extractor


def load_prompt(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_dir, "prompts", filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def _normalize_resume_result(result):
    if not isinstance(result, dict):
        return {"skills": [], "experience_years": 0, "summary": "Parser returned invalid data"}

    skills = result.get("skills", [])
    if not isinstance(skills, list):
        skills = []

    return {
        "skills": [str(skill).strip() for skill in skills if str(skill).strip()],
        "experience_years": int(result.get("experience_years", 0) or 0),
        "summary": result.get("summary") or "No summary available",
        "source": result.get("source", "llm"),
        "confidence": float(result.get("confidence", 0.8) or 0.8),
    }


def _normalize_jd_result(result):
    if not isinstance(result, dict):
        return {"skills": [], "role": "Unknown", "seniority": "Mid"}

    skills = result.get("skills", [])
    if not isinstance(skills, list):
        skills = []

    seniority = result.get("seniority") or "Mid"
    if seniority not in {"Junior", "Mid", "Senior", "Lead", "Principal"}:
        seniority = "Mid"

    return {
        "skills": [str(skill).strip() for skill in skills if str(skill).strip()],
        "role": result.get("role") or "Unknown",
        "seniority": seniority,
        "source": result.get("source", "llm"),
        "confidence": float(result.get("confidence", 0.8) or 0.8),
    }


def _dedupe_preserve_order(skills):
    seen = set()
    ordered = []
    for skill in skills:
        cleaned = str(skill).strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(cleaned)
    return ordered


def _normalize_match_key(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", value.lower())).strip()


def _infer_role_from_text(text: str) -> str:
    lines = [line.strip(" -:\t") for line in text.splitlines() if line.strip()]
    role_patterns = [
        r"([A-Z][A-Za-z/&\-\s]+(?:Engineer|Developer|Scientist|Architect|Analyst|Manager|Administrator|Specialist))",
        r"(Senior|Lead|Principal|Staff|Junior|Mid)[\s\-]+([A-Z][A-Za-z/&\-\s]+(?:Engineer|Developer|Scientist|Architect|Analyst|Manager|Administrator|Specialist))",
    ]

    for line in lines[:8]:
        for pattern in role_patterns:
            match = re.search(pattern, line, flags=re.IGNORECASE)
            if match:
                return " ".join(part for part in match.groups() if part).strip()
    return "Unknown"


def _infer_seniority(text: str) -> str:
    lowered = text.lower()
    if "principal" in lowered:
        return "Principal"
    if "lead" in lowered:
        return "Lead"
    if "senior" in lowered:
        return "Senior"
    if "junior" in lowered:
        return "Junior"
    return "Mid"


def parse_resume(text):
    if not text or len(text.strip()) < 50:
        return {"skills": [], "experience_years": 0, "summary": "Insufficient text"}

    grounded = skill_extractor.extract_from_text(text, context="resume")
    prompt_template = load_prompt("extract_resume.txt")
    prompt = prompt_template.format(
        text=(
            f"Grounded skills detected from local datasets: {', '.join(grounded.get('skills', [])[:30]) or 'None'}\n\n"
            f"{text[:3000]}"
        )
    )

    result = llm.generate(
        system_prompt="You are a precise JSON output engine. Always respond with valid JSON only.",
        user_prompt=prompt,
        response_type="json"
    )
    normalized = _normalize_resume_result(result)
    normalized["skills"] = _dedupe_preserve_order(grounded.get("skills", []) + normalized.get("skills", []))
    normalized["experience_years"] = normalized.get("experience_years") or grounded.get("experience_years") or 0
    normalized["source"] = grounded.get("source", normalized.get("source", "llm"))
    normalized["confidence"] = max(float(normalized.get("confidence", 0.0)), float(grounded.get("confidence", 0.0)))
    return normalized


def parse_jd(text):
    if not text or len(text.strip()) < 50:
        return {"skills": [], "role": "Unknown", "seniority": "Mid"}

    grounded = skill_extractor.extract_from_text(text, context="jd")
    prompt_template = load_prompt("extract_jd.txt")
    prompt = prompt_template.format(
        text=(
            f"Grounded skills detected from local datasets: {', '.join(grounded.get('skills', [])[:30]) or 'None'}\n\n"
            f"{text[:3000]}"
        )
    )

    result = llm.generate(
        system_prompt="You are a precise JSON output engine. Always respond with valid JSON only.",
        user_prompt=prompt,
        response_type="json"
    )
    normalized = _normalize_jd_result(result)
    normalized["skills"] = _dedupe_preserve_order(grounded.get("skills", []) + normalized.get("skills", []))
    if normalized.get("role", "Unknown") == "Unknown":
        normalized["role"] = _infer_role_from_text(text)
    if normalized.get("seniority", "Mid") == "Mid":
        normalized["seniority"] = _infer_seniority(text)
    normalized["source"] = grounded.get("source", normalized.get("source", "llm"))
    normalized["confidence"] = max(float(normalized.get("confidence", 0.0)), float(grounded.get("confidence", 0.0)))
    return normalized


def match_skills(candidate_skills, required_skills, role_context, seniority="Mid"):
    if not candidate_skills or not required_skills:
        return {
            "matched_skills": [],
            "missing_skills": required_skills if required_skills else [],
            "match_summary": {"weighted_match_score": 0.0, "overall_fit": "Poor"}
        }
    
    prompt_template = load_prompt("match_skills.txt")
    
    candidate_str = ", ".join(candidate_skills) if isinstance(candidate_skills, list) else candidate_skills
    required_str = ", ".join(required_skills) if isinstance(required_skills, list) else required_skills
    
    prompt = prompt_template.format(
        candidate_skills=candidate_str,
        required_skills=required_str,
        role_context=role_context,
        seniority_level=seniority
    )
    
    result = llm.generate(
        system_prompt="You are a precise JSON output engine. Return ONLY valid JSON.",
        user_prompt=prompt,
        response_type="json"
    )
    if isinstance(result, dict) and result.get("match_summary"):
        return result

    candidate_keys = {skill: _normalize_match_key(skill) for skill in candidate_skills}
    matched = []
    missing = []
    for req in required_skills:
        req_key = _normalize_match_key(req)
        best_candidate = None
        best_score = 0.0
        for candidate_skill, candidate_key in candidate_keys.items():
            if not candidate_key or not req_key:
                continue
            score = SequenceMatcher(None, candidate_key, req_key).ratio()
            if req_key == candidate_key:
                score = 1.0
            elif req_key in candidate_key or candidate_key in req_key:
                score = max(score, 0.86)
            if score > best_score:
                best_score = score
                best_candidate = candidate_skill

        if best_candidate and best_score >= 0.72:
            matched.append({
                "candidate_skill": best_candidate,
                "required_skill": req,
                "normalized_skill": req,
                "confidence": round(best_score, 2),
                "match_type": "exact" if best_score >= 0.95 else "partial",
                "notes": "Fallback grounded fuzzy matching was used.",
            })
        else:
            missing.append({
                "skill": req,
                "normalized_skill": req,
                "priority": "Critical",
                "reason": f"Required for the {role_context} role.",
                "transferable_alternatives": [],
                "suggested_learning_path": f"Build experience in {req} through guided project work and courses.",
            })

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": [],
        "match_summary": {
            "total_required": len(required_skills),
            "exact_matches": len(matched),
            "synonym_matches": 0,
            "partial_matches": 0,
            "missing_count": len(missing),
            "extra_count": 0,
            "weighted_match_score": round((len(matched) / len(required_skills) * 100), 2) if required_skills else 0.0,
            "overall_fit": "Strong" if len(missing) <= 2 else "Moderate" if len(missing) <= 5 else "Weak",
            "fit_explanation": "Fallback grounded matching was used because the model response was unavailable.",
        },
    }


def parse_batch(documents, doc_type="resume"):
    results = []
    prompt_file = "extract_resume.txt" if doc_type == "resume" else "extract_jd.txt"
    prompt_template = load_prompt(prompt_file)
    
    for doc in documents:
        text = doc.get("text", "")
        doc_id = doc.get("id", "unknown")
        
        if not text or len(text.strip()) < 50:
            results.append({"id": doc_id, "error": "Insufficient text", "data": {}})
            continue
        
        prompt = prompt_template.format(text=text[:3000])
        if doc_type == "resume":
            parsed = parse_resume(text)
        else:
            parsed = parse_jd(text)
        results.append({"id": doc_id, "error": None, "data": parsed})
    
    return results

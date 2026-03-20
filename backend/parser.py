import os
from services.llm_service import llm


def load_prompt(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_dir, "prompts", filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_resume(text):
    if not text or len(text.strip()) < 50:
        return {"skills": [], "experience_years": 0, "summary": "Insufficient text"}
    
    prompt_template = load_prompt("extract_resume.txt")
    prompt = prompt_template.format(text=text[:3000])
    
    return llm.generate(
        system_prompt="You are a precise JSON output engine. Always respond with valid JSON only.",
        user_prompt=prompt,
        response_type="json"
    )


def parse_jd(text):
    if not text or len(text.strip()) < 50:
        return {"skills": [], "role": "Unknown", "seniority": "Mid"}
    
    prompt_template = load_prompt("extract_jd.txt")
    prompt = prompt_template.format(text=text[:3000])
    
    return llm.generate(
        system_prompt="You are a precise JSON output engine. Always respond with valid JSON only.",
        user_prompt=prompt,
        response_type="json"
    )


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
    
    return llm.generate(
        system_prompt="You are a precise JSON output engine. Return ONLY valid JSON.",
        user_prompt=prompt,
        response_type="json"
    )


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
        parsed = llm.generate(
            system_prompt="You are a precise JSON output engine. Always respond with valid JSON only.",
            user_prompt=prompt,
            response_type="json"
        )
        
        results.append({"id": doc_id, "error": None, "data": parsed})
    
    return results
import os
from services.llm_service import llm

def load_prompt(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_dir, "prompts", filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def explain_reasoning(resume_summary, jd_role, gap_data):
    """Generate human-readable explanation of skill gap analysis"""
    missing = gap_data.get("missing_skills", [])
    
    if not missing:
        return "✅ Excellent match! The candidate possesses all key skills required for this role."
    
    prompt_template = load_prompt("explain_trace.txt")
    prompt = prompt_template.format(
        candidate_summary=resume_summary[:200],
        target_role=jd_role,
        missing_skills=", ".join(missing[:5])  # Limit to top 5 for context
    )
    
    explanation = llm.generate(
        system_prompt="You are a helpful career coach. Provide clear, encouraging feedback.",
        user_prompt=prompt,
        response_type="text"
    )
    
    return explanation if explanation else f"The candidate is missing {len(missing)} key skill(s) for the {jd_role} position: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}. Focus on these areas to improve fit."
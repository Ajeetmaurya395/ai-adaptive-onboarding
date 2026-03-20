from services.llm_service import llm
import os

def load_prompt(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_dir, "prompts", filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def generate_roadmap(missing_skills, role_context="Target Role"):
    """Generate personalized learning roadmap for missing skills"""
    if not missing_skills:
        return []
    
    # Load course catalog for resource suggestions
    catalog_path = os.path.join(os.path.dirname(__file__), "..", "data", "course_catalog.json")
    courses = {}
    
    if os.path.exists(catalog_path):
        import json
        with open(catalog_path, "r") as f:
            data = json.load(f)
            for course in data.get("courses", []):
                courses[course["skill"].lower()] = course
    
    # Build context for prompt
    skill_list = ", ".join(missing_skills[:10])  # Limit for context window
    
    prompt_template = load_prompt("build_roadmap.txt")
    prompt = prompt_template.format(
        missing_skills=skill_list,
        role_context=role_context
    )
    
    roadmap = llm.generate(
        system_prompt="You are a precise JSON output engine. Return ONLY a valid JSON array.",
        user_prompt=prompt,
        response_type="json"
    )
    
    # Validate and enhance results
    if isinstance(roadmap, list) and len(roadmap) > 0:
        # Add fallback resources from catalog if missing
        for item in roadmap:
            skill = item.get("skill", "").lower()
            if not item.get("resource") and skill in courses:
                item["resource"] = courses[skill].get("title", "Online Course")
            if not item.get("duration"):
                item["duration"] = "4 weeks"
            if not item.get("priority"):
                item["priority"] = "High"
        return roadmap
    
    # Fallback: generate basic roadmap from catalog
    fallback = []
    for skill in missing_skills[:5]:  # Limit to 5 for fallback
        skill_lower = skill.lower()
        resource = courses.get(skill_lower, {}).get("title", f"{skill} Fundamentals Course")
        fallback.append({
            "skill": skill,
            "resource": resource,
            "duration": "4 weeks",
            "priority": "High" if len(missing_skills) <= 3 else "Medium"
        })
    
    return fallback
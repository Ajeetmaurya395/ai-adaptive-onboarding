from backend.roadmap_graph import run_roadmap_graph
import os
import json

def generate_roadmap(missing_skills, role_context="Target Role"):
    """Generate personalized learning roadmap for missing skills using LangGraph workflow."""
    if not missing_skills:
        return []
    
    # Use LangGraph for orchestrated roadmap generation
    try:
        roadmap_items = run_roadmap_graph(missing_skills, role_context)
        if roadmap_items:
            return roadmap_items
    except Exception as e:
        print(f"LangGraph roadmap generation failed: {e}")
    
    # Fallback robust steps
    return [
        {
            "step": i + 1,
            "title": f"Mastering {skill}",
            "course_name": f"{skill} Specialist Certification",
            "url": "https://coursera.org",
            "reasoning": f"Identified as a critical gap for the {role_context} role."
        }
        for i, skill in enumerate(missing_skills[:5])
    ]
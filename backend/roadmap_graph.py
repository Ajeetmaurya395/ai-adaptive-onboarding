from typing import Annotated, Dict, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
import operator

from backend.resource_library import build_learning_resources

class RoadmapState(TypedDict):
    role: str
    missing_skills: List[str]
    courses_found: Annotated[List[Dict], operator.add]
    roadmap: List[Dict]
    current_skill_index: int

def get_category_for_skill(skill: str) -> str:
    """Helper to map a skill to its O*NET category."""
    import json
    try:
        with open("data/skill_taxonomy.json", "r") as f:
            taxonomy = json.load(f)["categories"]
        for cat_label, skill_list in taxonomy.items():
            if any(skill.lower() == s.lower() for s in skill_list):
                return cat_label
    except:
        pass
    return None

def search_courses_node(state: RoadmapState):
    """Search for courses with Agentic Loop-back if needed."""
    from services.vector_service import vector_service
    
    idx = state["current_skill_index"]
    if idx >= len(state["missing_skills"]):
        return {"current_skill_index": idx}
        
    skill = state["missing_skills"][idx]
    
    # Try Direct Search
    courses = vector_service.get_relevant_courses(skill, n_results=1)
    
    # Loop-back Logic: if weak match, search by category
    if not courses or (courses and courses[0].get("distance", 1.0) > 0.5):
        category = get_category_for_skill(skill)
        if category:
            courses_cat = vector_service.get_relevant_courses(category, n_results=1)
            if courses_cat:
                courses = courses_cat
                
    found = []
    if courses:
        found.append({
            "skill": skill,
            "course": courses[0],
        })
    else:
        found.append({
            "skill": skill,
            "course": {
                "title": f"{skill} Specialist Certification",
                "metadata": {
                    "title": f"{skill} Specialist Certification",
                    "duration": "4 weeks",
                    "provider": "Curated Catalog",
                    "level": "Intermediate",
                    "url": "",
                },
                "distance": 1.0,
            },
        })
        
    return {
        "courses_found": found,
        "current_skill_index": idx + 1
    }

def compile_roadmap_node(state: RoadmapState):
    """Compile the final roadmap from found courses."""
    roadmap = []
    for i, c in enumerate(state["courses_found"]):
        metadata = c["course"].get("metadata", {})
        priority = "High" if i < 2 else "Medium" if i < 4 else "Low"
        resource = metadata.get("title") or c["course"].get("title", f"{c['skill']} Expert")
        learning_resources = build_learning_resources(
            c["skill"],
            {
                "title": resource,
                "resource": resource,
                "url": metadata.get("url", ""),
                "provider": metadata.get("provider", "Curated Catalog"),
            },
        )
        free_resource_count = sum(1 for item in learning_resources if item.get("cost") == "Free")
        paid_resource_count = sum(1 for item in learning_resources if item.get("cost") == "Paid")
        roadmap.append({
            "step": i + 1,
            "title": f"Mastering {c['skill']}",
            "skill": c["skill"],
            "resource": resource,
            "course_name": resource,
            "duration": metadata.get("duration", "4 weeks"),
            "priority": priority,
            "url": metadata.get("url", ""),
            "provider": metadata.get("provider", "Curated Catalog"),
            "level": metadata.get("level", "Intermediate"),
            "reasoning": f"Recommended for the {state['role']} role based on the missing skill {c['skill']}.",
            "source": c["course"].get("source", "catalog-fallback"),
            "learning_resources": learning_resources,
            "resource_mix": ", ".join(item.get("type", "Resource") for item in learning_resources),
            "free_resource_count": free_resource_count,
            "paid_resource_count": paid_resource_count,
        })
    return {"roadmap": roadmap}

def should_continue(state: RoadmapState):
    """Check if there are more skills to process."""
    if state["current_skill_index"] < len(state["missing_skills"]) and state["current_skill_index"] < 5:
        return "continue"
    return "end"

# Build Graph
builder = StateGraph(RoadmapState)
builder.add_node("search", search_courses_node)
builder.add_node("compile", compile_roadmap_node)

builder.set_entry_point("search")
builder.add_conditional_edges(
    "search",
    should_continue,
    {
        "continue": "search",
        "end": "compile"
    }
)
builder.add_edge("compile", END)

roadmap_graph = builder.compile()

def run_roadmap_graph(missing_skills: List[str], role: str):
    """Interface to run the LangGraph workflow."""
    initial_state = {
        "role": role,
        "missing_skills": missing_skills,
        "courses_found": [],
        "roadmap": [],
        "current_skill_index": 0
    }
    result = roadmap_graph.invoke(initial_state)
    return result["roadmap"]

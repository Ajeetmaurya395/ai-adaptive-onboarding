import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.gap_engine import GapEngine

def test_bridge():
    engine = GapEngine()
    resume_text = "Software Engineer with Python, Docker, and Git experience."
    jd_text = "Looking for a Software Engineer with Python, Docker, Git, Kubernetes, and Redis."
    
    print("Running process()...")
    result = engine.process(resume_text, jd_text)
    
    print("\nUnified Schema Verification:")
    print(f"Summary: {result.get('summary')}")
    print(f"Skills Matched: {len(result['skills']['matched'])}")
    print(f"Skills Missing: {len(result['skills']['missing'])}")
    print(f"Roadmap Steps: {len(result['roadmap'])}")
    
    if result['roadmap']:
        print(f"First Roadmap Step: {result['roadmap'][0]}")
    
    print("\nRaw Text Check:")
    print(f"Resume Snippet: {result['raw_text']['resume'][:50]}...")
    
    # Check if schema keys exist as requested
    required_keys = ["summary", "skills", "roadmap", "raw_text"]
    for key in required_keys:
        if key in result:
            print(f"[OK] Key '{key}' found.")
        else:
            print(f"[MISSING] Key '{key}' not found.")

if __name__ == "__main__":
    test_bridge()

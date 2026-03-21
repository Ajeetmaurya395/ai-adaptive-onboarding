import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.parser import parse_resume, parse_jd
import json

def test_parsing():
    sample_resume = "Software Engineer with 5 years experience in Python and Java."
    sample_jd = "Senior Python Developer role requiring AWS and Docker experience."
    
    print("Testing parse_resume...")
    resume_data = parse_resume(sample_resume)
    print(f"Resume Data: {json.dumps(resume_data, indent=2)}")
    
    print("\nTesting parse_jd...")
    jd_data = parse_jd(sample_jd)
    print(f"JD Data: {json.dumps(jd_data, indent=2)}")

if __name__ == "__main__":
    test_parsing()

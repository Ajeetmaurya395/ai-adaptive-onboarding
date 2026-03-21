import json
import os
from services.vector_service import vector_service

def index_all():
    batch_size = 2000
    
    # 1. Index O*NET Skills
    skill_path = "data/skill_lookup.json"
    if os.path.exists(skill_path):
        with open(skill_path, "r") as f:
            skills = json.load(f)
            docs = list(skills.keys())
            ids = [f"skill_{i}" for i in range(len(docs))]
            
            for i in range(0, len(docs), batch_size):
                end = min(i + batch_size, len(docs))
                vector_service.onet_skills.upsert(
                    ids=ids[i:end], 
                    documents=docs[i:end]
                )
            print(f"Indexed {len(docs)} O*NET skills.")

    # 2. Index Occupations
    occ_path = "data/onet_occupations.json"
    if os.path.exists(occ_path):
        with open(occ_path, "r") as f:
            occs_dict = json.load(f)
            occs = list(occs_dict.values())
            docs = [o["title"] for o in occs]
            ids = [f"occ_{i}" for i in range(len(docs))]
            metadatas = [{"soc": o.get("code", o.get("soc", "unknown"))} for o in occs]
            
            for i in range(0, len(docs), batch_size):
                end = min(i + batch_size, len(docs))
                vector_service.onet_occupations.upsert(
                    ids=ids[i:end], 
                    documents=docs[i:end], 
                    metadatas=metadatas[i:end]
                )
            print(f"Indexed {len(docs)} O*NET occupations.")

    # 3. Index Course Catalog
    course_path = "data/course_catalog.json"
    if os.path.exists(course_path):
        with open(course_path, "r") as f:
            data = json.load(f)
            courses = data.get("courses", [])
            ids = [f"course_{i}" for i in range(len(courses))]
            docs = [c["title"] for c in courses]
            metadatas = [c for c in courses]
            vector_service.course_catalog.upsert(ids=ids, documents=docs, metadatas=metadatas)
            print(f"Indexed {len(courses)} courses.")

if __name__ == "__main__":
    index_all()

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from services.vector_service import VectorService


def list_search_indexes(collection, expected_index_name: str) -> None:
    indexes = list(collection.aggregate([{"$listSearchIndexes": {}}]))
    print(f"\nCollection: {collection.name}")
    if not indexes:
        print("  No search/vector indexes found.")
        return
    for index in indexes:
        marker = " (expected)" if index.get("name") == expected_index_name else ""
        print(
            f"  - {index.get('name')} | type={index.get('type')} | queryable={index.get('queryable')}{marker}"
        )


def main() -> None:
    mongo_uri = os.getenv("MONGODB_URI", "").strip()
    mongo_db_name = os.getenv("MONGODB_DB", "ai_onboarding").strip()

    if not mongo_uri:
        raise ValueError("MONGODB_URI is required.")

    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]

    skills_collection_name = os.getenv("ATLAS_SKILLS_COLLECTION", "skill_vectors").strip()
    occupations_collection_name = os.getenv("ATLAS_OCCUPATIONS_COLLECTION", "occupation_vectors").strip()
    courses_collection_name = os.getenv("ATLAS_COURSES_COLLECTION", "course_vectors").strip()

    list_search_indexes(db[skills_collection_name], os.getenv("ATLAS_SKILLS_INDEX", "skills_vector_index").strip())
    list_search_indexes(
        db[occupations_collection_name],
        os.getenv("ATLAS_OCCUPATIONS_INDEX", "occupations_vector_index").strip(),
    )
    list_search_indexes(
        db[courses_collection_name],
        os.getenv("ATLAS_COURSES_INDEX", "courses_vector_index").strip(),
    )

    os.environ["VECTOR_BACKEND"] = "atlas"
    vector_service = VectorService()

    print("\nSample skill query:")
    print(vector_service.get_nearest_skills("python backend api", n_results=3))

    print("\nSample occupation query:")
    print(vector_service.get_nearest_occupation("data analyst"))

    print("\nSample course query:")
    print(vector_service.get_relevant_courses("docker", n_results=3))


if __name__ == "__main__":
    main()

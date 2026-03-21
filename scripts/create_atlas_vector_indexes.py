import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")


def vector_index_definition(num_dimensions: int) -> dict:
    return {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": num_dimensions,
                "similarity": "cosine",
            }
        ]
    }


def create_vector_index(db, collection_name: str, index_name: str, num_dimensions: int) -> None:
    command = {
        "createSearchIndexes": collection_name,
        "indexes": [
            {
                "name": index_name,
                "type": "vectorSearch",
                "definition": vector_index_definition(num_dimensions),
            }
        ],
    }
    result = db.command(command)
    print(f"Requested index '{index_name}' on '{collection_name}': {result}")


def main() -> None:
    mongo_uri = os.getenv("MONGODB_URI", "").strip()
    mongo_db_name = os.getenv("MONGODB_DB", "ai_onboarding").strip()
    num_dimensions = int(os.getenv("ATLAS_VECTOR_DIMENSIONS", "384"))

    if not mongo_uri:
        raise ValueError("MONGODB_URI is required.")

    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]

    create_vector_index(
        db,
        os.getenv("ATLAS_SKILLS_COLLECTION", "skill_vectors").strip(),
        os.getenv("ATLAS_SKILLS_INDEX", "skills_vector_index").strip(),
        num_dimensions,
    )
    create_vector_index(
        db,
        os.getenv("ATLAS_OCCUPATIONS_COLLECTION", "occupation_vectors").strip(),
        os.getenv("ATLAS_OCCUPATIONS_INDEX", "occupations_vector_index").strip(),
        num_dimensions,
    )
    create_vector_index(
        db,
        os.getenv("ATLAS_COURSES_COLLECTION", "course_vectors").strip(),
        os.getenv("ATLAS_COURSES_INDEX", "courses_vector_index").strip(),
        num_dimensions,
    )


if __name__ == "__main__":
    main()

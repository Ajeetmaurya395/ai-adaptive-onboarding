import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, List

from dotenv import load_dotenv
from pymongo import MongoClient, ReplaceOne
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from backend.data_loader import data_loader


def normalize_id(prefix: str, value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return f"{prefix}:{cleaned or 'unknown'}"


def chunked(items: List[Dict], size: int) -> Iterable[List[Dict]]:
    for start in range(0, len(items), size):
        yield items[start:start + size]


def build_skill_documents() -> List[Dict]:
    taxonomy = data_loader.load_json("skill_taxonomy.json", {})
    categories = taxonomy.get("categories", {})
    documents: List[Dict] = []
    seen = set()

    for category, skills in categories.items():
        for skill in skills:
            key = skill.strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            documents.append({
                "_id": normalize_id("skill", skill),
                "canonical": skill,
                "category": category,
                "source": "skill_taxonomy",
                "embedding_text": f"{skill}. Category: {category}.",
            })

    return documents


def build_occupation_documents() -> List[Dict]:
    occupations = data_loader.load_json("onet_occupations.json", {})
    documents: List[Dict] = []

    for code, payload in occupations.items():
        title = payload.get("title", code)
        raw_skills = payload.get("skills", [])[:20]
        raw_knowledge = payload.get("knowledge", [])[:20]
        skills = [item.get("name", "") if isinstance(item, dict) else str(item) for item in raw_skills]
        knowledge = [item.get("name", "") if isinstance(item, dict) else str(item) for item in raw_knowledge]
        skills = [item for item in skills if item]
        knowledge = [item for item in knowledge if item]
        summary_parts = [title]
        if skills:
            summary_parts.append(f"Skills: {', '.join(skills)}")
        if knowledge:
            summary_parts.append(f"Knowledge: {', '.join(knowledge)}")

        documents.append({
            "_id": normalize_id("occupation", code),
            "code": code,
            "title": title,
            "skills": skills,
            "knowledge": knowledge,
            "metadata": {
                "code": code,
                "raw_skills": raw_skills,
                "raw_knowledge": raw_knowledge,
                "skills": skills,
                "knowledge": knowledge,
            },
            "source": "onet_occupations",
            "embedding_text": ". ".join(summary_parts),
        })

    return documents


def build_course_documents() -> List[Dict]:
    catalog = data_loader.load_json("course_catalog.json", {})
    courses = catalog.get("courses", [])
    documents: List[Dict] = []

    for course in courses:
        title = course.get("title", "Untitled Course")
        skill = course.get("skill", "")
        provider = course.get("provider", "")
        level = course.get("level", "")
        duration = course.get("duration", "")

        summary_parts = [title]
        if skill:
            summary_parts.append(f"Skill: {skill}")
        if provider:
            summary_parts.append(f"Provider: {provider}")
        if level:
            summary_parts.append(f"Level: {level}")
        if duration:
            summary_parts.append(f"Duration: {duration}")

        documents.append({
            "_id": normalize_id("course", course.get("id", title)),
            "title": title,
            "metadata": course,
            "source": "course_catalog",
            "embedding_text": ". ".join(summary_parts),
        })

    return documents


def add_embeddings(documents: List[Dict], model: SentenceTransformer, batch_size: int) -> List[Dict]:
    texts = [doc["embedding_text"] for doc in documents]
    vectors = model.encode(texts, batch_size=batch_size, normalize_embeddings=True)

    enriched = []
    for doc, vector in zip(documents, vectors):
        item = dict(doc)
        item["embedding"] = vector.tolist()
        item.pop("embedding_text", None)
        enriched.append(item)

    return enriched


def upsert_documents(collection, documents: List[Dict], batch_size: int) -> None:
    for batch in chunked(documents, batch_size):
        operations = [ReplaceOne({"_id": doc["_id"]}, doc, upsert=True) for doc in batch]
        collection.bulk_write(operations, ordered=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed MongoDB Atlas collections with vector embeddings.")
    parser.add_argument("--batch-size", type=int, default=64, help="Embedding and upload batch size.")
    parser.add_argument("--dry-run", action="store_true", help="Build documents and embeddings without writing to MongoDB.")
    parser.add_argument("--reset", action="store_true", help="Delete target collections before writing.")
    args = parser.parse_args()

    import os

    mongo_uri = os.getenv("MONGODB_URI", "").strip()
    mongo_db_name = os.getenv("MONGODB_DB", "ai_onboarding").strip()
    skills_collection_name = os.getenv("ATLAS_SKILLS_COLLECTION", "skill_vectors").strip()
    occupations_collection_name = os.getenv("ATLAS_OCCUPATIONS_COLLECTION", "occupation_vectors").strip()
    courses_collection_name = os.getenv("ATLAS_COURSES_COLLECTION", "course_vectors").strip()
    embedding_model_name = os.getenv("VECTOR_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2").strip()

    skill_docs = build_skill_documents()
    occupation_docs = build_occupation_documents()
    course_docs = build_course_documents()

    print(f"Prepared {len(skill_docs)} skills, {len(occupation_docs)} occupations, and {len(course_docs)} courses.")
    print(f"Loading embedding model: {embedding_model_name}")
    model = SentenceTransformer(embedding_model_name)

    skill_docs = add_embeddings(skill_docs, model, args.batch_size)
    occupation_docs = add_embeddings(occupation_docs, model, args.batch_size)
    course_docs = add_embeddings(course_docs, model, args.batch_size)
    print("Embeddings generated.")

    if args.dry_run:
        print("Dry run complete. No MongoDB writes were performed.")
        return

    if not mongo_uri:
        raise ValueError("MONGODB_URI is required unless you use --dry-run.")

    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]

    if args.reset:
        db[skills_collection_name].delete_many({})
        db[occupations_collection_name].delete_many({})
        db[courses_collection_name].delete_many({})
        print("Cleared existing Atlas vector collections.")

    upsert_documents(db[skills_collection_name], skill_docs, args.batch_size)
    upsert_documents(db[occupations_collection_name], occupation_docs, args.batch_size)
    upsert_documents(db[courses_collection_name], course_docs, args.batch_size)

    print(f"Upserted skill vectors into '{skills_collection_name}'.")
    print(f"Upserted occupation vectors into '{occupations_collection_name}'.")
    print(f"Upserted course vectors into '{courses_collection_name}'.")


if __name__ == "__main__":
    main()

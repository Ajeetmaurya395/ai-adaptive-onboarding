import os
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

from backend.data_loader import data_loader
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

try:
    import chromadb
    from chromadb.utils import embedding_functions
except Exception:  # pragma: no cover - optional dependency at runtime
    chromadb = None
    embedding_functions = None


class VectorService:
    def __init__(self, persist_directory: str = "data/chroma_db"):
        project_root = Path(__file__).resolve().parents[1]
        try:
            self.persist_directory = str(data_loader.get_directory_path("chroma_db"))
        except Exception:
            self.persist_directory = str(project_root / persist_directory)

        self.vector_backend = os.getenv("VECTOR_BACKEND", "auto").strip().lower()
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017").strip()
        self.mongodb_db = os.getenv("MONGODB_DB", "ai_onboarding").strip()
        self.embedding_model_name = os.getenv("VECTOR_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2").strip()
        self.vector_field = os.getenv("ATLAS_VECTOR_FIELD", "embedding").strip()
        self.num_candidates_multiplier = int(os.getenv("ATLAS_VECTOR_NUM_CANDIDATES_MULTIPLIER", "20"))

        self.atlas_skills_collection = os.getenv("ATLAS_SKILLS_COLLECTION", "skill_vectors").strip()
        self.atlas_skills_index = os.getenv("ATLAS_SKILLS_INDEX", "skills_vector_index").strip()
        self.atlas_skills_text_field = os.getenv("ATLAS_SKILLS_TEXT_FIELD", "canonical").strip()

        self.atlas_occupations_collection = os.getenv("ATLAS_OCCUPATIONS_COLLECTION", "occupation_vectors").strip()
        self.atlas_occupations_index = os.getenv("ATLAS_OCCUPATIONS_INDEX", "occupations_vector_index").strip()
        self.atlas_occupations_text_field = os.getenv("ATLAS_OCCUPATIONS_TEXT_FIELD", "title").strip()

        self.atlas_courses_collection = os.getenv("ATLAS_COURSES_COLLECTION", "course_vectors").strip()
        self.atlas_courses_index = os.getenv("ATLAS_COURSES_INDEX", "courses_vector_index").strip()
        self.atlas_courses_text_field = os.getenv("ATLAS_COURSES_TEXT_FIELD", "title").strip()

        self.mongo_client: Optional[MongoClient] = None
        self.mongo_db = None
        self.embedding_model: Optional[SentenceTransformer] = None

        self.client = None
        self.embedding_fn = None
        self.onet_skills = None
        self.onet_occupations = None
        self.course_catalog = None
        self.chroma_error = None
        self.atlas_error = None

        self.skill_aliases = {
            "aws": "AWS",
            "cloud formation": "CloudFormation",
            "cloudformation": "CloudFormation",
            "github actions": "CI/CD",
            "gitlab ci": "CI/CD",
            "ci/cd": "CI/CD",
            "cicd": "CI/CD",
            "microservices architecture": "Microservices",
            "technical communication": "Communication",
            "mentoring": "Leadership",
        }
        self.skill_lookup = data_loader.load_json("skill_lookup.json", {})
        self.course_data = data_loader.load_json("course_catalog.json", {}).get("courses", [])
        self._init_chroma()

    def _normalize(self, text: str) -> str:
        return " ".join((text or "").strip().lower().split())

    def _score(self, left: str, right: str) -> float:
        return SequenceMatcher(None, self._normalize(left), self._normalize(right)).ratio()

    def _local_skill_candidates(self, skill_text: str, n_results: int = 5) -> List[Dict]:
        query = self._normalize(skill_text)
        if not query:
            return []

        alias = self.skill_aliases.get(query)
        if alias:
            return [{"id": query, "canonical": alias, "distance": 0.0, "source": "local"}]

        exact = self.skill_lookup.get(query)
        if exact:
            return [{
                "id": query,
                "canonical": exact.get("canonical", skill_text),
                "distance": 0.0,
                "source": "local",
            }]

        direct_catalog_match = []
        for course in self.course_data:
            course_skill = course.get("skill", "")
            if self._normalize(course_skill) == query:
                direct_catalog_match.append({
                    "id": query,
                    "canonical": course_skill,
                    "distance": 0.0,
                    "source": "catalog",
                })
        if direct_catalog_match:
            return direct_catalog_match[:n_results]

        candidates = []
        catalog_skills = {course.get("skill", "") for course in self.course_data}
        for candidate in list(self.skill_lookup.keys()) + list(catalog_skills):
            if not candidate:
                continue
            score = self._score(skill_text, candidate)
            if query in self._normalize(candidate) or self._normalize(candidate) in query:
                score = max(score, 0.92)
            if score >= 0.55:
                lookup = self.skill_lookup.get(self._normalize(candidate), {})
                canonical = lookup.get("canonical") or candidate
                candidates.append({
                    "id": self._normalize(candidate),
                    "canonical": canonical,
                    "distance": round(1 - score, 4),
                    "source": "local-fuzzy",
                })

        candidates.sort(key=lambda item: item["distance"])
        return candidates[:n_results]

    def _atlas_allowed(self) -> bool:
        return self.vector_backend in {"atlas", "auto"}

    def _chroma_allowed(self) -> bool:
        return self.vector_backend in {"local", "chroma", "auto"}

    def _init_chroma(self) -> None:
        if not self._chroma_allowed():
            self.chroma_error = "chromadb disabled by VECTOR_BACKEND"
            return

        if chromadb is None or embedding_functions is None:
            self.chroma_error = "chromadb dependency unavailable"
            return

        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.onet_skills = self.client.get_collection(
                name="onet_skills", embedding_function=self.embedding_fn
            )
            self.onet_occupations = self.client.get_collection(
                name="onet_occupations", embedding_function=self.embedding_fn
            )
            self.course_catalog = self.client.get_collection(
                name="course_catalog", embedding_function=self.embedding_fn
            )
        except Exception as exc:
            self.client = None
            self.embedding_fn = None
            self.onet_skills = None
            self.onet_occupations = None
            self.course_catalog = None
            self.chroma_error = str(exc)
            print(f"⚠️ ChromaDB unavailable, using fallback: {exc}")

    def _get_embedding_model(self) -> SentenceTransformer:
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
        return self.embedding_model

    def _embed_text(self, text: str) -> List[float]:
        model = self._get_embedding_model()
        vector = model.encode(text or "", normalize_embeddings=True)
        return vector.tolist()

    def _get_mongo_db(self):
        if not self._atlas_allowed():
            return None
        if self.mongo_db is not None:
            return self.mongo_db
        try:
            self.mongo_client = MongoClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                socketTimeoutMS=10000,
                connectTimeoutMS=10000,
                retryWrites=True,
                retryReads=True,
            )
            self.mongo_db = self.mongo_client[self.mongodb_db]
            return self.mongo_db
        except Exception as exc:
            self.atlas_error = str(exc)
            return None

    def _atlas_vector_search(
        self,
        collection_name: str,
        index_name: str,
        query_text: str,
        n_results: int,
    ) -> List[Dict]:
        db = self._get_mongo_db()
        if db is None:
            return []

        try:
            query_vector = self._embed_text(query_text)
            num_candidates = max(n_results * self.num_candidates_multiplier, n_results)
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": index_name,
                        "path": self.vector_field,
                        "queryVector": query_vector,
                        "numCandidates": num_candidates,
                        "limit": n_results,
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "canonical": 1,
                        "title": 1,
                        "metadata": 1,
                        "score": {"$meta": "vectorSearchScore"},
                    }
                },
            ]
            return list(db[collection_name].aggregate(pipeline))
        except Exception as exc:
            self.atlas_error = str(exc)
            print(f"⚠️ Atlas Vector Search unavailable, using fallback: {exc}")
            return []

    def _format_distance(self, score: float) -> float:
        bounded_score = max(0.0, min(score, 1.0))
        return round(1 - bounded_score, 4)

    def _atlas_skill_results(self, skill_text: str, n_results: int) -> List[Dict]:
        docs = self._atlas_vector_search(
            collection_name=self.atlas_skills_collection,
            index_name=self.atlas_skills_index,
            query_text=skill_text,
            n_results=n_results,
        )
        output = []
        for doc in docs:
            canonical = doc.get("canonical") or doc.get("title") or skill_text
            score = float(doc.get("score", 0.0) or 0.0)
            output.append({
                "id": str(doc.get("_id", canonical)),
                "canonical": canonical,
                "distance": self._format_distance(score),
                "source": "atlas_vector_search",
                "similarity_score": round(score, 4),
            })
        return output

    def _atlas_occupation_results(self, role_title: str, n_results: int = 1) -> List[Dict]:
        docs = self._atlas_vector_search(
            collection_name=self.atlas_occupations_collection,
            index_name=self.atlas_occupations_index,
            query_text=role_title,
            n_results=n_results,
        )
        output = []
        for doc in docs:
            title = doc.get("title") or doc.get("canonical") or role_title
            score = float(doc.get("score", 0.0) or 0.0)
            output.append({
                "id": str(doc.get("_id", title)),
                "title": title,
                "distance": self._format_distance(score),
                "source": "atlas_vector_search",
                "similarity_score": round(score, 4),
            })
        return output

    def _atlas_course_results(self, skill: str, n_results: int) -> List[Dict]:
        docs = self._atlas_vector_search(
            collection_name=self.atlas_courses_collection,
            index_name=self.atlas_courses_index,
            query_text=skill,
            n_results=n_results,
        )
        output = []
        for doc in docs:
            title = doc.get("title") or doc.get("canonical") or skill
            metadata = doc.get("metadata") or {}
            score = float(doc.get("score", 0.0) or 0.0)
            output.append({
                "id": str(doc.get("_id", title)),
                "title": title,
                "metadata": metadata,
                "distance": self._format_distance(score),
                "source": "atlas_vector_search",
                "similarity_score": round(score, 4),
            })
        return output

    def _chroma_skill_results(self, skill_text: str, n_results: int) -> List[Dict]:
        if self.onet_skills is None:
            return []
        try:
            results = self.onet_skills.query(query_texts=[skill_text], n_results=n_results)
            output = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    output.append({
                        "id": results["ids"][0][i],
                        "canonical": results["documents"][0][i],
                        "distance": results["distances"][0][i],
                        "source": "chromadb",
                    })
            return output
        except Exception as exc:
            print(f"⚠️ Chroma skill lookup failed, using fallback: {exc}")
            return []

    def _chroma_occupation_result(self, role_title: str) -> Optional[Dict]:
        if self.onet_occupations is None:
            return None
        try:
            results = self.onet_occupations.query(query_texts=[role_title], n_results=1)
            if results["ids"] and results["ids"][0]:
                return {
                    "id": results["ids"][0][0],
                    "title": results["documents"][0][0],
                    "distance": results["distances"][0][0],
                    "source": "chromadb",
                }
        except Exception as exc:
            print(f"⚠️ Chroma occupation lookup failed, using fallback: {exc}")
        return None

    def _chroma_course_results(self, skill: str, n_results: int) -> List[Dict]:
        if self.course_catalog is None:
            return []
        try:
            results = self.course_catalog.query(query_texts=[skill], n_results=n_results)
            output = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    output.append({
                        "id": results["ids"][0][i],
                        "title": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                        "source": "chromadb",
                    })
            return output
        except Exception as exc:
            print(f"⚠️ Chroma course lookup failed, using fallback: {exc}")
            return []

    def get_nearest_skills(self, skill_text: str, n_results: int = 5) -> List[Dict]:
        """Find O*NET-normalized skills using Atlas first, then Chroma, then local fallback."""
        local_matches = self._local_skill_candidates(skill_text, n_results=n_results)
        if local_matches and local_matches[0]["distance"] <= 0.15:
            return local_matches

        atlas_matches = self._atlas_skill_results(skill_text, n_results)
        if atlas_matches:
            return atlas_matches

        chroma_matches = self._chroma_skill_results(skill_text, n_results)
        if chroma_matches and chroma_matches[0]["distance"] < 0.35:
            return chroma_matches

        return local_matches

    def get_nearest_occupation(self, role_title: str) -> Optional[Dict]:
        """Find O*NET occupation for a role title."""
        atlas_matches = self._atlas_occupation_results(role_title, n_results=1)
        if atlas_matches:
            return atlas_matches[0]

        chroma_match = self._chroma_occupation_result(role_title)
        if chroma_match:
            return chroma_match
        return None

    def get_relevant_courses(self, skill: str, n_results: int = 1) -> List[Dict]:
        """Find courses for a missing skill."""
        atlas_matches = self._atlas_course_results(skill, n_results)
        if atlas_matches:
            return atlas_matches

        chroma_matches = self._chroma_course_results(skill, n_results)
        if chroma_matches:
            return chroma_matches

        resolved_skill = self.skill_aliases.get(self._normalize(skill), skill)
        output = []
        for course in self.course_data:
            course_skill = course.get("skill", "")
            title = course.get("title", "")
            score = max(self._score(resolved_skill, course_skill), self._score(resolved_skill, title))
            if self._normalize(resolved_skill) in self._normalize(course_skill):
                score = max(score, 0.96)
            if score >= 0.45:
                output.append({
                    "id": course.get("id", self._normalize(title)),
                    "title": title,
                    "metadata": course,
                    "distance": round(1 - score, 4),
                    "source": "catalog",
                })

        output.sort(key=lambda item: item["distance"])
        return output[:n_results]


vector_service = VectorService()

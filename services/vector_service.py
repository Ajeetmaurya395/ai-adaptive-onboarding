import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

try:
    import chromadb
    from chromadb.utils import embedding_functions
except Exception:  # pragma: no cover - optional dependency at runtime
    chromadb = None
    embedding_functions = None

class VectorService:
    def __init__(self, persist_directory: str = "data/chroma_db"):
        project_root = Path(__file__).resolve().parents[1]
        self.persist_directory = str(project_root / persist_directory)
        self.client = None
        self.embedding_fn = None
        self.onet_skills = None
        self.onet_occupations = None
        self.course_catalog = None
        self.chroma_error = None
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
        self.skill_lookup = self._load_json(project_root / "data" / "skill_lookup.json")
        self.course_data = self._load_json(project_root / "data" / "course_catalog.json").get("courses", [])
        self._init_chroma()

    def _load_json(self, path: Path) -> Dict:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

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

    def _init_chroma(self) -> None:
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
            print(f"⚠️ ChromaDB unavailable, using JSON fallback: {exc}")

    def get_nearest_skills(self, skill_text: str, n_results: int = 5) -> List[Dict]:
        """Find O*NET normalized skills."""
        local_matches = self._local_skill_candidates(skill_text, n_results=n_results)
        if local_matches and local_matches[0]["distance"] <= 0.15:
            return local_matches

        if self.onet_skills is not None:
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
                if output and output[0]["distance"] < 0.35:
                    return output
            except Exception as exc:
                print(f"⚠️ Chroma skill lookup failed, using fallback: {exc}")

        return local_matches

    def get_nearest_occupation(self, role_title: str) -> Optional[Dict]:
        """Find O*NET occupation for a role title."""
        if self.onet_occupations is not None:
            try:
                results = self.onet_occupations.query(query_texts=[role_title], n_results=1)
                if results["ids"] and results["ids"][0]:
                    return {
                        "id": results["ids"][0][0],
                        "title": results["documents"][0][0],
                        "distance": results["distances"][0][0]
                    }
            except Exception as exc:
                print(f"⚠️ Chroma occupation lookup failed, using fallback: {exc}")
        return None

    def get_relevant_courses(self, skill: str, n_results: int = 1) -> List[Dict]:
        """Find courses for a missing skill."""
        if self.course_catalog is not None:
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
                if output:
                    return output
            except Exception as exc:
                print(f"⚠️ Chroma course lookup failed, using fallback: {exc}")

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

# Singleton instance
vector_service = VectorService()

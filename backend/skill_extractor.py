"""
Dataset-grounded skill extraction with optional LLM refinement.
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from backend.data_loader import data_loader
from services.llm_service import llm


class SkillExtractor:
    """Extract and normalize skills using local datasets first, then LLM refinement."""

    SKILL_SYNONYMS = {
        "Python": ["py", "python3", "python programming"],
        "JavaScript": ["js", "ecmascript", "node.js", "nodejs"],
        "SQL": ["mysql", "postgresql", "database querying", "structured query language"],
        "AWS": ["amazon web services", "aws ec2", "aws s3", "aws lambda"],
        "Docker": ["containerization", "docker engine", "docker compose"],
        "Kubernetes": ["k8s", "kubernetes orchestration", "k8s cluster"],
        "React": ["react.js", "reactjs", "react framework"],
        "Machine Learning": ["ml", "machine-learning", "statistical modeling"],
        "Communication": ["verbal communication", "written communication", "presentation skills"],
        "Leadership": ["team leadership", "people management", "mentoring"],
        "CI/CD": ["github actions", "gitlab ci", "continuous integration", "continuous delivery", "continuous deployment", "ci cd", "cicd"],
        "CloudFormation": ["cloud formation", "aws cloudformation"],
        "Microservices": ["microservices architecture", "microservice architecture"],
    }

    EXCLUDE_PATTERNS = [
        r"\b(ms\s*word|excel|powerpoint|office)\b",
        r"\b(internet|email|web\s*browsing)\b",
        r"\b(team\s*player|hard\s*working|fast\s*learner)\b",
    ]

    def __init__(self, taxonomy_path: Optional[str] = None):
        self.project_root = Path(__file__).resolve().parents[1]
        if taxonomy_path:
            taxonomy_candidate = Path(taxonomy_path)
            resolved_taxonomy = (
                taxonomy_candidate
                if taxonomy_candidate.exists()
                else data_loader.get_file_path(taxonomy_candidate.name)
            )
        else:
            resolved_taxonomy = data_loader.get_file_path("skill_taxonomy.json")
        self.taxonomy = self._load_json(resolved_taxonomy)
        self.skill_lookup = data_loader.load_json("skill_lookup.json", {})
        self.course_catalog = data_loader.load_json("course_catalog.json", {})
        self.onet_tools = data_loader.load_json("onet_tech_skills.json", {})
        self.known_skills = self._build_known_skills()
        self._sorted_skill_keys = sorted(self.known_skills.keys(), key=len, reverse=True)

    def _load_json(self, path: Path) -> Dict:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _normalize_key(self, text: str) -> str:
        lowered = (text or "").lower().strip()
        lowered = lowered.replace("&", " and ")
        lowered = lowered.replace("/", " ")
        lowered = re.sub(r"[^a-z0-9\+\#\.\-\s]", " ", lowered)
        lowered = re.sub(r"\s+", " ", lowered).strip()
        return lowered

    def _canonical_title(self, skill: str) -> str:
        normalized = self._normalize_key(skill)
        for canonical, variants in self.SKILL_SYNONYMS.items():
            if normalized == self._normalize_key(canonical):
                return canonical
            if normalized in {self._normalize_key(variant) for variant in variants}:
                return canonical
        return (skill or "").strip()

    def _build_known_skills(self) -> Dict[str, str]:
        known: Dict[str, str] = {}

        def register(raw_skill: str, canonical: Optional[str] = None) -> None:
            canonical_value = (canonical or raw_skill or "").strip()
            normalized = self._normalize_key(raw_skill)
            if not normalized or len(normalized) < 2:
                return
            known[normalized] = canonical_value

        for category_skills in self.taxonomy.get("categories", {}).values():
            for skill in category_skills:
                register(skill, self._canonical_title(skill))

        for key, value in self.skill_lookup.items():
            canonical = value.get("canonical", key)
            register(key, canonical)
            register(canonical, canonical)

        for course in self.course_catalog.get("courses", []):
            skill = course.get("skill")
            if skill:
                canonical = self._canonical_title(skill)
                register(skill, canonical)
                register(canonical, canonical)

        for tool_list in self.onet_tools.values():
            for tool in tool_list:
                tool_name = tool.get("tool")
                if tool_name:
                    register(tool_name, self._canonical_title(tool_name))

        for canonical, variants in self.SKILL_SYNONYMS.items():
            register(canonical, canonical)
            for variant in variants:
                register(variant, canonical)

        return known

    def _is_valid_skill(self, skill: str) -> bool:
        normalized = self._normalize_key(skill)
        if len(normalized) < 2 or len(normalized) > 80:
            return False
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                return False
        return True

    def _dedupe_preserve_order(self, skills: List[str]) -> List[str]:
        seen = set()
        ordered = []
        for skill in skills:
            canonical = self._canonical_title(skill)
            key = canonical.lower()
            if key in seen or not self._is_valid_skill(canonical):
                continue
            seen.add(key)
            ordered.append(canonical)
        return ordered

    def _find_dataset_skills(self, text: str) -> List[str]:
        normalized_text = f" {self._normalize_key(text)} "
        found = []
        for phrase in self._sorted_skill_keys:
            if len(found) >= 25:
                break
            if f" {phrase} " not in normalized_text:
                continue
            canonical = self.known_skills.get(phrase, phrase)
            found.append(canonical)
        return self._dedupe_preserve_order(found)

    def _infer_experience_years(self, text: str) -> int:
        matches = re.findall(r"(\d+)\+?\s+years?", text, flags=re.IGNORECASE)
        if not matches:
            return 0
        return max(int(value) for value in matches)

    def extract_from_text(self, text: str, context: str = "resume") -> Dict:
        if not text or len(text.strip()) < 20:
            return {"skills": [], "confidence": 0.0, "source": "empty_input", "count": 0}

        dataset_skills = self._find_dataset_skills(text)
        truncated = text[:4000]

        if context == "resume":
            system_prompt = (
                "You extract professional skills from resumes. "
                "Return ONLY valid JSON with a 'skills' array. "
                "Prefer grounded technical, domain, and leadership skills."
            )
        else:
            system_prompt = (
                "You extract job requirement skills from job descriptions. "
                "Return ONLY valid JSON with a 'skills' array. "
                "Prefer explicit requirements and strongly implied stack skills."
            )

        candidates_block = ", ".join(dataset_skills[:40]) if dataset_skills else "None"
        user_prompt = (
            f"Analyze this {context} text.\n"
            f"Grounded candidate skills from local datasets: {candidates_block}\n\n"
            f"{truncated}"
        )

        raw_result = llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_type="json",
        )

        llm_skills = raw_result.get("skills", []) if isinstance(raw_result, dict) else []
        processed_llm = self._dedupe_preserve_order([skill for skill in llm_skills if isinstance(skill, str)])
        combined = self._dedupe_preserve_order(dataset_skills + processed_llm)

        if not combined:
            combined = dataset_skills

        if processed_llm and dataset_skills:
            source = "llm+dataset"
            confidence = 0.94
        elif processed_llm:
            source = "llm"
            confidence = 0.88
        elif dataset_skills:
            source = "dataset"
            confidence = 0.72
        else:
            source = "fallback"
            confidence = 0.3

        return {
            "skills": combined[:20],
            "confidence": confidence,
            "source": source,
            "count": len(combined[:20]),
            "experience_years": self._infer_experience_years(text) if context == "resume" else None,
        }


skill_extractor = SkillExtractor()

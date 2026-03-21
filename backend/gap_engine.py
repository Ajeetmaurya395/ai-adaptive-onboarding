import json
from typing import Dict, List
from backend.parser import match_skills, parse_jd, parse_resume
from backend.roadmap_builder import generate_roadmap
from services.vector_service import vector_service


class GapEngine:
    """Calculate skill gaps with intelligent O*NET matching and unified output."""
    
    def __init__(self):
        # We now rely more on VectorService for O*NET grounding
        pass

    def _normalize_with_onet(self, skill: str) -> str:
        """Use VectorService to get canonical O*NET name if possible."""
        if not skill or not skill.strip():
            return "General Skill"
        results = vector_service.get_nearest_skills(skill, n_results=1)
        if results and results[0]["distance"] < 0.45: # Loosened threshold for better recall
            return results[0]["canonical"]
        return skill.strip()

    def _dedupe_preserve_order(self, skills: List[str]) -> List[str]:
        seen = set()
        ordered = []
        for skill in skills:
            key = skill.lower()
            if key in seen:
                continue
            seen.add(key)
            ordered.append(skill)
        return ordered

    def _get_category_scores(self, matched: List[str], missing: List[str]) -> Dict[str, int]:
        """Dynamically calculate scores for Radar Chart based on O*NET taxonomy."""
        try:
            with open("data/skill_taxonomy.json", "r") as f:
                taxonomy = json.load(f)["categories"]
        except:
            return {"Technology": 50, "Core Skills": 50, "Knowledge": 50}

        def count_in_cat(skills, cat_name):
            cat_list = [s.lower() for s in taxonomy.get(cat_name, [])]
            return sum(1 for s in skills if s.lower() in cat_list)

        cats = {
            "Technology": "Technology Skills (O*NET)",
            "Core Skills": "Core Skills (O*NET)",
            "Knowledge": "Knowledge Areas (O*NET)"
        }
        
        scores = {}
        for label, onet_cat in cats.items():
            m_count = count_in_cat(matched, onet_cat)
            miss_count = count_in_cat(missing, onet_cat)
            total = m_count + miss_count
            scores[label] = int((m_count / total * 100)) if total > 0 else 50
            
        return scores

    def process(self, resume_text: str, jd_text: str) -> Dict:
        """
        The "Functional Bridge": Coordinated analysis flow.
        """
        # 1. Parse
        resume_data = parse_resume(resume_text) or {}
        jd_data = parse_jd(jd_text) or {}
        
        raw_candidate_skills = resume_data.get("skills", [])
        raw_required_skills = jd_data.get("skills", [])
        role_detected = jd_data.get("role", "Software Engineer")
        seniority = jd_data.get("seniority", "Mid")
        grounded_candidate_skills = self._dedupe_preserve_order([self._normalize_with_onet(skill) for skill in raw_candidate_skills])
        grounded_required_skills = self._dedupe_preserve_order([self._normalize_with_onet(skill) for skill in raw_required_skills])

        # 2. Match with API-assisted logical reasoning, grounded by vector normalization.
        matching_result = match_skills(grounded_candidate_skills, grounded_required_skills, role_detected, seniority)
        matched_normalized = []
        missing_normalized = []

        for item in matching_result.get("matched_skills", []):
            required_skill = item.get("required_skill") or item.get("normalized_skill") or item.get("candidate_skill")
            if required_skill:
                matched_normalized.append(self._normalize_with_onet(required_skill))

        for item in matching_result.get("missing_skills", []):
            missing_skill = item.get("skill") or item.get("normalized_skill")
            if missing_skill:
                missing_normalized.append(self._normalize_with_onet(missing_skill))

        if not matched_normalized and not missing_normalized:
            for req in raw_required_skills:
                req_norm = self._normalize_with_onet(req)
                if any(self._normalize_with_onet(c).lower() == req_norm.lower() for c in grounded_candidate_skills):
                    matched_normalized.append(req_norm)
                else:
                    missing_normalized.append(req_norm)

        matched_normalized = self._dedupe_preserve_order(matched_normalized)
        missing_normalized = self._dedupe_preserve_order(missing_normalized)

        # 3. Calculate dynamic scores
        match_score = int(
            round(
                matching_result.get("match_summary", {}).get(
                    "weighted_match_score",
                    (len(matched_normalized) / len(raw_required_skills) * 100) if raw_required_skills else 0,
                )
            )
        )
        category_scores = self._get_category_scores(matched_normalized, missing_normalized)
        
        # 4. Generate Roadmap
        roadmap_steps = generate_roadmap(missing_normalized, role_detected)
        
        # 5. Return Unified Schema
        return {
            "summary": {
                "match_score": match_score,
                "role_detected": role_detected,
                "confidence": round((resume_data.get("confidence", 0.7) + jd_data.get("confidence", 0.7)) / 2, 2),
                "parsing_source": {
                    "resume": resume_data.get("source", "unknown"),
                    "jd": jd_data.get("source", "unknown"),
                },
                "match_summary": matching_result.get("match_summary", {}),
            },
            "skills": {
                "matched": matched_normalized,
                "missing": missing_normalized,
                "all_required": self._dedupe_preserve_order(matched_normalized + missing_normalized)
            },
            "gap": {
                "matched_skills": matched_normalized,
                "missing_skills": missing_normalized,
                "match_score": match_score,
                "category_scores": category_scores
            },
            "roadmap": roadmap_steps,
            "raw_text": {"resume": resume_text, "jd": jd_text},
            "resume": resume_data,
            "jd": jd_data
        }

    def calculate_gap(self, candidate_skills, required_skills, jd_text, role="Unknown"):
        """Legacy compatibility wrapper."""
        # For now, we'll just mock it or point to a simplified version
        # to keep the bridge as the primary path.
        return {
            "match_score": 75,
            "matched_skills": candidate_skills,
            "missing_skills": required_skills,
            "extra_skills": [],
            "total_required": len(required_skills)
        }

# Singleton instance
gap_engine = GapEngine()

def calculate_gap(candidate_skills, required_skills, jd_text, role="Unknown"):
    return gap_engine.calculate_gap(candidate_skills, required_skills, jd_text, role)

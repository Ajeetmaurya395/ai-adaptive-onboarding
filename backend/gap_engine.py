"""
Skill gap calculation engine with fuzzy matching and weighting
"""
import re
from typing import List, Dict, Set, Tuple, Optional
from difflib import SequenceMatcher
from backend.schemas import GapAnalysisResult, SkillMatch, MissingSkill


class GapEngine:
    """Calculate skill gaps with intelligent matching and scoring"""
    
    # Similarity threshold for fuzzy matching
    FUZZY_THRESHOLD = 0.85
    
    # Skill category weights for scoring
    CATEGORY_WEIGHTS = {
        "core_technical": 1.0,
        "frameworks": 0.9,
        "tools": 0.8,
        "soft_skills": 0.7,
        "domain_knowledge": 0.85
    }
    
    # Priority mapping based on skill frequency in JDs
    PRIORITY_KEYWORDS = {
        "Critical": ["required", "must have", "essential", "mandatory"],
        "Important": ["preferred", "strongly desired", "highly valued"],
        "Nice-to-have": ["bonus", "plus", "nice to have", "familiarity with"]
    }
    
    def __init__(self, taxonomy: Optional[Dict] = None):
        """Initialize with optional skill taxonomy for categorization"""
        self.taxonomy = taxonomy or {}
        self._build_skill_index()
    
    def _build_skill_index(self):
        """Build reverse index for skill categorization"""
        self.skill_to_category = {}
        categories = self.taxonomy.get("categories", {})
        for category, skills in categories.items():
            for skill in skills:
                self.skill_to_category[skill.lower()] = category
    
    def _normalize(self, skill: str) -> str:
        """Normalize skill string for comparison"""
        # Lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', skill.lower().strip())
        # Remove common modifiers
        normalized = re.sub(r'\s*(proficient|experienced|familiar)\s+with\s*', '', normalized)
        normalized = re.sub(r'\s*\(\s*advanced\s*\)|\s*\+\s*|\s*expertise\s*', '', normalized)
        return normalized
    
    def _similarity_ratio(self, a: str, b: str) -> float:
        """Calculate string similarity using SequenceMatcher"""
        return SequenceMatcher(None, a, b).ratio()
    
    def _find_best_match(self, candidate_skill: str, required_skills: List[str]) -> Tuple[Optional[str], float]:
        """Find best matching required skill for a candidate skill"""
        candidate_norm = self._normalize(candidate_skill)
        best_match = None
        best_score = 0.0
        
        for required in required_skills:
            required_norm = self._normalize(required)
            
            # Exact match
            if candidate_norm == required_norm:
                return required, 1.0
            
            # Fuzzy match
            score = self._similarity_ratio(candidate_norm, required_norm)
            if score > best_score and score >= self.FUZZY_THRESHOLD:
                best_score = score
                best_match = required
        
        return best_match, best_score
    
    def _categorize_skill(self, skill: str) -> str:
        """Categorize skill using taxonomy"""
        skill_lower = skill.lower()
        
        # Check direct mapping
        if skill_lower in self.skill_to_category:
            return self.skill_to_category[skill_lower]
        
        # Heuristic categorization
        if any(kw in skill_lower for kw in ["python", "java", "sql", "aws", "docker", "react"]):
            return "core_technical"
        elif any(kw in skill_lower for kw in ["django", "flask", "spring", "express"]):
            return "frameworks"
        elif any(kw in skill_lower for kw in ["git", "jenkins", "jira", "slack"]):
            return "tools"
        elif any(kw in skill_lower for kw in ["communication", "leadership", "team"]):
            return "soft_skills"
        else:
            return "domain_knowledge"
    
    def _determine_priority(self, skill: str, jd_text: str) -> str:
        """Determine skill priority based on JD context"""
        skill_lower = skill.lower()
        jd_lower = jd_text.lower()
        
        # Check for priority keywords near skill mention
        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                # Look for keyword within 50 chars of skill
                pattern = f'.{{0,50}}{re.escape(skill_lower)}.{{0,50}}{re.escape(keyword)}'
                if re.search(pattern, jd_lower, re.IGNORECASE | re.DOTALL):
                    return priority
        
        # Default priority based on category
        category = self._categorize_skill(skill)
        if category == "core_technical":
            return "Critical"
        elif category in ["frameworks", "domain_knowledge"]:
            return "Important"
        return "Nice-to-have"
    
    def calculate_gap(
        self, 
        candidate_skills: List[str], 
        required_skills: List[str],
        jd_text: str = ""
    ) -> GapAnalysisResult:
        """
        Calculate comprehensive skill gap analysis
        
        Args:
            candidate_skills: List of skills from resume
            required_skills: List of skills from job description
            jd_text: Full JD text for context-aware priority
            
        Returns:
            GapAnalysisResult with detailed breakdown
        """
        # Normalize inputs
        candidate_norm = [self._normalize(s) for s in candidate_skills if s]
        required_norm = [self._normalize(s) for s in required_skills if s]
        
        matched: List[SkillMatch] = []
        missing: List[MissingSkill] = []
        extra: List[Dict] = []
        used_required: Set[str] = set()
        
        # Step 1: Find matches
        for c_skill in candidate_skills:
            c_norm = self._normalize(c_skill)
            best_match, confidence = self._find_best_match(c_skill, required_skills)
            
            if best_match:
                # Record match
                matched.append(SkillMatch(
                    candidate_skill=c_skill,
                    required_skill=best_match,
                    confidence=round(confidence, 2),
                    notes="Exact match" if confidence == 1.0 else f"Fuzzy match ({confidence:.0%})"
                ))
                used_required.add(self._normalize(best_match))
            else:
                # Candidate has extra skill
                category = self._categorize_skill(c_skill)
                extra.append({
                    "skill": c_skill,
                    "category": category,
                    "potential_value": f"Could enhance {category.replace('_', ' ')} capabilities"
                })
        
        # Step 2: Identify missing skills
        for r_skill in required_skills:
            r_norm = self._normalize(r_skill)
            if r_norm not in used_required:
                # Determine priority
                priority = self._determine_priority(r_skill, jd_text)
                
                # Find transferable alternatives
                transferable = []
                for c_skill in candidate_skills:
                    if self._similarity_ratio(self._normalize(c_skill), r_norm) > 0.6:
                        transferable.append(c_skill)
                
                missing.append(MissingSkill(
                    skill=r_skill,
                    priority=priority,
                    transferable_alternatives=transferable[:3],  # Top 3 alternatives
                    estimated_learning_time=self._estimate_learning_time(r_skill)
                ))
        
        # Step 3: Calculate weighted score
        total_weight = 0
        matched_weight = 0
        
        for r_skill in required_skills:
            category = self._categorize_skill(r_skill)
            weight = self.CATEGORY_WEIGHTS.get(category, 0.8)
            total_weight += weight
            
            if self._normalize(r_skill) in used_required:
                matched_weight += weight
        
        match_score = (matched_weight / total_weight * 100) if total_weight > 0 else 0
        
        # Step 4: Build result
        return GapAnalysisResult(
            match_score=round(match_score, 2),
            matched_skills=matched,
            missing_skills=missing,
            extra_skills=extra,
            total_required=len(required_skills)
        )
    
    def _estimate_learning_time(self, skill: str) -> str:
        """Estimate time to learn a skill (heuristic)"""
        skill_lower = skill.lower()
        
        # Quick wins
        if any(kw in skill_lower for kw in ["git", "slack", "jira", "agile"]):
            return "1-2 weeks"
        # Moderate complexity
        elif any(kw in skill_lower for kw in ["docker", "sql", "rest api", "linux"]):
            return "3-4 weeks"
        # Complex skills
        elif any(kw in skill_lower for kw in ["aws", "kubernetes", "machine learning", "react"]):
            return "6-8 weeks"
        # Advanced/expert level
        elif any(kw in skill_lower for kw in ["system design", "architecture", "tensorflow"]):
            return "2-3 months"
        else:
            return "4-6 weeks"  # Default
    
    def calculate_batch_gap(
        self, 
        candidates: List[Dict], 
        required_skills: List[str],
        jd_text: str = ""
    ) -> List[GapAnalysisResult]:
        """Calculate gaps for multiple candidates"""
        return [
            self.calculate_gap(
                candidate.get("skills", []),
                required_skills,
                jd_text
            )
            for candidate in candidates
        ]
    
    def get_skill_recommendations(
        self, 
        missing_skills: List[MissingSkill],
        max_recommendations: int = 5
    ) -> List[Dict]:
        """Generate prioritized learning recommendations"""
        # Sort by priority then by estimated time
        sorted_missing = sorted(
            missing_skills,
            key=lambda x: (
                {"Critical": 0, "Important": 1, "Nice-to-have": 2}.get(x.priority, 3),
                x.estimated_learning_time or "99 weeks"
            )
        )
        
        recommendations = []
        for skill in sorted_missing[:max_recommendations]:
            recommendations.append({
                "skill": skill.skill,
                "priority": skill.priority,
                "estimated_time": skill.estimated_learning_time,
                "start_with": skill.transferable_alternatives[0] if skill.transferable_alternatives else None,
                "action": f"Focus on {skill.skill} through structured learning"
            })
        
        return recommendations


# Singleton instance
gap_engine = GapEngine()


def calculate_gap(candidate_skills: List[str], required_skills: List[str], jd_text: str = "") -> Dict:
    """
    Backward-compatible wrapper used by Streamlit pages.
    Returns a dict with simple list fields expected by the UI layer.
    """
    result = gap_engine.calculate_gap(candidate_skills, required_skills, jd_text)
    return {
        "match_score": result.match_score,
        "matched_skills": [match.required_skill for match in result.matched_skills],
        "missing_skills": [item.skill for item in result.missing_skills],
        "extra_skills": result.extra_skills,
        "total_required": result.total_required,
    }

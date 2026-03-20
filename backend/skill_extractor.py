"""
Dedicated skill extraction module with normalization and validation
"""
import re
import json
from typing import List, Dict, Optional
from services.llm_service import llm


class SkillExtractor:
    """Extract and normalize skills from text using LLM + rule-based fallbacks"""
    
    # Common skill synonyms for normalization
    SKILL_SYNONYMS = {
        "python": ["py", "python3", "python programming"],
        "javascript": ["js", "ecmascript", "node.js", "nodejs"],
        "sql": ["mysql", "postgresql", "database querying", "sql programming"],
        "aws": ["amazon web services", "ec2", "s3", "lambda", "cloudformation"],
        "docker": ["containerization", "docker engine", "docker compose"],
        "kubernetes": ["k8s", "kubernetes orchestration", "k8s cluster"],
        "react": ["react.js", "reactjs", "react framework"],
        "machine learning": ["ml", "machine-learning", "statistical modeling"],
        "communication": ["verbal communication", "written communication", "presentation skills"],
        "leadership": ["team leadership", "people management", "mentoring"],
    }
    
    # Skills to exclude (too generic)
    EXCLUDE_PATTERNS = [
        r'\b(ms\s*word|excel|powerpoint|office)\b',
        r'\b(internet|email|web\s*browsing)\b',
        r'\b(team\s*player|hard\s*working|fast\s*learner)\b',
    ]
    
    def __init__(self, taxonomy_path: Optional[str] = None):
        """Initialize with optional skill taxonomy for validation"""
        self.taxonomy = self._load_taxonomy(taxonomy_path) if taxonomy_path else {}
    
    def _load_taxonomy(self, path: str) -> Dict:
        """Load skill taxonomy JSON for validation"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill name to canonical form"""
        skill_lower = skill.lower().strip()
        
        # Check synonyms
        for canonical, variants in self.SKILL_SYNONYMS.items():
            if skill_lower == canonical or skill_lower in variants:
                return canonical.title()
        
        # Basic cleanup
        normalized = re.sub(r'[^a-zA-Z0-9\s\.\+\-#]', '', skill_lower)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized.title() if normalized else skill
    
    def _is_valid_skill(self, skill: str) -> bool:
        """Filter out invalid or too-generic skills"""
        skill_lower = skill.lower()
        
        # Too short or too long
        if len(skill_lower) < 2 or len(skill_lower) > 50:
            return False
        
        # Check exclusion patterns
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, skill_lower, re.IGNORECASE):
                return False
        
        # Check against taxonomy if available
        if self.taxonomy:
            categories = self.taxonomy.get("categories", {})
            all_valid = [s.lower() for cat in categories.values() for s in cat]
            if skill_lower not in all_valid and skill_lower not in [syn for variants in self.SKILL_SYNONYMS.values() for syn in variants]:
                # Allow new skills but flag for review
                pass
        
        return True
    
    def extract_from_text(self, text: str, context: str = "resume") -> Dict:
        """
        Extract skills using LLM with rule-based post-processing
        
        Args:
            text: Raw text to analyze
            context: "resume" or "jd" for context-aware extraction
            
        Returns:
            Dict with extracted skills and metadata
        """
        if not text or len(text.strip()) < 20:
            return {"skills": [], "confidence": 0.0, "source": "empty_input"}
        
        # Truncate to avoid token limits
        truncated = text[:4000]
        
        # Choose prompt based on context
        if context == "resume":
            system_prompt = """You are a precise skill extraction engine. 
            Output ONLY valid JSON with key "skills" containing a list of skill strings.
            Focus on technical skills, tools, frameworks, and professional competencies.
            Exclude generic terms like "communication" unless clearly emphasized."""
        else:  # jd
            system_prompt = """You are a job requirements analyzer.
            Output ONLY valid JSON with key "skills" containing required skill strings.
            Include must-have and nice-to-have skills. Be specific about tools/technologies."""
        
        user_prompt = f"Extract skills from this {context}:\n\n{truncated}"
        
        # Call LLM
        raw_result = llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_type="json"
        )
        
        # Parse and validate results
        skills = raw_result.get("skills", []) if isinstance(raw_result, dict) else []
        
        # Post-process: normalize and filter
        processed = []
        for skill in skills:
            if isinstance(skill, str) and self._is_valid_skill(skill):
                normalized = self._normalize_skill(skill)
                if normalized not in processed:  # Deduplicate
                    processed.append(normalized)
        
        # Fallback: rule-based extraction if LLM fails
        if not processed:
            processed = self._rule_based_extract(text, context)
        
        return {
            "skills": processed,
            "confidence": 0.9 if processed else 0.3,
            "source": "llm" if processed else "fallback",
            "count": len(processed)
        }
    
    def _rule_based_extract(self, text: str, context: str) -> List[str]:
        """Fallback regex-based skill extraction"""
        skills = []
        text_lower = text.lower()
        
        # Extract common tech skills via keywords
        tech_keywords = [
            "python", "javascript", "java", "sql", "aws", "azure", "gcp",
            "docker", "kubernetes", "react", "angular", "vue", "node",
            "django", "flask", "tensorflow", "pytorch", "pandas", "numpy",
            "git", "linux", "bash", "rest", "graphql", "mongodb", "redis"
        ]
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                normalized = self._normalize_skill(keyword)
                if normalized not in skills:
                    skills.append(normalized)
        
        # Extract experience patterns: "X years of Y"
        exp_pattern = r'(\d+\+?\s*years?\s*(?:of\s*)?experience\s*(?:in\s*)?)([a-zA-Z\s\.\+]+)'
        for match in re.finditer(exp_pattern, text, re.IGNORECASE):
            skill_candidate = match.group(2).strip()
            if self._is_valid_skill(skill_candidate):
                normalized = self._normalize_skill(skill_candidate)
                if normalized not in skills:
                    skills.append(normalized)
        
        return skills[:15]  # Limit fallback results
    
    def batch_extract(self, documents: List[Dict]) -> List[Dict]:
        """Extract skills from multiple documents efficiently"""
        results = []
        for doc in documents:
            result = self.extract_from_text(
                text=doc.get("text", ""),
                context=doc.get("type", "resume")
            )
            result["doc_id"] = doc.get("id")
            results.append(result)
        return results


# Singleton instance
skill_extractor = SkillExtractor(taxonomy_path="data/skill_taxonomy.json")
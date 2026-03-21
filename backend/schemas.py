"""
Pydantic schemas for data validation and serialization
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from datetime import datetime
import re


# ============ AUTH SCHEMAS ============

class UserCreate(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9]+$')
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=6)

    @validator('email')
    def email_format(cls, v):
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('Password must contain both letters and numbers')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    identifier: str = Field(..., min_length=3)  # username or email
    password: str


class UserResponse(BaseModel):
    """Schema for user data (excluding password)"""
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ DOCUMENT SCHEMAS ============

class ParsedResume(BaseModel):
    """Structured resume data from LLM"""
    skills: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    summary: Optional[str] = None
    education: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    
    @validator('skills', pre=True)
    def ensure_list(cls, v):
        return v if isinstance(v, list) else []


class ParsedJD(BaseModel):
    """Structured job description data from LLM"""
    skills: List[str] = Field(default_factory=list)
    role: str = "Unknown Role"
    seniority: Optional[str] = Field(None, pattern=r'^(Junior|Mid|Senior|Lead|Principal)$')
    company: Optional[str] = None
    location: Optional[str] = None
    
    @validator('skills', pre=True)
    def ensure_list(cls, v):
        return v if isinstance(v, list) else []


# ============ GAP ANALYSIS SCHEMAS ============

class SkillMatch(BaseModel):
    """Individual skill match result"""
    candidate_skill: str
    required_skill: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    notes: Optional[str] = None


class MissingSkill(BaseModel):
    """Skill gap entry"""
    skill: str
    priority: str = Field(..., pattern=r'^(Critical|Important|Nice-to-have)$')
    transferable_alternatives: List[str] = Field(default_factory=list)
    estimated_learning_time: Optional[str] = None


class GapAnalysisResult(BaseModel):
    """Complete skill gap analysis"""
    match_score: float = Field(ge=0.0, le=100.0)
    matched_skills: List[SkillMatch] = Field(default_factory=list)
    missing_skills: List[MissingSkill] = Field(default_factory=list)
    extra_skills: List[Dict] = Field(default_factory=list)
    total_required: int
    category_scores: Dict[str, float] = Field(default_factory=dict)
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    
    @property
    def gap_percentage(self) -> float:
        """Calculate percentage of skills missing"""
        if self.total_required == 0:
            return 0.0
        return round((len(self.missing_skills) / self.total_required) * 100, 2)


# ============ ROADMAP SCHEMAS ============

class RoadmapItem(BaseModel):
    """Single learning path item"""
    skill: str
    resource: str
    resource_type: Optional[str] = Field(None, pattern=r'^(Course|Certification|Book|Project|Tutorial)$')
    duration: str  # e.g., "4 weeks"
    priority: str = Field(..., pattern=r'^(High|Medium|Low)$')
    url: Optional[str] = None
    estimated_cost: Optional[str] = None
    
    @validator('duration')
    def validate_duration_format(cls, v):
        if not re.match(r'^\d+\s*(weeks?|months?|hours?)$', v, re.IGNORECASE):
            raise ValueError('Duration must be like "4 weeks", "2 months"')
        return v


class LearningRoadmap(BaseModel):
    """Complete adaptive learning roadmap"""
    user_id: Optional[int] = None
    target_role: str
    items: List[RoadmapItem] = Field(default_factory=list)
    total_estimated_duration: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict] = None
    
    def get_by_priority(self, priority: str) -> List[RoadmapItem]:
        """Filter items by priority"""
        return [item for item in self.items if item.priority == priority]


# ============ DATABASE SCHEMAS ============

class DatabaseResult(BaseModel):
    """Stored analysis result"""
    id: Optional[int] = None
    user_id: int
    score: float = Field(ge=0.0, le=100.0)
    gap_data: Optional[Dict] = None
    created_at: datetime = Field(default_factory=datetime.now)


class DatabaseRoadmap(BaseModel):
    """Stored roadmap"""
    id: Optional[int] = None
    user_id: int
    roadmap_json: Dict  # Serialized LearningRoadmap
    created_at: datetime = Field(default_factory=datetime.now)


# ============ API REQUEST/RESPONSE SCHEMAS ============

class AnalysisRequest(BaseModel):
    """Request schema for skill analysis endpoint"""
    resume_text: str = Field(..., min_length=50)
    jd_text: str = Field(..., min_length=50)
    user_id: Optional[int] = None


class AnalysisResponse(BaseModel):
    """Response schema for analysis endpoint"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None


class EvaluationMetrics(BaseModel):
    """Schema for evaluation results"""
    accuracy: float = Field(ge=0.0, le=100.0)
    match_score: float = Field(ge=0.0, le=100.0)
    precision: float = Field(ge=0.0, le=100.0)
    recall: float = Field(ge=0.0, le=100.0)
    f1_score: float = Field(ge=0.0, le=100.0)
    skills_found: int
    skills_expected: int
    processing_time_ms: Optional[int] = None


# ============ UTILITY SCHEMAS ============

class APIError(BaseModel):
    """Standardized error response"""
    error: str
    details: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check endpoint response"""
    status: str = "healthy"
    version: str = "1.0.0"
    database: str = "connected"
    llm_service: str = "operational"
    timestamp: datetime = Field(default_factory=datetime.now)

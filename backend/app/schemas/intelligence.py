from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class IntelligenceIndicator(BaseModel):
    """Specific intelligence metric with confidence and reasoning"""
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    status: str = "reliable"  # reliable, uncertain, or insufficient_data

class SkillCredibility(BaseModel):
    """Validation of claimed skills against resume context"""
    overall_credibility: float
    validated_skills: List[str]
    unsupported_skills: List[str]
    reasoning: str

class CareerTrajectory(BaseModel):
    """Analysis of candidate's career path and role suitability"""
    progression_score: float
    role_obsolescence_risk: float
    suitability_explanation: str

class BiasAudit(BaseModel):
    """Detection of potential bias in matching results"""
    is_biased: bool
    detected_patterns: List[str]
    mitigation_applied: bool
    adjusted_score: Optional[float] = None
    audit_log: str

class MatchIntelligence(BaseModel):
    """Aggregated post-matching intelligence insights"""
    hiring_success_probability: IntelligenceIndicator
    retention_likelihood: IntelligenceIndicator
    skill_credibility: SkillCredibility
    career_trajectory: CareerTrajectory
    bias_audit: BiasAudit
    labor_market_context: Optional[str] = None

class ProfileCompleteness(BaseModel):
    """Weighted profile completeness score and breakdown"""
    overall_score: float
    breakdown: Dict[str, float]
    missing_critical_fields: List[str]
    suggestions: List[str]

class SkillGap(BaseModel):
    """Analysis of missing skills against a target"""
    skill: str
    gap_level: float # 0.0 to 1.0 (1.0 = completely missing)
    importance: str  # high, medium, low
    learning_resources: Optional[List[str]] = None

class SkillGapResponse(BaseModel):
    """Aggregated skill gap analysis"""
    target_role: str
    match_score: float
    gaps: List[SkillGap]
    recommendations: List[str]

class CareerSuggestionResponse(BaseModel):
    """AI Career path suggestion schema"""
    id: str
    title: str
    description: str
    priority: str
    category: str
    created_at: datetime


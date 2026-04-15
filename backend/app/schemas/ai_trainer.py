from pydantic import BaseModel, Field
from typing import List, Optional, Any


class TrainingRequest(BaseModel):
    job_role: str
    candidate_skills: str | List[str]
    job_skills: str | List[str]
    matched_skills: str | List[str]
    question: Optional[str] = None
    answer: Optional[str] = None
    roadmap_days: Optional[int] = 14
    quiz_type: Optional[str] = "Mixed"


class SkillAnalysis(BaseModel):
    level: str
    missing_skills: List[str]
    strengths: List[str]
    focus_areas: List[str]


class InterviewQuestion(BaseModel):
    type: str = "medium"                          # easy / medium / hard
    question: str
    cat: str = "General"                          # topic/category label
    quiz_type: str = "long_answer"               # mcq | fill_in_the_blank | long_answer
    options: List[str] = Field(default_factory=list)
    correct_answer: str = ""                      # expected answer or chosen MCQ option
    explanation: str = ""                         # shown after the user submits


class AnswerEvaluation(BaseModel):
    score: Optional[int] = None
    correctness: str = ""
    missing_points: List[str] = Field(default_factory=list)
    improvement: str = ""
    ideal_answer: str = ""


class RealWorldTask(BaseModel):
    title: str = ""
    description: str = ""
    requirements: List[str] = Field(default_factory=list)
    expected_output: str = ""
    difficulty: str = ""


class RoadmapDay(BaseModel):
    day: int
    task: str
    focus: Optional[str] = ""       # optional focus label shown on the roadmap card


class SkillProfileItem(BaseModel):
    skill: str
    confidence: str


class JobMatch(BaseModel):
    role: str
    match_score: str
    why: str


class TrainingResponse(BaseModel):
    skill_analysis: Optional[Any] = None
    questions: List[Any] = Field(default_factory=list)
    answer_evaluation: Optional[Any] = None
    tasks: List[Any] = Field(default_factory=list)
    roadmap: List[Any] = Field(default_factory=list)
    
    # Conversational Flow additions
    is_profile_complete: bool = False
    next_question: Optional[str] = None
    coach_comment: Optional[str] = None
    skill_profile: List[Any] = Field(default_factory=list)
    top_job_matches: List[Any] = Field(default_factory=list)
    career_insight: Optional[str] = None

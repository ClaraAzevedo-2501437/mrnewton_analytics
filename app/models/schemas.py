"""
Pydantic models for analytics data structures
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime


class MetricDefinition(BaseModel):
    """Definition of a single metric in the analytics contract"""
    name: str
    type: str
    description: Optional[str] = None


class AnalyticsContract(BaseModel):
    """Analytics contract defining available metrics"""
    qualitative: List[MetricDefinition]
    quantitative: List[MetricDefinition]


class QuantitativeMetrics(BaseModel):
    """Quantitative metrics for an instance"""
    total_attempts: int = Field(description="Total number of attempts across all exercises")
    total_time_seconds: int = Field(description="Total time spent in seconds")
    average_time_per_attempt: float = Field(description="Average time per attempt")
    number_of_correct_answers: int = Field(description="Number of correct answers")
    final_score: float = Field(description="Final score (0-1)")
    activity_success: bool = Field(description="Whether the activity was successful")


class QualitativeMetrics(BaseModel):
    """Qualitative metrics for an instance"""
    answer_rationale: List[str] = Field(default_factory=list, description="Student reasoning for answers")


class AnalyticsMetrics(BaseModel):
    """Complete analytics metrics for a student submission"""
    instance_id: str
    student_id: str
    metrics: QuantitativeMetrics
    qualitative: QualitativeMetrics
    calculated_at: str


# Activity component data models (for API communication)

class Answer(BaseModel):
    """Individual answer for a question"""
    selectedOption: str
    rationale: str


class AttemptResult(BaseModel):
    """Result of a single attempt"""
    attemptIndex: int
    answers: Dict[str, Answer]
    result: float
    submittedAt: str
    timeSpentSeconds: Optional[int] = None


class Submission(BaseModel):
    """Student submission with multiple attempts"""
    submissionId: str = Field(alias="submission_id")
    instanceId: str = Field(alias="instance_id")
    studentId: str = Field(alias="student_id")
    numberOfAttempts: int = Field(alias="number_of_attempts")
    attempts: List[AttemptResult]
    createdAt: str = Field(alias="created_at")

    class Config:
        populate_by_name = True


class Exercise(BaseModel):
    """Exercise definition"""
    question: str
    options: List[str]
    correct_options: str
    correct_answer: str


class ActivityConfig(BaseModel):
    """Activity configuration"""
    title: str
    grade: int
    modules: str
    number_of_exercises: int
    total_time_minutes: int
    number_of_retries: int
    relative_tolerance_pct: Optional[float] = None
    absolute_tolerance: Optional[float] = None
    show_answers_after_submission: Optional[bool] = None
    scoring_policy: Optional[str] = "linear"
    approval_threshold: Optional[float] = None
    exercises: List[Exercise]


class Activity(BaseModel):
    """Activity definition - matches Activity API response format"""
    activity_id: str = Field(alias="activity_id")
    created_at: str = Field(alias="created_at")
    title: str
    grade: int
    modules: str
    number_of_exercises: int
    total_time_minutes: int
    number_of_retries: int
    relative_tolerance_pct: Optional[float] = None
    absolute_tolerance: Optional[float] = None
    show_answers_after_submission: Optional[bool] = None
    scoring_policy: Optional[str] = "linear"
    approval_threshold: Optional[float] = None
    exercises: List[Exercise]

    class Config:
        populate_by_name = True


class DeploymentInstance(BaseModel):
    """Deployment instance"""
    instanceId: str = Field(alias="instance_id")
    activityId: str = Field(alias="activity_id")
    createdAt: str = Field(alias="created_at")
    expiresAt: Optional[str] = Field(alias="expires_at", default=None)
    sessionParams: Optional[Dict[str, Any]] = Field(alias="session_params", default=None)

    class Config:
        populate_by_name = True

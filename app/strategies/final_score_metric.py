"""
Strategy for calculating final score
"""
from typing import List
from app.strategies.analytics_metric_strategy import AnalyticsMetricStrategy
from app.strategies.correct_answers_metric import CorrectAnswersMetric
from app.models.schemas import Submission, Activity


class FinalScoreMetric(AnalyticsMetricStrategy):
    """
    Calculates the final score based on the activity's scoring policy.
    
    Supports:
    - linear: score = correct_answers / total_exercises
    - non-linear: score with penalty for multiple attempts
    """
    
    def __init__(self):
        self._correct_answers_strategy = CorrectAnswersMetric()
    
    @property
    def metric_name(self) -> str:
        return "final_score"
    
    def calculate(self, submissions: List[Submission], activity: Activity) -> float:
        """
        Calculate final score from submissions.
        
        Args:
            submissions: List of student submissions
            activity: Activity configuration with scoring policy
            
        Returns:
            Final score as a float between 0.0 and 1.0
        """
        if not submissions:
            return 0.0
        
        total_exercises = activity.number_of_exercises
        if total_exercises == 0:
            return 0.0
        
        # For single student, calculate their score
        if len(submissions) == 1:
            return self._calculate_single_score(submissions[0], activity)
        
        # For multiple students, calculate average score
        total_score = sum(
            self._calculate_single_score(submission, activity)
            for submission in submissions
        )
        return total_score / len(submissions)
    
    def _calculate_single_score(self, submission: Submission, activity: Activity) -> float:
        """
        Calculate score for a single student submission.
        """
        if not submission.attempts:
            return 0.0
        
        total_exercises = activity.number_of_exercises
        scoring_policy = activity.scoring_policy or "linear"
        
        # Count correct answers in last attempt
        correct_answers = self._correct_answers_strategy._count_correct_in_attempt(
            submission.attempts[-1],
            activity
        )
        
        if scoring_policy == "linear":
            # Simple linear scoring
            return correct_answers / total_exercises
        
        elif scoring_policy == "non-linear":
            # Non-linear scoring with penalty for retries
            base_score = correct_answers / total_exercises
            num_attempts = len(submission.attempts)
            
            # Apply penalty: reduce score by 10% for each retry beyond the first
            penalty_factor = max(0.5, 1.0 - (0.1 * (num_attempts - 1)))
            return base_score * penalty_factor
        
        else:
            # Default to linear
            return correct_answers / total_exercises

"""
Strategy for determining activity success
"""
from typing import List
from app.strategies.analytics_metric_strategy import AnalyticsMetricStrategy
from app.strategies.final_score_metric import FinalScoreMetric
from app.models.schemas import Submission, Activity


class ActivitySuccessMetric(AnalyticsMetricStrategy):
    """
    Determines whether the activity was successfully completed.
    
    Success is determined by comparing the final score against
    the activity's approval threshold.
    """
    
    def __init__(self):
        self._final_score_strategy = FinalScoreMetric()
    
    @property
    def metric_name(self) -> str:
        return "activity_success"
    
    def calculate(self, submissions: List[Submission], activity: Activity) -> bool:
        """
        Determine if activity was successful from submissions.
        
        Args:
            submissions: List of student submissions
            activity: Activity configuration with approval threshold
            
        Returns:
            True if activity was successful, False otherwise
        """
        if not submissions:
            return False
        
        # Get the approval threshold (default to 0.5 if not set)
        approval_threshold = activity.approval_threshold or 0.5
        
        # For single student, check their score
        if len(submissions) == 1:
            final_score = self._final_score_strategy._calculate_single_score(
                submissions[0],
                activity
            )
            return final_score >= approval_threshold
        
        # For multiple students, check if any student succeeded
        # (or adjust logic based on requirements)
        for submission in submissions:
            final_score = self._final_score_strategy._calculate_single_score(
                submission,
                activity
            )
            if final_score >= approval_threshold:
                return True
        
        return False

"""
Strategy for calculating total number of attempts
"""
from typing import List
from app.strategies.analytics_metric_strategy import AnalyticsMetricStrategy
from app.models.schemas import Submission, Activity


class TotalAttemptsMetric(AnalyticsMetricStrategy):
    """
    Calculates the total number of attempts across all submissions.
    
    For a single student submission, returns the count of attempts they made.
    For multiple students, returns the sum of all attempts.
    """
    
    @property
    def metric_name(self) -> str:
        return "total_attempts"
    
    def calculate(self, submissions: List[Submission], activity: Activity) -> int:
        """
        Calculate total attempts from submissions.
        
        Args:
            submissions: List of student submissions
            activity: Activity configuration (not used for this metric)
            
        Returns:
            Total number of attempts as an integer
        """
        if not submissions:
            return 0
        
        # Sum up attempts from all submissions
        total = sum(len(submission.attempts) for submission in submissions)
        return total

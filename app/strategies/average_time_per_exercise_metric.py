"""
Strategy for calculating average time per exercise/attempt
"""
from typing import List
from app.strategies.analytics_metric_strategy import AnalyticsMetricStrategy
from app.strategies.total_time_metric import TotalTimeMetric
from app.strategies.total_attempts_metric import TotalAttemptsMetric
from app.models.schemas import Submission, Activity


class AverageTimePerExerciseMetric(AnalyticsMetricStrategy):
    """
    Calculates the average time spent per attempt.
    
    This is computed as total_time / total_attempts.
    """
    
    def __init__(self):
        self._total_time_strategy = TotalTimeMetric()
        self._total_attempts_strategy = TotalAttemptsMetric()
    
    @property
    def metric_name(self) -> str:
        return "average_time_per_attempt"
    
    def calculate(self, submissions: List[Submission], activity: Activity) -> float:
        """
        Calculate average time per attempt from submissions.
        
        Args:
            submissions: List of student submissions
            activity: Activity configuration
            
        Returns:
            Average time per attempt in seconds as a float
        """
        if not submissions:
            return 0.0
        
        # Calculate using other strategies
        total_time = self._total_time_strategy.calculate(submissions, activity)
        total_attempts = self._total_attempts_strategy.calculate(submissions, activity)
        
        if total_attempts == 0:
            return 0.0
        
        return total_time / total_attempts

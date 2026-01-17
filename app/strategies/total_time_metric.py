"""
Strategy for calculating total time spent on activity
"""
from typing import List
from datetime import datetime
from app.strategies.analytics_metric_strategy import AnalyticsMetricStrategy
from app.models.schemas import Submission, Activity


class TotalTimeMetric(AnalyticsMetricStrategy):
    """
    Calculates the total time spent on an activity in seconds.
    
    Uses timeSpentSeconds from attempts if available, otherwise calculates
    from timestamps between first and last attempt.
    """
    
    @property
    def metric_name(self) -> str:
        return "total_time_seconds"
    
    def calculate(self, submissions: List[Submission], activity: Activity) -> int:
        """
        Calculate total time spent from submissions.
        
        Args:
            submissions: List of student submissions
            activity: Activity configuration with time limits
            
        Returns:
            Total time in seconds as an integer
        """
        if not submissions:
            return 0
        
        total_time = 0
        
        for submission in submissions:
            total_time += self._calculate_submission_time(submission, activity)
        
        return total_time
    
    def _calculate_submission_time(self, submission: Submission, activity: Activity) -> int:
        """
        Calculate time for a single submission.
        """
        if not submission.attempts or len(submission.attempts) == 0:
            return 0
        
        # If attempts have timeSpentSeconds, sum them up
        if all(attempt.timeSpentSeconds is not None for attempt in submission.attempts):
            return sum(attempt.timeSpentSeconds for attempt in submission.attempts)
        
        # Fallback: calculate from timestamps
        try:
            # If only one attempt, return 0 since we can't calculate duration
            if len(submission.attempts) == 1:
                return 0
            
            # Parse timestamps for first and last attempts
            first_submitted = datetime.fromisoformat(
                submission.attempts[0].submittedAt.replace("Z", "+00:00")
            )
            last_submitted = datetime.fromisoformat(
                submission.attempts[-1].submittedAt.replace("Z", "+00:00")
            )
            
            # Calculate difference in seconds
            time_diff = (last_submitted - first_submitted).total_seconds()
            time_diff = max(0, time_diff)
            
            # Cap at activity's total time limit if configured
            max_time = activity.total_time_minutes * 60
            return min(int(time_diff), max_time) if max_time > 0 else int(time_diff)
        
        except Exception:
            # Fallback: estimate based on average
            return activity.total_time_minutes * 60

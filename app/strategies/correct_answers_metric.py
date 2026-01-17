"""
Strategy for calculating number of correct answers
"""
from typing import List
from app.strategies.analytics_metric_strategy import AnalyticsMetricStrategy
from app.models.schemas import Submission, Activity, AttemptResult


class CorrectAnswersMetric(AnalyticsMetricStrategy):
    """
    Calculates the number of correct answers in the last attempt.
    
    A question is considered correct if the selected option matches
    the correct option defined in the activity configuration.
    """
    
    @property
    def metric_name(self) -> str:
        return "number_of_correct_answers"
    
    def calculate(self, submissions: List[Submission], activity: Activity) -> int:
        """
        Calculate number of correct answers from submissions.
        
        Args:
            submissions: List of student submissions
            activity: Activity configuration with correct answers
            
        Returns:
            Number of correct answers as an integer
        """
        if not submissions:
            return 0
        
        total_correct = 0
        
        for submission in submissions:
            if submission.attempts:
                # Get the last (most recent) attempt for each student
                last_attempt = submission.attempts[-1]
                total_correct += self._count_correct_in_attempt(last_attempt, activity)
        
        return total_correct
    
    def _count_correct_in_attempt(self, attempt: AttemptResult, activity: Activity) -> int:
        """
        Count the number of correct answers in a single attempt.
        """
        correct_count = 0
        exercises = activity.exercises
        
        for question_id, answer in attempt.answers.items():
            try:
                # Extract question index from question_id (e.g., "q0" -> 0)
                q_index = int(question_id.replace("q", ""))
                
                if q_index < len(exercises):
                    exercise = exercises[q_index]
                    
                    # Check if selected option is correct
                    if answer.selectedOption == exercise.correct_options:
                        correct_count += 1
            
            except (ValueError, IndexError):
                # Skip invalid question IDs
                continue
        
        return correct_count

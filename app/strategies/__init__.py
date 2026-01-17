"""
Analytics metric strategies for the Strategy pattern implementation
"""
from app.strategies.analytics_metric_strategy import AnalyticsMetricStrategy
from app.strategies.total_attempts_metric import TotalAttemptsMetric
from app.strategies.total_time_metric import TotalTimeMetric
from app.strategies.average_time_per_exercise_metric import AverageTimePerExerciseMetric
from app.strategies.final_score_metric import FinalScoreMetric
from app.strategies.activity_success_metric import ActivitySuccessMetric
from app.strategies.correct_answers_metric import CorrectAnswersMetric

__all__ = [
    "AnalyticsMetricStrategy",
    "TotalAttemptsMetric",
    "TotalTimeMetric",
    "AverageTimePerExerciseMetric",
    "FinalScoreMetric",
    "ActivitySuccessMetric",
    "CorrectAnswersMetric",
]

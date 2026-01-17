"""
Strategy resolver for selecting the appropriate analytics metric strategy
"""
from typing import Dict
from app.strategies.analytics_metric_strategy import AnalyticsMetricStrategy
from app.strategies.total_attempts_metric import TotalAttemptsMetric
from app.strategies.total_time_metric import TotalTimeMetric
from app.strategies.average_time_per_exercise_metric import AverageTimePerExerciseMetric
from app.strategies.correct_answers_metric import CorrectAnswersMetric
from app.strategies.final_score_metric import FinalScoreMetric
from app.strategies.activity_success_metric import ActivitySuccessMetric


class MetricStrategyResolver:
    """
    Resolves and provides access to analytics metric strategies.
    
    This class maintains a registry of available strategies and provides
    a simple selection mechanism based on metric identifiers.
    """
    
    def __init__(self):
        """
        Initialize the resolver with all available metric strategies.
        """
        self._strategies: Dict[str, AnalyticsMetricStrategy] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """
        Register all built-in metric strategies.
        """
        strategies = [
            TotalAttemptsMetric(),
            TotalTimeMetric(),
            AverageTimePerExerciseMetric(),
            CorrectAnswersMetric(),
            FinalScoreMetric(),
            ActivitySuccessMetric(),
        ]
        
        for strategy in strategies:
            self._strategies[strategy.metric_name] = strategy
    
    def get_strategy(self, metric_name: str) -> AnalyticsMetricStrategy:
        """
        Get a strategy by its metric name.
        
        Args:
            metric_name: The identifier of the metric (e.g., "total_attempts")
            
        Returns:
            The corresponding strategy instance
            
        Raises:
            ValueError: If the metric name is not registered
        """
        strategy = self._strategies.get(metric_name)
        
        if strategy is None:
            available_metrics = ", ".join(self._strategies.keys())
            raise ValueError(
                f"Unknown metric '{metric_name}'. "
                f"Available metrics: {available_metrics}"
            )
        
        return strategy
    
    def register_strategy(self, strategy: AnalyticsMetricStrategy):
        """
        Register a new custom strategy.
        
        This allows extending the system with new metrics without
        modifying existing code.
        
        Args:
            strategy: The strategy instance to register
        """
        self._strategies[strategy.metric_name] = strategy
    
    def get_all_metric_names(self) -> list[str]:
        """
        Get a list of all registered metric names.
        
        Returns:
            List of metric identifiers
        """
        return list(self._strategies.keys())

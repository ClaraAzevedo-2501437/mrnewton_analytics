"""
Base Strategy interface for analytics metric calculations
"""
from abc import ABC, abstractmethod
from typing import Any, List
from app.models.schemas import Submission, Activity


class AnalyticsMetricStrategy(ABC):
    """
    Abstract base class defining the interface for all analytics metric strategies.
    
    Each concrete strategy implements a specific metric calculation algorithm
    that operates on the same input data (submissions and activity configuration).
    """
    
    @abstractmethod
    def calculate(self, submissions: List[Submission], activity: Activity) -> Any:
        """
        Calculate the metric based on student submissions and activity configuration.
        
        Args:
            submissions: List of student submissions (typically one per student)
            activity: Activity configuration containing exercise details and rules
            
        Returns:
            The calculated metric value (type varies by metric)
        """
        pass
    
    @property
    @abstractmethod
    def metric_name(self) -> str:
        """
        Returns the unique identifier/name of this metric.
        
        Returns:
            String identifier for the metric
        """
        pass

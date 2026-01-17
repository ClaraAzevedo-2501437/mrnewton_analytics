"""
Controller for analytics metrics endpoints
"""
from typing import Dict, Any
from app.services.analytics_service import AnalyticsCalculationService


class AnalyticsMetricsController:
    """
    Controller for handling analytics metrics HTTP requests.
    
    Translates HTTP requests to service calls and formats responses.
    """
    
    def __init__(self, analytics_service: AnalyticsCalculationService):
        """
        Initialize the metrics controller.
        
        Args:
            analytics_service: Service for metrics calculation
        """
        self.analytics_service = analytics_service
    
    async def get_instance_metrics(
        self,
        instance_id: str,
        metric_id: str,
        force_recalculate: bool = False
    ) -> Dict[str, Any]:
        """
        Get analytics metrics for all students in an instance for a specific metric.
        
        Args:
            instance_id: The instance ID
            metric_id: The specific metric to calculate
            force_recalculate: Force recalculation ignoring cache
            
        Returns:
            Formatted metrics response with student data
            
        Raises:
            ValueError: If instance not found
            Exception: If calculation fails
        """
        metrics_list = await self.analytics_service.calculate_instance_metrics(
            instance_id,
            metric_id,
            force_recalculate
        )
        
        return {
            "instance_id": instance_id,
            "count": len(metrics_list),
            "students": [
                {
                    "student_id": metrics.student_id,
                    "metrics": metrics.metrics.model_dump(),
                    "qualitative": metrics.qualitative.model_dump(),
                    "calculated_at": metrics.calculated_at
                }
                for metrics in metrics_list
            ]
        }
    
    async def get_student_metrics(
        self,
        instance_id: str,
        student_id: str,
        force_recalculate: bool = False
    ) -> Dict[str, Any]:
        """
        Get analytics metrics for a specific student in an instance.
        
        Args:
            instance_id: The instance ID
            student_id: The student ID
            force_recalculate: Force recalculation ignoring cache
            
        Returns:
            Formatted metrics response for the student
            
        Raises:
            ValueError: If instance or student not found
            Exception: If calculation fails
        """
        metrics = await self.analytics_service.calculate_metrics(
            instance_id,
            student_id,
            force_recalculate
        )
        
        return {
            "instance_id": metrics.instance_id,
            "student_id": metrics.student_id,
            "metrics": metrics.metrics.model_dump(),
            "qualitative": metrics.qualitative.model_dump(),
            "calculated_at": metrics.calculated_at
        }

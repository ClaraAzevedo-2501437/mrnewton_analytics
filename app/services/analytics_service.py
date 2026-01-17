"""
Service for calculating analytics metrics from submission data using Strategy pattern
"""
from datetime import datetime
from typing import List, Dict
from app.models.schemas import (
    Submission,
    Activity,
    QuantitativeMetrics,
    QualitativeMetrics,
    AnalyticsMetrics,
    Answer,
    AttemptResult
)
from app.clients.activity_client import ActivityClient
from app.strategies.metric_strategy_resolver import MetricStrategyResolver


class AnalyticsCalculationService:
    """
    Service for calculating analytics metrics from student submissions.
    
    Uses the Strategy pattern to delegate metric calculations to specific strategy classes.
    Metrics are calculated on-demand without caching.
    """
    
    def __init__(self, activity_client: ActivityClient):
        self.activity_client = activity_client
        self.strategy_resolver = MetricStrategyResolver()
    
    async def calculate_instance_metrics(
        self,
        instance_id: str,
        metric_id: str
    ) -> List[AnalyticsMetrics]:
        """
        Calculate analytics metrics for all students in an instance for a specific metric.
        Uses the Strategy pattern to select and execute only the requested metric calculation.
        Metrics are calculated on-demand without caching.
        
        Args:
            instance_id: The instance ID
            metric_id: The specific metric to calculate (e.g., 'total_attempts', 'final_score')
        
        Returns:
            List of AnalyticsMetrics for all students in the instance
        """
        # Fetch instance to verify it exists
        instance = await self.activity_client.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")
        
        # Fetch activity configuration
        activity = await self.activity_client.get_activity(instance.activityId)
        if not activity:
            raise ValueError(f"Activity {instance.activityId} not found")
        
        # Get all submissions for this instance from Activity component
        submissions = await self.activity_client.get_instance_submissions(instance_id)
        
        if not submissions:
            return []
        
        # Calculate metrics for each student
        all_metrics = []
        for submission in submissions:
            # Calculate only the requested metric using the appropriate strategy
            quantitative = self._calculate_specific_metric(submission, activity, metric_id)
            qualitative = self._extract_qualitative_metrics(submission)
            
            # Create analytics metrics object
            metrics = AnalyticsMetrics(
                instance_id=instance_id,
                student_id=submission.studentId,
                metrics=quantitative,
                qualitative=qualitative,
                calculated_at=datetime.utcnow().isoformat() + "Z"
            )
            
            all_metrics.append(metrics)
        
        return all_metrics
    
    async def calculate_metrics(
        self,
        instance_id: str,
        student_id: str
    ) -> AnalyticsMetrics:
        """
        Calculate analytics metrics for a student's submission.
        Metrics are calculated on-demand without caching.
        
        Args:
            instance_id: The instance ID
            student_id: The student ID
        
        Returns:
            AnalyticsMetrics with calculated quantitative and qualitative data
        """
        # Fetch submission data from activity component
        submission = await self.activity_client.get_submission(instance_id, student_id)
        if not submission:
            raise ValueError(f"No submission found for instance {instance_id} and student {student_id}")
        
        # Fetch instance to get activity_id
        instance = await self.activity_client.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")
        
        # Fetch activity configuration
        activity = await self.activity_client.get_activity(instance.activityId)
        if not activity:
            raise ValueError(f"Activity {instance.activityId} not found")
        
        # Calculate metrics
        quantitative = self._calculate_quantitative_metrics(submission, activity)
        qualitative = self._extract_qualitative_metrics(submission)
        
        # Create analytics metrics object
        metrics = AnalyticsMetrics(
            instance_id=instance_id,
            student_id=student_id,
            metrics=quantitative,
            qualitative=qualitative,
            calculated_at=datetime.utcnow().isoformat() + "Z"
        )
        
        return metrics
    
    def _calculate_quantitative_metrics(
        self,
        submission: Submission,
        activity: Activity
    ) -> QuantitativeMetrics:
        """
        Calculate quantitative metrics from submission data using Strategy pattern.
        
        Each metric is calculated by its corresponding strategy, eliminating
        conditional logic from this service.
        """
        if not submission.attempts:
            # No attempts, return zeros
            return QuantitativeMetrics(
                total_attempts=0,
                total_time_seconds=0,
                average_time_per_attempt=0.0,
                number_of_correct_answers=0,
                final_score=0.0,
                activity_success=False
            )
        
        # Wrap single submission in list for strategy interface
        submissions = [submission]
        
        # Calculate each metric using its strategy
        total_attempts = self.strategy_resolver.get_strategy("total_attempts").calculate(
            submissions, activity
        )
        
        total_time_seconds = self.strategy_resolver.get_strategy("total_time_seconds").calculate(
            submissions, activity
        )
        
        average_time_per_attempt = self.strategy_resolver.get_strategy("average_time_per_attempt").calculate(
            submissions, activity
        )
        
        number_of_correct_answers = self.strategy_resolver.get_strategy("number_of_correct_answers").calculate(
            submissions, activity
        )
        
        final_score = self.strategy_resolver.get_strategy("final_score").calculate(
            submissions, activity
        )
        
        activity_success = self.strategy_resolver.get_strategy("activity_success").calculate(
            submissions, activity
        )
        
        return QuantitativeMetrics(
            total_attempts=total_attempts,
            total_time_seconds=total_time_seconds,
            average_time_per_attempt=average_time_per_attempt,
            number_of_correct_answers=number_of_correct_answers,
            final_score=final_score,
            activity_success=activity_success
        )
    
    def _calculate_specific_metric(
        self,
        submission: Submission,
        activity: Activity,
        metric_id: str
    ) -> QuantitativeMetrics:
        """
        Calculate a specific metric using the Strategy pattern.
        Only the requested metric is calculated; others are set to default values.
        
        Args:
            submission: The student submission data
            activity: The activity configuration
            metric_id: The metric to calculate
        
        Returns:
            QuantitativeMetrics with only the requested metric calculated
        """
        if not submission.attempts:
            # No attempts, return zeros
            return QuantitativeMetrics(
                total_attempts=0,
                total_time_seconds=0,
                average_time_per_attempt=0.0,
                number_of_correct_answers=0,
                final_score=0.0,
                activity_success=False
            )
        
        # Map frontend metric_ids to backend strategy keys
        metric_id_map = {
            "total_attempts": "total_attempts",
            "total_time": "total_time_seconds",
            "average_time_per_attempt": "average_time_per_attempt",
            "correct_answers": "number_of_correct_answers",
            "final_score": "final_score",
            "activity_success": "activity_success"
        }
        
        strategy_key = metric_id_map.get(metric_id)
        if not strategy_key:
            raise ValueError(f"Unknown metric_id: {metric_id}")
        
        # Wrap single submission in list for strategy interface
        submissions = [submission]
        
        # Calculate only the requested metric using its strategy
        strategy = self.strategy_resolver.get_strategy(strategy_key)
        calculated_value = strategy.calculate(submissions, activity)
        
        # Create QuantitativeMetrics with only the requested metric populated
        # Set all others to 0 or False
        return QuantitativeMetrics(
            total_attempts=calculated_value if metric_id == "total_attempts" else 0,
            total_time_seconds=calculated_value if metric_id == "total_time" else 0,
            average_time_per_attempt=calculated_value if metric_id == "average_time_per_attempt" else 0.0,
            number_of_correct_answers=calculated_value if metric_id == "correct_answers" else 0,
            final_score=calculated_value if metric_id == "final_score" else 0.0,
            activity_success=calculated_value if metric_id == "activity_success" else False
        )
    
    def _extract_qualitative_metrics(self, submission: Submission) -> QualitativeMetrics:
        """
        Extract qualitative metrics (rationales) from submission
        """
        rationales = []
        
        # Get rationales from the last attempt
        if submission.attempts:
            last_attempt = submission.attempts[-1]
            for question_id, answer in last_attempt.answers.items():
                if answer.rationale and answer.rationale.strip():
                    rationales.append(answer.rationale)
        
        return QualitativeMetrics(answer_rationale=rationales)

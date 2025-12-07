"""
Service for calculating analytics metrics from submission data
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
from app.repositories.metrics_repository import AnalyticsMetricsRepository


class AnalyticsCalculationService:
    """
    Service for calculating analytics metrics from student submissions
    """
    
    def __init__(
        self,
        activity_client: ActivityClient,
        metrics_repository: AnalyticsMetricsRepository
    ):
        self.activity_client = activity_client
        self.metrics_repository = metrics_repository
    
    async def calculate_instance_metrics(
        self,
        instance_id: str,
        force_recalculate: bool = False
    ) -> List[AnalyticsMetrics]:
        """
        Calculate analytics metrics for all students in an instance
        
        Args:
            instance_id: The instance ID
            force_recalculate: If True, recalculate even if cached metrics exist
        
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
            # Calculate quantitative metrics
            quantitative = self._calculate_quantitative_metrics(submission, activity)
            qualitative = self._extract_qualitative_metrics(submission)
            
            # Create analytics metrics object
            metrics = AnalyticsMetrics(
                instance_id=instance_id,
                student_id=submission.studentId,
                metrics=quantitative,
                qualitative=qualitative,
                calculated_at=datetime.utcnow().isoformat() + "Z"
            )
            
            # Cache the metrics
            await self.metrics_repository.save(metrics)
            
            all_metrics.append(metrics)
        
        return all_metrics
    
    async def calculate_metrics(
        self,
        instance_id: str,
        student_id: str,
        force_recalculate: bool = False
    ) -> AnalyticsMetrics:
        """
        Calculate analytics metrics for a student's submission
        
        Args:
            instance_id: The instance ID
            student_id: The student ID
            force_recalculate: If True, recalculate even if cached metrics exist
        
        Returns:
            AnalyticsMetrics with calculated quantitative and qualitative data
        """
        
        # Check if we have cached metrics
        if not force_recalculate:
            cached_metrics = await self.metrics_repository.find_by_instance_and_student(
                instance_id,
                student_id
            )
            if cached_metrics:
                return cached_metrics
        
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
        
        # Cache the metrics
        await self.metrics_repository.save(metrics)
        
        return metrics
    
    def _calculate_quantitative_metrics(
        self,
        submission: Submission,
        activity: Activity
    ) -> QuantitativeMetrics:
        """
        Calculate quantitative metrics from submission data
        """
        total_exercises = activity.number_of_exercises
        attempts = submission.attempts
        
        # Get the last (most recent) attempt
        last_attempt = attempts[-1] if attempts else None
        
        if not last_attempt:
            # No attempts, return zeros
            return QuantitativeMetrics(
                total_attempts=0,
                total_time_seconds=0,
                average_time_per_attempt=0.0,
                number_of_correct_answers=0,
                final_score=0.0,
                activity_success=False
            )
        
        # Total attempts across all exercises
        total_attempts = len(attempts)
        
        # Calculate time spent
        total_time_seconds = self._calculate_total_time(submission, activity)
        
        # Average time per attempt
        average_time_per_attempt = (
            total_time_seconds / total_attempts if total_attempts > 0 else 0.0
        )
        
        # Count correct answers
        number_of_correct_answers = self._count_correct_answers(
            last_attempt,
            activity
        )
        
        # Calculate final score based on scoring policy
        final_score = self._calculate_final_score(
            submission,
            activity,
            number_of_correct_answers
        )
        
        # Check if activity was successful
        approval_threshold = activity.approval_threshold or 0.5
        activity_success = final_score >= approval_threshold
        
        return QuantitativeMetrics(
            total_attempts=total_attempts,
            total_time_seconds=total_time_seconds,
            average_time_per_attempt=average_time_per_attempt,
            number_of_correct_answers=number_of_correct_answers,
            final_score=final_score,
            activity_success=activity_success
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
    
    def _calculate_total_time(self, submission: Submission, activity: Activity) -> int:
        """
        Calculate total time spent on the activity in seconds
        """
        if not submission.attempts or len(submission.attempts) == 0:
            return 0
        
        # If attempts have timeSpentSeconds, sum them up
        if all(attempt.timeSpentSeconds is not None for attempt in submission.attempts):
            return sum(attempt.timeSpentSeconds for attempt in submission.attempts)
        
        # Fallback: calculate from timestamps (for backward compatibility)
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
            
            # Calculate difference in seconds between first and last attempt
            time_diff = (last_submitted - first_submitted).total_seconds()
            
            # Ensure non-negative
            time_diff = max(0, time_diff)
            
            # Cap at activity's total time limit if configured
            max_time = activity.total_time_minutes * 60
            return min(int(time_diff), max_time) if max_time > 0 else int(time_diff)
        
        except Exception as e:
            print(f"Error calculating time: {e}")
            # Fallback: estimate based on average
            return activity.total_time_minutes * 60
    
    def _count_correct_answers(self, attempt: AttemptResult, activity: Activity) -> int:
        """
        Count the number of correct answers in an attempt
        
        A question is correct if:
        - The selected option matches the correct option
        - The answer is within tolerance (if applicable)
        """
        correct_count = 0
        
        # Create a mapping of question index to exercise
        exercises = activity.exercises
        
        for question_id, answer in attempt.answers.items():
            # Extract question index from question_id (e.g., "q0" -> 0)
            try:
                q_index = int(question_id.replace("q", ""))
                if q_index < len(exercises):
                    exercise = exercises[q_index]
                    
                    # Check if selected option is correct
                    if answer.selectedOption == exercise.correct_options:
                        correct_count += 1
            
            except (ValueError, IndexError) as e:
                print(f"Error processing question {question_id}: {e}")
                continue
        
        return correct_count
    
    def _calculate_final_score(
        self,
        submission: Submission,
        activity: Activity,
        correct_answers: int
    ) -> float:
        """
        Calculate final score based on scoring policy
        
        Policies:
        - linear: score = correct_answers / total_exercises
        - non-linear: score based on best attempt with diminishing returns
        """
        total_exercises = activity.number_of_exercises
        
        if total_exercises == 0:
            return 0.0
        
        scoring_policy = activity.scoring_policy or "linear"
        
        if scoring_policy == "linear":
            # Simple linear scoring
            return correct_answers / total_exercises
        
        elif scoring_policy == "non-linear":
            # Non-linear scoring with penalty for retries
            base_score = correct_answers / total_exercises
            num_attempts = len(submission.attempts)
            
            # Apply penalty: reduce score by 10% for each retry beyond the first
            penalty_factor = max(0.5, 1.0 - (0.1 * (num_attempts - 1)))
            return base_score * penalty_factor
        
        else:
            # Default to linear
            return correct_answers / total_exercises

"""
Unit tests for analytics metric strategies
"""
import pytest
from datetime import datetime
from app.models.schemas import (
    Submission,
    Activity,
    AttemptResult,
    Answer,
    Exercise,
    ActivityConfig
)
from app.strategies.total_attempts_metric import TotalAttemptsMetric
from app.strategies.total_time_metric import TotalTimeMetric
from app.strategies.average_time_per_exercise_metric import AverageTimePerExerciseMetric
from app.strategies.correct_answers_metric import CorrectAnswersMetric
from app.strategies.final_score_metric import FinalScoreMetric
from app.strategies.activity_success_metric import ActivitySuccessMetric
from app.strategies.metric_strategy_resolver import MetricStrategyResolver


@pytest.fixture
def sample_activity():
    """Create a sample activity configuration"""
    return Activity(
        activity_id="act_001",
        created_at="2026-01-15T09:00:00Z",
        title="Test Quiz",
        grade=10,
        modules="Physics",
        number_of_exercises=5,
        total_time_minutes=30,
        number_of_retries=3,
        approval_threshold=0.6,
        scoring_policy="linear",
        exercises=[
            Exercise(
                question="Question 1",
                options=["A", "B", "C", "D"],
                correct_options="B",
                correct_answer="Answer B"
            ),
            Exercise(
                question="Question 2",
                options=["A", "B", "C", "D"],
                correct_options="C",
                correct_answer="Answer C"
            ),
            Exercise(
                question="Question 3",
                options=["A", "B", "C", "D"],
                correct_options="A",
                correct_answer="Answer A"
            ),
            Exercise(
                question="Question 4",
                options=["A", "B", "C", "D"],
                correct_options="D",
                correct_answer="Answer D"
            ),
            Exercise(
                question="Question 5",
                options=["A", "B", "C", "D"],
                correct_options="B",
                correct_answer="Answer B"
            ),
        ]
    )


@pytest.fixture
def sample_submission_single_attempt():
    """Create a sample submission with one attempt"""
    return Submission(
        submissionId="sub_001",
        instanceId="inst_001",
        studentId="student_001",
        numberOfAttempts=1,
        attempts=[
            AttemptResult(
                attemptIndex=0,
                answers={
                    "q0": Answer(selectedOption="B", rationale="Reason for B"),
                    "q1": Answer(selectedOption="C", rationale="Reason for C"),
                    "q2": Answer(selectedOption="A", rationale="Reason for A"),
                    "q3": Answer(selectedOption="A", rationale="Wrong answer"),
                    "q4": Answer(selectedOption="B", rationale="Reason for B"),
                },
                result=0.8,
                submittedAt="2026-01-15T10:00:00Z",
                timeSpentSeconds=600
            )
        ],
        createdAt="2026-01-15T09:50:00Z"
    )


@pytest.fixture
def sample_submission_multiple_attempts():
    """Create a sample submission with multiple attempts"""
    return Submission(
        submissionId="sub_002",
        instanceId="inst_001",
        studentId="student_002",
        numberOfAttempts=3,
        attempts=[
            AttemptResult(
                attemptIndex=0,
                answers={
                    "q0": Answer(selectedOption="A", rationale="First try"),
                    "q1": Answer(selectedOption="A", rationale="First try"),
                    "q2": Answer(selectedOption="A", rationale="First try"),
                    "q3": Answer(selectedOption="A", rationale="First try"),
                    "q4": Answer(selectedOption="A", rationale="First try"),
                },
                result=0.2,
                submittedAt="2026-01-15T10:00:00Z",
                timeSpentSeconds=300
            ),
            AttemptResult(
                attemptIndex=1,
                answers={
                    "q0": Answer(selectedOption="B", rationale="Second try"),
                    "q1": Answer(selectedOption="C", rationale="Second try"),
                    "q2": Answer(selectedOption="A", rationale="Second try"),
                    "q3": Answer(selectedOption="A", rationale="Second try"),
                    "q4": Answer(selectedOption="A", rationale="Second try"),
                },
                result=0.6,
                submittedAt="2026-01-15T10:10:00Z",
                timeSpentSeconds=400
            ),
            AttemptResult(
                attemptIndex=2,
                answers={
                    "q0": Answer(selectedOption="B", rationale="Final try"),
                    "q1": Answer(selectedOption="C", rationale="Final try"),
                    "q2": Answer(selectedOption="A", rationale="Final try"),
                    "q3": Answer(selectedOption="D", rationale="Final try"),
                    "q4": Answer(selectedOption="B", rationale="Final try"),
                },
                result=1.0,
                submittedAt="2026-01-15T10:20:00Z",
                timeSpentSeconds=500
            )
        ],
        createdAt="2026-01-15T09:55:00Z"
    )


class TestTotalAttemptsMetric:
    """Tests for TotalAttemptsMetric strategy"""
    
    def test_metric_name(self):
        strategy = TotalAttemptsMetric()
        assert strategy.metric_name == "total_attempts"
    
    def test_single_submission_single_attempt(self, sample_submission_single_attempt, sample_activity):
        strategy = TotalAttemptsMetric()
        result = strategy.calculate([sample_submission_single_attempt], sample_activity)
        assert result == 1
    
    def test_single_submission_multiple_attempts(self, sample_submission_multiple_attempts, sample_activity):
        strategy = TotalAttemptsMetric()
        result = strategy.calculate([sample_submission_multiple_attempts], sample_activity)
        assert result == 3
    
    def test_multiple_submissions(self, sample_submission_single_attempt, sample_submission_multiple_attempts, sample_activity):
        strategy = TotalAttemptsMetric()
        result = strategy.calculate(
            [sample_submission_single_attempt, sample_submission_multiple_attempts],
            sample_activity
        )
        assert result == 4  # 1 + 3
    
    def test_empty_submissions(self, sample_activity):
        strategy = TotalAttemptsMetric()
        result = strategy.calculate([], sample_activity)
        assert result == 0


class TestTotalTimeMetric:
    """Tests for TotalTimeMetric strategy"""
    
    def test_metric_name(self):
        strategy = TotalTimeMetric()
        assert strategy.metric_name == "total_time_seconds"
    
    def test_single_submission_with_time_spent(self, sample_submission_single_attempt, sample_activity):
        strategy = TotalTimeMetric()
        result = strategy.calculate([sample_submission_single_attempt], sample_activity)
        assert result == 600
    
    def test_multiple_attempts_with_time_spent(self, sample_submission_multiple_attempts, sample_activity):
        strategy = TotalTimeMetric()
        result = strategy.calculate([sample_submission_multiple_attempts], sample_activity)
        assert result == 1200  # 300 + 400 + 500
    
    def test_empty_submissions(self, sample_activity):
        strategy = TotalTimeMetric()
        result = strategy.calculate([], sample_activity)
        assert result == 0


class TestAverageTimePerExerciseMetric:
    """Tests for AverageTimePerExerciseMetric strategy"""
    
    def test_metric_name(self):
        strategy = AverageTimePerExerciseMetric()
        assert strategy.metric_name == "average_time_per_attempt"
    
    def test_single_attempt(self, sample_submission_single_attempt, sample_activity):
        strategy = AverageTimePerExerciseMetric()
        result = strategy.calculate([sample_submission_single_attempt], sample_activity)
        assert result == 600.0  # 600 seconds / 1 attempt
    
    def test_multiple_attempts(self, sample_submission_multiple_attempts, sample_activity):
        strategy = AverageTimePerExerciseMetric()
        result = strategy.calculate([sample_submission_multiple_attempts], sample_activity)
        assert result == 400.0  # 1200 seconds / 3 attempts
    
    def test_empty_submissions(self, sample_activity):
        strategy = AverageTimePerExerciseMetric()
        result = strategy.calculate([], sample_activity)
        assert result == 0.0


class TestCorrectAnswersMetric:
    """Tests for CorrectAnswersMetric strategy"""
    
    def test_metric_name(self):
        strategy = CorrectAnswersMetric()
        assert strategy.metric_name == "number_of_correct_answers"
    
    def test_four_correct_answers(self, sample_submission_single_attempt, sample_activity):
        strategy = CorrectAnswersMetric()
        result = strategy.calculate([sample_submission_single_attempt], sample_activity)
        assert result == 4  # q0, q1, q2, q4 are correct
    
    def test_all_correct_answers(self, sample_submission_multiple_attempts, sample_activity):
        strategy = CorrectAnswersMetric()
        result = strategy.calculate([sample_submission_multiple_attempts], sample_activity)
        # Last attempt has all correct
        assert result == 5
    
    def test_empty_submissions(self, sample_activity):
        strategy = CorrectAnswersMetric()
        result = strategy.calculate([], sample_activity)
        assert result == 0


class TestFinalScoreMetric:
    """Tests for FinalScoreMetric strategy"""
    
    def test_metric_name(self):
        strategy = FinalScoreMetric()
        assert strategy.metric_name == "final_score"
    
    def test_linear_scoring(self, sample_submission_single_attempt, sample_activity):
        strategy = FinalScoreMetric()
        result = strategy.calculate([sample_submission_single_attempt], sample_activity)
        assert result == 0.8  # 4 correct out of 5
    
    def test_all_correct(self, sample_submission_multiple_attempts, sample_activity):
        strategy = FinalScoreMetric()
        result = strategy.calculate([sample_submission_multiple_attempts], sample_activity)
        assert result == 1.0  # 5 correct out of 5
    
    def test_non_linear_scoring(self, sample_submission_multiple_attempts, sample_activity):
        # Test non-linear scoring with penalty
        sample_activity.scoring_policy = "non-linear"
        strategy = FinalScoreMetric()
        result = strategy.calculate([sample_submission_multiple_attempts], sample_activity)
        # Base score 1.0, with 3 attempts: penalty = 1.0 - 0.1*(3-1) = 0.8
        assert result == 0.8
    
    def test_empty_submissions(self, sample_activity):
        strategy = FinalScoreMetric()
        result = strategy.calculate([], sample_activity)
        assert result == 0.0


class TestActivitySuccessMetric:
    """Tests for ActivitySuccessMetric strategy"""
    
    def test_metric_name(self):
        strategy = ActivitySuccessMetric()
        assert strategy.metric_name == "activity_success"
    
    def test_successful_above_threshold(self, sample_submission_single_attempt, sample_activity):
        # Score is 0.8, threshold is 0.6
        strategy = ActivitySuccessMetric()
        result = strategy.calculate([sample_submission_single_attempt], sample_activity)
        assert result is True
    
    def test_successful_meets_threshold(self, sample_submission_multiple_attempts, sample_activity):
        # Perfect score of 1.0
        strategy = ActivitySuccessMetric()
        result = strategy.calculate([sample_submission_multiple_attempts], sample_activity)
        assert result is True
    
    def test_unsuccessful_below_threshold(self, sample_activity):
        # Create submission with low score
        low_score_submission = Submission(
            submissionId="sub_003",
            instanceId="inst_001",
            studentId="student_003",
            numberOfAttempts=1,
            attempts=[
                AttemptResult(
                    attemptIndex=0,
                    answers={
                        "q0": Answer(selectedOption="A", rationale="Wrong"),
                        "q1": Answer(selectedOption="A", rationale="Wrong"),
                        "q2": Answer(selectedOption="B", rationale="Wrong"),
                        "q3": Answer(selectedOption="A", rationale="Wrong"),
                        "q4": Answer(selectedOption="A", rationale="Wrong"),
                    },
                    result=0.2,
                    submittedAt="2026-01-15T10:00:00Z",
                    timeSpentSeconds=300
                )
            ],
            createdAt="2026-01-15T09:50:00Z"
        )
        
        strategy = ActivitySuccessMetric()
        result = strategy.calculate([low_score_submission], sample_activity)
        assert result is False
    
    def test_empty_submissions(self, sample_activity):
        strategy = ActivitySuccessMetric()
        result = strategy.calculate([], sample_activity)
        assert result is False


class TestMetricStrategyResolver:
    """Tests for MetricStrategyResolver"""
    
    def test_get_all_metric_names(self):
        resolver = MetricStrategyResolver()
        metric_names = resolver.get_all_metric_names()
        
        expected_metrics = [
            "total_attempts",
            "total_time_seconds",
            "average_time_per_attempt",
            "number_of_correct_answers",
            "final_score",
            "activity_success"
        ]
        
        for metric in expected_metrics:
            assert metric in metric_names
    
    def test_get_valid_strategy(self):
        resolver = MetricStrategyResolver()
        strategy = resolver.get_strategy("total_attempts")
        assert isinstance(strategy, TotalAttemptsMetric)
        assert strategy.metric_name == "total_attempts"
    
    def test_get_invalid_strategy_raises_error(self):
        resolver = MetricStrategyResolver()
        with pytest.raises(ValueError, match="Unknown metric"):
            resolver.get_strategy("invalid_metric")
    
    def test_register_custom_strategy(self, sample_activity):
        resolver = MetricStrategyResolver()
        
        # Create a custom strategy
        from app.strategies.analytics_metric_strategy import AnalyticsMetricStrategy
        
        class CustomMetric(AnalyticsMetricStrategy):
            @property
            def metric_name(self):
                return "custom_metric"
            
            def calculate(self, submissions, activity):
                return 42
        
        custom_strategy = CustomMetric()
        resolver.register_strategy(custom_strategy)
        
        # Verify it's registered
        assert "custom_metric" in resolver.get_all_metric_names()
        
        # Verify we can retrieve and use it
        retrieved_strategy = resolver.get_strategy("custom_metric")
        result = retrieved_strategy.calculate([], sample_activity)
        assert result == 42
    
    def test_all_strategies_have_unique_names(self):
        resolver = MetricStrategyResolver()
        metric_names = resolver.get_all_metric_names()
        
        # Check for duplicates
        assert len(metric_names) == len(set(metric_names))


class TestStrategyExtensibility:
    """Tests demonstrating extensibility of the Strategy pattern"""
    
    def test_new_strategy_can_be_added_without_modifying_existing(self, sample_activity):
        """
        Demonstrates that new strategies can be added without modifying
        existing code - adhering to Open/Closed Principle
        """
        from app.strategies.analytics_metric_strategy import AnalyticsMetricStrategy
        
        class PassRateMetric(AnalyticsMetricStrategy):
            """New metric: percentage of students who passed"""
            
            @property
            def metric_name(self):
                return "pass_rate"
            
            def calculate(self, submissions, activity):
                if not submissions:
                    return 0.0
                
                from app.strategies.activity_success_metric import ActivitySuccessMetric
                success_strategy = ActivitySuccessMetric()
                
                passed_count = sum(
                    1 for submission in submissions
                    if success_strategy.calculate([submission], activity)
                )
                
                return passed_count / len(submissions)
        
        # Add new strategy to resolver
        resolver = MetricStrategyResolver()
        new_metric = PassRateMetric()
        resolver.register_strategy(new_metric)
        
        # Use the new strategy
        strategy = resolver.get_strategy("pass_rate")
        assert strategy.metric_name == "pass_rate"

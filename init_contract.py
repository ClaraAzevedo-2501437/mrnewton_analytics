"""
Script to initialize the analytics contract with all available metrics
"""
import asyncio
from app.database.mongodb import connect_to_mongodb, close_mongodb_connection
from app.repositories.contract_repository import AnalyticsContractRepository
from app.models.schemas import MetricDefinition, AnalyticsContract


async def initialize_contract():
    """Create the default analytics contract"""
    print("Connecting to MongoDB...")
    await connect_to_mongodb()
    
    # Define all available quantitative metrics
    quantitative_metrics = [
        MetricDefinition(
            metric_id="total_attempts",
            name="Total Attempts",
            type="int",
            description="Total number of attempts across all exercises"
        ),
        MetricDefinition(
            metric_id="total_time",
            name="Total Time",
            type="int",
            description="Total time spent in seconds"
        ),
        MetricDefinition(
            metric_id="average_time_per_attempt",
            name="Average Time Per Attempt",
            type="float",
            description="Average time spent per attempt"
        ),
        MetricDefinition(
            metric_id="correct_answers",
            name="Correct Answers",
            type="int",
            description="Number of correct answers"
        ),
        MetricDefinition(
            metric_id="final_score",
            name="Final Score",
            type="float",
            description="Final score (0-1)"
        ),
        MetricDefinition(
            metric_id="activity_success",
            name="Activity Success",
            type="bool",
            description="Whether the activity was successful"
        )
    ]
    
    # Define qualitative metrics (if any)
    qualitative_metrics = [
        MetricDefinition(
            metric_id="answer_rationale",
            name="Answer Rationale",
            type="list[str]",
            description="Rationales provided for answers"
        )
    ]
    
    # Create the contract
    contract = AnalyticsContract(
        quantitative=quantitative_metrics,
        qualitative=qualitative_metrics
    )
    
    # Save to database
    from app.database.mongodb import get_database
    db = get_database()
    repo = AnalyticsContractRepository(db)
    
    saved_contract = await repo.save(contract)
    
    print("\n✓ Analytics contract created successfully!")
    print(f"  - Quantitative metrics: {len(saved_contract.quantitative)}")
    print(f"  - Qualitative metrics: {len(saved_contract.qualitative)}")
    
    for metric in saved_contract.quantitative:
        print(f"    • {metric.name} ({metric.metric_id})")
    
    await close_mongodb_connection()
    print("\n✓ Contract initialization complete!")


if __name__ == "__main__":
    asyncio.run(initialize_contract())

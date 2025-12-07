from fastapi import APIRouter, Path, HTTPException, Depends, Body, Query
from datetime import datetime
from typing import List
from app.database.mongodb import get_database
from app.repositories.contract_repository import AnalyticsContractRepository
from app.repositories.metrics_repository import AnalyticsMetricsRepository
from app.clients.activity_client import ActivityClient
from app.services.analytics_service import AnalyticsCalculationService
from app.models.schemas import MetricDefinition, AnalyticsContract

router = APIRouter()

# Dependency injection helpers
def get_contract_repository():
    db = get_database()
    return AnalyticsContractRepository(db)

def get_metrics_repository():
    db = get_database()
    return AnalyticsMetricsRepository(db)

def get_activity_client():
    return ActivityClient()

def get_analytics_service(
    activity_client: ActivityClient = Depends(get_activity_client),
    metrics_repository: AnalyticsMetricsRepository = Depends(get_metrics_repository)
):
    return AnalyticsCalculationService(activity_client, metrics_repository)


@router.get("/contract")
async def get_analytics_contract(
    contract_repo: AnalyticsContractRepository = Depends(get_contract_repository)
):
    """
    Get the analytics contract listing all supported qualitative and quantitative metrics.
    """
    # Get the current analytics contract
    contract = await contract_repo.get_current()
    
    if not contract:
        raise HTTPException(
            status_code=404,
            detail="No analytics contract found. Please create one using POST /api/v1/analytics/contract"
        )
    
    # Format response to match expected structure
    return {
        "qualAnalytics": [metric.model_dump() for metric in contract.qualitative],
        "quantAnalytics": [metric.model_dump() for metric in contract.quantitative]
    }


@router.post("/contract")
async def create_analytics_contract(
    qualitative: List[MetricDefinition] = Body(..., description="List of qualitative metrics"),
    quantitative: List[MetricDefinition] = Body(..., description="List of quantitative metrics"),
    contract_repo: AnalyticsContractRepository = Depends(get_contract_repository)
):
    """
    Create or update the analytics contract with custom metrics.
    This defines which qualitative and quantitative metrics are available.
    """
    try:
        # Create new contract
        contract = AnalyticsContract(
            qualitative=qualitative,
            quantitative=quantitative
        )
        
        # Save to database
        saved_contract = await contract_repo.save(contract)
        
        return {
            "message": "Analytics contract created successfully",
            "qualAnalytics": [metric.model_dump() for metric in saved_contract.qualitative],
            "quantAnalytics": [metric.model_dump() for metric in saved_contract.quantitative]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating analytics contract: {str(e)}")


@router.get("/instances/{instance_id}/metrics")
async def get_instance_metrics(
    instance_id: str = Path(..., description="The instance ID to retrieve metrics for"),
    force_recalculate: bool = Query(False, description="Force recalculation of metrics, ignoring cache"),
    analytics_service: AnalyticsCalculationService = Depends(get_analytics_service)
):
    """
    Get analytics metrics for all students in an activity instance.
    Returns cached metrics for all students who have submitted.
    """
    try:
        metrics_list = await analytics_service.calculate_instance_metrics(instance_id, force_recalculate)
        
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
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving instance metrics: {str(e)}")


@router.get("/instances/{instance_id}/students/{student_id}/metrics")
async def get_student_metrics(
    instance_id: str = Path(..., description="The instance ID to retrieve metrics for"),
    student_id: str = Path(..., description="The student ID to retrieve metrics for"),
    force_recalculate: bool = Query(False, description="Force recalculation of metrics, ignoring cache"),
    analytics_service: AnalyticsCalculationService = Depends(get_analytics_service)
):
    """
    Get analytics metrics for a specific student in an activity instance.
    Calculates metrics on-demand from submission data.
    """
    try:
        metrics = await analytics_service.calculate_metrics(instance_id, student_id, force_recalculate)
        
        return {
            "instance_id": metrics.instance_id,
            "student_id": metrics.student_id,
            "metrics": metrics.metrics.model_dump(),
            "qualitative": metrics.qualitative.model_dump(),
            "calculated_at": metrics.calculated_at
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating metrics: {str(e)}")

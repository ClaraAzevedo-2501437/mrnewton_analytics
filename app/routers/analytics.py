from fastapi import APIRouter, Path, HTTPException, Depends, Body, Query
from typing import List
from app.database.mongodb import get_database
from app.repositories.contract_repository import AnalyticsContractRepository
from app.clients.activity_client import ActivityClient
from app.services.analytics_service import AnalyticsCalculationService
from app.services.contract_service import AnalyticsContractService
from app.controllers.contract_controller import AnalyticsContractController
from app.controllers.metrics_controller import AnalyticsMetricsController
from app.models.schemas import MetricDefinition

router = APIRouter()

# Dependency injection helpers
def get_contract_repository():
    db = get_database()
    return AnalyticsContractRepository(db)

def get_activity_client():
    return ActivityClient()

def get_contract_service(
    contract_repo: AnalyticsContractRepository = Depends(get_contract_repository)
):
    return AnalyticsContractService(contract_repo)

def get_contract_controller(
    contract_service: AnalyticsContractService = Depends(get_contract_service)
):
    return AnalyticsContractController(contract_service)

def get_analytics_service(
    activity_client: ActivityClient = Depends(get_activity_client)
):
    return AnalyticsCalculationService(activity_client)

def get_metrics_controller(
    analytics_service: AnalyticsCalculationService = Depends(get_analytics_service)
):
    return AnalyticsMetricsController(analytics_service)


@router.get("/contract")
async def get_analytics_contract(
    contract_controller: AnalyticsContractController = Depends(get_contract_controller)
):
    """
    Get the analytics contract listing all supported qualitative and quantitative metrics.
    """
    try:
        return await contract_controller.get_contract()
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving analytics contract: {str(e)}"
        )


@router.post("/contract")
async def create_analytics_contract(
    qualitative: List[MetricDefinition] = Body(..., description="List of qualitative metrics"),
    quantitative: List[MetricDefinition] = Body(..., description="List of quantitative metrics"),
    contract_controller: AnalyticsContractController = Depends(get_contract_controller)
):
    """
    Create or update the analytics contract with custom metrics.
    This defines which qualitative and quantitative metrics are available.
    """
    try:
        return await contract_controller.create_contract(qualitative, quantitative)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating analytics contract: {str(e)}"
        )


@router.get("/instances/{instance_id}/metrics")
async def get_instance_metrics(
    instance_id: str = Path(..., description="The instance ID to retrieve metrics for"),
    metric_id: str = Query(..., description="The metric ID to calculate (e.g., 'total_attempts', 'final_score')"),
    metrics_controller: AnalyticsMetricsController = Depends(get_metrics_controller)
):
    """
    Get analytics metrics for all students in an activity instance for a specific metric.
    Uses the Strategy pattern to calculate only the requested metric.
    """
    try:
        return await metrics_controller.get_instance_metrics(instance_id, metric_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving instance metrics: {str(e)}")


@router.get("/instances/{instance_id}/students/{student_id}/metrics")
async def get_student_metrics(
    instance_id: str = Path(..., description="The instance ID to retrieve metrics for"),
    student_id: str = Path(..., description="The student ID to retrieve metrics for"),
    metrics_controller: AnalyticsMetricsController = Depends(get_metrics_controller)
):
    """
    Get analytics metrics for a specific student in an activity instance.
    Calculates metrics on-demand from submission data.
    """
    try:
        return await metrics_controller.get_student_metrics(instance_id, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating metrics: {str(e)}")

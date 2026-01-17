"""
Controller for analytics contract endpoints
"""
from typing import Dict, Any
from app.services.contract_service import AnalyticsContractService
from app.models.schemas import MetricDefinition


class AnalyticsContractController:
    """
    Controller for handling analytics contract HTTP requests.
    
    Translates HTTP requests to service calls and formats responses.
    """
    
    def __init__(self, contract_service: AnalyticsContractService):
        """
        Initialize the contract controller.
        
        Args:
            contract_service: Service for contract operations
        """
        self.contract_service = contract_service
    
    async def get_contract(self) -> Dict[str, Any]:
        """
        Get the current analytics contract.
        
        Returns:
            Formatted contract response with qualitative and quantitative metrics
            
        Raises:
            ValueError: If no contract exists
        """
        contract = await self.contract_service.get_current_contract()
        
        # Format response to match expected structure
        return {
            "qualAnalytics": [metric.model_dump() for metric in contract.qualitative],
            "quantAnalytics": [metric.model_dump() for metric in contract.quantitative]
        }
    
    async def create_contract(
        self,
        qualitative: list[MetricDefinition],
        quantitative: list[MetricDefinition]
    ) -> Dict[str, Any]:
        """
        Create or update the analytics contract.
        
        Args:
            qualitative: List of qualitative metric definitions
            quantitative: List of quantitative metric definitions
            
        Returns:
            Response with success message and saved contract data
            
        Raises:
            Exception: If contract creation fails
        """
        saved_contract = await self.contract_service.create_or_update_contract(
            qualitative,
            quantitative
        )
        
        return {
            "message": "Analytics contract created successfully",
            "qualAnalytics": [metric.model_dump() for metric in saved_contract.qualitative],
            "quantAnalytics": [metric.model_dump() for metric in saved_contract.quantitative]
        }

"""
Service for managing analytics contract
"""
from typing import List
from app.models.schemas import AnalyticsContract, MetricDefinition
from app.repositories.contract_repository import AnalyticsContractRepository


class AnalyticsContractService:
    """
    Service for managing analytics contract operations.
    
    Maintains consistent layering by handling business logic between
    the controller and repository layers.
    """
    
    def __init__(self, contract_repository: AnalyticsContractRepository):
        """
        Initialize the contract service.
        
        Args:
            contract_repository: Repository for contract persistence
        """
        self.contract_repository = contract_repository
    
    async def get_current_contract(self) -> AnalyticsContract:
        """
        Get the current analytics contract.
        
        Returns:
            The current analytics contract
            
        Raises:
            ValueError: If no contract exists
        """
        contract = await self.contract_repository.get_current()
        
        if not contract:
            raise ValueError("No analytics contract found")
        
        return contract
    
    async def create_or_update_contract(
        self,
        qualitative_metrics: List[MetricDefinition],
        quantitative_metrics: List[MetricDefinition]
    ) -> AnalyticsContract:
        """
        Create or update the analytics contract.
        
        Args:
            qualitative_metrics: List of qualitative metric definitions
            quantitative_metrics: List of quantitative metric definitions
            
        Returns:
            The saved analytics contract
            
        Raises:
            Exception: If contract creation/update fails
        """
        # Create new contract
        contract = AnalyticsContract(
            qualitative=qualitative_metrics,
            quantitative=quantitative_metrics
        )
        
        # Save to database
        saved_contract = await self.contract_repository.save(contract)
        
        return saved_contract

"""
Repository for analytics contract operations
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from app.models.schemas import AnalyticsContract, MetricDefinition


class AnalyticsContractRepository:
    """Repository for managing analytics contract in MongoDB"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["analyticsContract"]
    
    async def get_current(self) -> Optional[AnalyticsContract]:
        """
        Get the current analytics contract
        Returns the most recent contract
        """
        document = await self.collection.find_one(
            {},
            sort=[("_id", -1)]
        )
        
        if document:
            return AnalyticsContract(
                qualitative=document.get("qualitative", []),
                quantitative=document.get("quantitative", [])
            )
        return None
    
    async def save(self, contract: AnalyticsContract) -> AnalyticsContract:
        """
        Save a new analytics contract
        """
        document = contract.model_dump()
        await self.collection.insert_one(document)
        return contract

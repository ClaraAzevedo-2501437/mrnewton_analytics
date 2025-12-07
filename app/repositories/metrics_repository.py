"""
Repository for analytics metrics operations
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from app.models.schemas import AnalyticsMetrics
from datetime import datetime


class AnalyticsMetricsRepository:
    """Repository for managing calculated analytics metrics in MongoDB"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["analytics"]
    
    async def save(self, metrics: AnalyticsMetrics) -> AnalyticsMetrics:
        """
        Save calculated analytics metrics
        """
        document = metrics.model_dump()
        document["_calculated_at"] = datetime.utcnow()
        
        # Upsert: update if exists, insert if not
        await self.collection.update_one(
            {
                "instance_id": metrics.instance_id,
                "student_id": metrics.student_id
            },
            {"$set": document},
            upsert=True
        )
        
        return metrics
    
    async def find_by_instance_and_student(
        self,
        instance_id: str,
        student_id: str
    ) -> Optional[AnalyticsMetrics]:
        """
        Find analytics metrics for a specific instance and student
        """
        document = await self.collection.find_one({
            "instance_id": instance_id,
            "student_id": student_id
        })
        
        if document:
            # Remove MongoDB _id field
            document.pop("_id", None)
            document.pop("_calculated_at", None)
            return AnalyticsMetrics(**document)
        
        return None
    
    async def find_by_instance(self, instance_id: str) -> List[AnalyticsMetrics]:
        """
        Find all analytics metrics for an instance
        """
        cursor = self.collection.find({"instance_id": instance_id})
        results = []
        
        async for document in cursor:
            document.pop("_id", None)
            document.pop("_calculated_at", None)
            results.append(AnalyticsMetrics(**document))
        
        return results
    
    async def delete_by_instance_and_student(
        self,
        instance_id: str,
        student_id: str
    ) -> bool:
        """
        Delete analytics metrics for a specific instance and student
        """
        result = await self.collection.delete_one({
            "instance_id": instance_id,
            "student_id": student_id
        })
        
        return result.deleted_count > 0

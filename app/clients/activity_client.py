"""
HTTP client for communicating with the mrnewton-activity component
"""
import httpx
import os
from typing import Optional, List
from app.models.schemas import Submission, Activity, DeploymentInstance


class ActivityClient:
    """
    Client for interacting with the mrnewton-activity API
    """
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv(
            "ACTIVITY_API_URL",
            "http://localhost:5000/api/v1"
        )
        self.timeout = httpx.Timeout(30.0)
    
    async def get_submission(
        self,
        instance_id: str,
        student_id: str
    ) -> Optional[Submission]:
        """
        Get submission data for a specific student in an instance
        """
        url = f"{self.base_url}/submissions/instance/{instance_id}/student/{student_id}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                data = response.json()
                return Submission(**data)
            
            except httpx.HTTPError as e:
                print(f"HTTP error occurred while fetching submission: {e}")
                raise
    
    async def get_activity(self, activity_id: str) -> Optional[Activity]:
        """
        Get activity configuration by ID
        """
        url = f"{self.base_url}/config/{activity_id}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                data = response.json()
                return Activity(**data)
            
            except httpx.HTTPError as e:
                print(f"HTTP error occurred while fetching activity: {e}")
                raise
    
    async def get_instance(self, instance_id: str) -> Optional[DeploymentInstance]:
        """
        Get deployment instance by ID
        """
        url = f"{self.base_url}/deploy/{instance_id}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                data = response.json()
                return DeploymentInstance(**data)
            
            except httpx.HTTPError as e:
                print(f"HTTP error occurred while fetching instance: {e}")
                raise
    
    async def get_instance_submissions(self, instance_id: str) -> List[Submission]:
        """
        Get all submissions for an instance
        """
        url = f"{self.base_url}/submissions/instance/{instance_id}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                
                if response.status_code == 404:
                    return []
                
                response.raise_for_status()
                data = response.json()
                
                # Response format: {"count": n, "submissions": [...]}
                submissions_data = data.get("submissions", [])
                return [Submission(**sub) for sub in submissions_data]
            
            except httpx.HTTPError as e:
                print(f"HTTP error occurred while fetching instance submissions: {e}")
                raise

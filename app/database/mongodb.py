"""
MongoDB database configuration and connection management
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import os

# MongoDB connection string and database name
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://user-mrnewton:4cVtjvdfqW26Hst3@cluster0.nui5rqk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
DATABASE_NAME = "mrnewton-analytics"

# Global database client
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongodb():
    """
    Establish connection to MongoDB
    """
    global _client, _database
    _client = AsyncIOMotorClient(MONGODB_URI)
    _database = _client[DATABASE_NAME]
    print(f"Connected to MongoDB database: {DATABASE_NAME}")


async def close_mongodb_connection():
    """
    Close MongoDB connection
    """
    global _client
    if _client:
        _client.close()
        print("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the MongoDB database instance
    """
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongodb() first.")
    return _database

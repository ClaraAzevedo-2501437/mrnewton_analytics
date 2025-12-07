"""
Setup script to initialize the analytics database
"""
import asyncio
from app.database.mongodb import connect_to_mongodb, close_mongodb_connection


async def setup_database():
    """Initialize the database connection"""
    print("Connecting to MongoDB...")
    await connect_to_mongodb()
    
    print("\n✓ MongoDB connection established!")
    print("\nTo create an analytics contract, use:")
    print("  POST http://localhost:8000/api/v1/analytics/contract")
    print("\nOr use the provided analytics_contract_request.json file")
    
    await close_mongodb_connection()
    print("\n✓ Database setup complete!")


if __name__ == "__main__":
    asyncio.run(setup_database())

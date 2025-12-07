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
    
    await close_mongodb_connection()
    print("\n✓ Database setup complete!")


if __name__ == "__main__":
    asyncio.run(setup_database())

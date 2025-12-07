from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from datetime import datetime
import logging

from app.routers import analytics
from app.database.mongodb import connect_to_mongodb, close_mongodb_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MrNewton Analytics Provider API",
    description="Analytics provider for MrNewton in Inven!RA architecture. Calculates and provides quantitative and qualitative metrics from student submissions.",
    version="1.0.0",
    docs_url="/api-docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event: Connect to MongoDB
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up MrNewton Analytics API...")
    await connect_to_mongodb()
    logger.info("MongoDB connected successfully")

# Shutdown event: Close MongoDB connection
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down MrNewton Analytics API...")
    await close_mongodb_connection()
    logger.info("MongoDB connection closed")

# Request logger middleware
@app.middleware("http")
async def log_requests(request, call_next):
    timestamp = datetime.utcnow().isoformat()
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response

# Include routers
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

# Root redirect to API docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/api-docs")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "mrnewton-analytics",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

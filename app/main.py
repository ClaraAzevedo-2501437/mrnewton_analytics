from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from app.routers import analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MrNewton Analytics Provider API",
    description="Backend skeleton for MrNewton Analytics Provider in Inven!RA architecture. Provides static JSON responses for analytics endpoints.",
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

# Request logger middleware
@app.middleware("http")
async def log_requests(request, call_next):
    timestamp = datetime.utcnow().isoformat()
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response

# Include routers
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

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

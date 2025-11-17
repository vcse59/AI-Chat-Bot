"""Analytics Service Main Application"""
# Load environment variables FIRST before any local imports
from dotenv import load_dotenv
from pathlib import Path

# Load root .env first (shared config)
root_env = Path(__file__).parent.parent / ".env"
load_dotenv(root_env)

# Load local .env for service-specific overrides
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

from analytics.database.db import Base, engine
from analytics.routers import analytics

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Analytics Service",
    description="Admin-only analytics and metrics tracking for ConvoAI Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 60)
    logger.info("Analytics Service Starting Up")
    logger.info(f"AUTH_SECRET_KEY: {os.getenv('AUTH_SECRET_KEY', 'NOT SET')[:20]}...")
    logger.info(f"AUTH_SERVICE_URL: {os.getenv('AUTH_SERVICE_URL', 'NOT SET')}")
    logger.info("=" * 60)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    return response


# Include routers
app.include_router(analytics.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Analytics Service",
        "version": "1.0.0",
        "description": "Admin-only analytics and metrics tracking",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "analytics-service",
        "version": "1.0.0"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )

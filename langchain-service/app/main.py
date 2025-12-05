"""
Main FastAPI application for LangChain Workflow Service
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.api.routes import router
from app.services.chat_service_client import ChatServiceClient
from app.utils.config import get_settings
from app.utils.logging_utils import setup_logger
from app.models.schemas import HealthResponse

settings = get_settings()
logger = setup_logger(__name__, settings.LOG_LEVEL)

# Create FastAPI app
app = FastAPI(
    title="LangChain Workflow Service",
    description="Advanced AI conversation workflows using LangChain and OpenAI",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["langchain"])


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "description": "LangChain Workflow Service for ConvoAI Platform",
        "features": [
            "Simple conversation chains with full memory",
            "Structured task-specific chains (Q&A, summarization, extraction)",
            "Summary memory for long conversations",
            "AI-powered conversation summaries",
            "Integration with chat-service for message persistence"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": "/api/v1/"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Check chat service connectivity
    chat_client = ChatServiceClient()
    chat_service_healthy = await chat_client.health_check()
    await chat_client.close()
    
    return HealthResponse(
        status="healthy" if chat_service_healthy else "degraded",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        chat_service_connected=chat_service_healthy,
        openai_configured=bool(settings.OPENAI_API_KEY),
        timestamp=datetime.utcnow()
    )


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.VERSION}")
    logger.info(f"Chat Service URL: {settings.CHAT_SERVICE_URL}")
    logger.info(f"LangChain Model: {settings.LANGCHAIN_MODEL}")
    logger.info(f"OpenAI API Key configured: {bool(settings.OPENAI_API_KEY)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info(f"Shutting down {settings.SERVICE_NAME}")

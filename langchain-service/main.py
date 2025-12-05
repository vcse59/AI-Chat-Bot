"""
Application entry point
"""
import uvicorn
import os
from app.utils.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
        log_level=settings.LOG_LEVEL.lower()
    )

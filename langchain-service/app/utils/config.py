"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Service Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8004
    SERVICE_NAME: str = "langchain-service"
    VERSION: str = "3.0.0"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    
    # Service URLs
    CHAT_SERVICE_URL: str = "http://localhost:8000"
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    
    # LangChain Configuration
    LANGCHAIN_MODEL: str = "gpt-3.5-turbo"
    LANGCHAIN_TEMPERATURE: float = 0.7
    LANGCHAIN_MAX_TOKENS: int = 1000
    LANGCHAIN_VERBOSE: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

# Use DATABASE_URL from environment if available, otherwise use default path
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # Default to local database for development
    # Use absolute path relative to the service directory
    service_dir = Path(__file__).parent.parent  # chat-service directory
    data_dir = service_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "chatbot.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
# For production, you might want to use PostgreSQL:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Database dependency
def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

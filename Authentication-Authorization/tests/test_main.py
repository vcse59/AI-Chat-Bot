
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth_server.main import app, init_roles
from auth_server.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create the tables
    Base.metadata.create_all(bind=engine)
    # Initialize roles in the test database
    db = TestingSessionLocal()
    try:
        from auth_server.models.role import Role
        # Define default roles
        default_roles = ["admin", "user", "manager"]
        
        # Check and create roles if they don't exist
        for role_name in default_roles:
            if not db.query(Role).filter_by(name=role_name).first():
                db.add(Role(name=role_name))
        
        db.commit()
    finally:
        db.close()
    yield
    # Drop the tables
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

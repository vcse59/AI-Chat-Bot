# Load environment variables FIRST before any local imports
from dotenv import load_dotenv
from pathlib import Path

# Load root .env first (shared config)
root_env = Path(__file__).parent.parent.parent / ".env"
load_dotenv(root_env)

# Load local .env for service-specific overrides
load_dotenv(Path(__file__).parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routers import auth, users, roles
from .models.role import Role
from .models.user import User
from .security.auth import get_password_hash
from .database import engine, SessionLocal, Base, run_all_migrations

# Create database tables
Base.metadata.create_all(bind=engine)

# Run database migrations for existing databases
run_all_migrations()

# Initialize default roles
def init_roles():
    """Initialize default roles if they don't exist."""
    db = SessionLocal()
    try:
        # Define default roles
        default_roles = ["admin", "user", "manager"]
        
        # Check and create roles if they don't exist
        for role_name in default_roles:
            if not db.query(Role).filter_by(name=role_name).first():
                print(f"Creating role: {role_name}")
                db.add(Role(name=role_name))
        
        db.commit()
    except Exception as e:
        print(f"Error initializing roles: {e}")
        db.rollback()
    finally:
        db.close()

def init_admin_user():
    """Initialize default admin user if it doesn't exist."""
    db = SessionLocal()
    try:
        # Get admin credentials from environment variables or use defaults
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        
        # Check if admin user already exists
        existing_admin = db.query(User).filter_by(username=admin_username).first()
        if existing_admin:
            print(f"Admin user '{admin_username}' already exists")
            return
        
        # Create admin user
        print(f"Creating admin user: {admin_username}")
        admin_user = User(
            username=admin_username,
            email=admin_email,
            full_name="System Administrator",
            hashed_password=get_password_hash(admin_password),
            is_active=True
        )
        db.add(admin_user)
        db.flush()  # Get the user ID
        
        # Assign admin and user roles
        admin_role = db.query(Role).filter_by(name="admin").first()
        user_role = db.query(Role).filter_by(name="user").first()
        
        if admin_role:
            admin_user.roles.append(admin_role)
            print(f"Assigned 'admin' role to {admin_username}")
        
        if user_role:
            admin_user.roles.append(user_role)
            print(f"Assigned 'user' role to {admin_username}")
        
        db.commit()
        print(f"✅ Admin user '{admin_username}' created successfully!")
        print(f"   Username: {admin_username}")
        print(f"   Email: {admin_email}")
        
    except Exception as e:
        print(f"Error initializing admin user: {e}")
        db.rollback()
    finally:
        db.close()

# Initialize roles and admin user
init_roles()
init_admin_user()

# Create FastAPI app
app = FastAPI(
    title="Authentication & Authorization Server",
    description="OAuth 2.0 based authentication and authorization service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-server"}

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)

def start():
    """Entry point for the application."""
    import uvicorn
    import sys
    sys.exit(uvicorn.run("auth_server.main:app", host="0.0.0.0", port=8000, reload=True))

if __name__ == "__main__":
    start()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, roles
from .models.role import Role
from .database import engine, SessionLocal, Base

# Create database tables
Base.metadata.create_all(bind=engine)

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

# Initialize roles
init_roles()

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
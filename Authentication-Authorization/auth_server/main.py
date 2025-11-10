from fastapi import FastAPI
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
app = FastAPI()

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
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
import httpx
import asyncio
import os
import logging

from ..models.user import User
from ..models.role import Role
from ..security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, get_current_user
from .. import schemas
from ..database import get_db

logger = logging.getLogger(__name__)

ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8002")

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    # Check user credentials
    user = db.query(User).options(joinedload(User.roles)).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "roles": [role.name for role in user.roles]},
        expires_delta=access_token_expires
    )
    
    # Track login activity
    asyncio.create_task(_track_user_activity(
        user_id=user.id,
        username=user.username,
        activity_type="login",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    ))
    
    # Sync user profile with analytics (ensure role is up to date)
    user_role = "admin" if any(role.name == "admin" for role in user.roles) else "user"
    asyncio.create_task(_sync_user_profile(
        user_id=user.id,
        username=user.username,
        role=user_role,
        email=user.email
    ))
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(
    user_data: schemas.UserCreate,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Public endpoint to register a new regular user."""
    # Check if user already exists
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user with "user" role only (ignore any roles in request)
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    # Assign default "user" role
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        db_user.roles.append(user_role)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Track registration activity
    asyncio.create_task(_track_user_activity(
        user_id=db_user.id,
        username=db_user.username,
        activity_type="register",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    ))
    
    # Sync user profile with analytics (including role)
    asyncio.create_task(_sync_user_profile(
        user_id=db_user.id,
        username=db_user.username,
        role="user",
        email=db_user.email
    ))
    
    return {"message": "User registered successfully"}

@router.post("/register-admin", response_model=schemas.UserResponse)
async def register_admin_user(
    user_data: schemas.UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint to register a new admin user."""
    # Verify admin access
    user_roles = [role.name for role in current_user.roles] if current_user.roles else []
    if "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create admin accounts"
        )
    
    # Check if user already exists
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Create new admin user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    # Assign both "admin" and "user" roles
    for role_name in ["admin", "user"]:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role:
            db_user.roles.append(role)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Sync admin user profile with analytics (including admin role)
    asyncio.create_task(_sync_user_profile(
        user_id=db_user.id,
        username=db_user.username,
        role="admin",
        email=db_user.email
    ))
    
    return {"message": "Admin user created successfully"}

async def _track_user_activity(user_id: str, username: str, activity_type: str,
                                ip_address: str = None, user_agent: str = None):
    """Helper function to track user activity to analytics service"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/track/activity-public",
                json={
                    "user_id": user_id,
                    "username": username,
                    "activity_type": activity_type,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "extra_data": {}
                }
            )
    except Exception as e:
        logger.debug(f"Analytics tracking failed (non-critical): {e}")


async def _sync_user_profile(user_id: str, username: str, role: str = None, email: str = None):
    """Helper function to sync user profile with analytics service"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/users/sync-profile",
                params={
                    "user_id": user_id,
                    "username": username,
                    "role": role,
                    "email": email
                }
            )
    except Exception as e:
        logger.debug(f"User profile sync failed (non-critical): {e}")


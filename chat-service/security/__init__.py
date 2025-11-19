"""
OAuth 2.0 Authentication Module for OpenAI Web Service

This module integrates with the Authorization Server for user authentication
"""
import os
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import logging

logger = logging.getLogger(__name__)

# Configuration
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(

    tokenUrl=f"{AUTH_SERVICE_URL}/auth/token",
    auto_error=False  # Allow endpoints to be optional
)

class CurrentUser:
    """Current authenticated user model"""
    def __init__(self, username: str, user_id: Optional[str] = None, roles: List[str] = None, token: Optional[str] = None):
        self.username = username
        self.user_id = user_id
        self.roles = roles or []
        self.token = token
        self.auth_service_url = AUTH_SERVICE_URL
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        return role in self.roles
    
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return "admin" in self.roles

def verify_token(token: str) -> dict:
    """
    Verify JWT token and return payload
    
    Args:
        token: JWT token string
        
    Returns:
        Token payload dict
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[CurrentUser]:
    """
    Get current authenticated user from JWT token (Optional)
    
    Args:
        token: JWT token from request header
        
    Returns:
        CurrentUser object or None if no token provided
        
    Raises:
        HTTPException: If token is invalid
    """
    if not token:
        return None
    
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        roles: List[str] = payload.get("roles", [])
        user_id: str = payload.get("user_id")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return CurrentUser(username=username, user_id=user_id, roles=roles, token=token)
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(
    current_user: Optional[CurrentUser] = Depends(get_current_user)
) -> CurrentUser:
    """
    Get current authenticated user (Required)
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        CurrentUser object
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

async def require_role(required_role: str):
    """
    Dependency to require a specific role
    
    Usage:
        @app.get("/admin-only", dependencies=[Depends(require_role("admin"))])
    
    Args:
        required_role: Role name required for access
        
    Returns:
        Dependency function
    """
    async def role_checker(current_user: CurrentUser = Depends(get_current_active_user)):
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        return current_user
    return role_checker

async def require_admin(current_user: CurrentUser = Depends(get_current_active_user)):
    """
    Dependency to require admin role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        CurrentUser if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required"
        )
    return current_user

def get_user_id_from_request(
    current_user: Optional[CurrentUser] = Depends(get_current_user)
) -> Optional[str]:
    """
    Extract user ID from authenticated request
    
    Args:
        current_user: Current user from token
        
    Returns:
        User ID string or None if not authenticated
    """
    if current_user:
        return current_user.user_id
    return None

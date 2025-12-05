"""Authentication and authorization for analytics service"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import os
import requests
import logging
import sys

# Configure logging to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

security = HTTPBearer()

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-server:8001")


class CurrentUser:
    """Current authenticated user information"""
    def __init__(self, user_id: str, username: str, roles: list[str]):
        self.user_id = user_id
        self.username = username
        self.roles = roles

    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return "admin" in self.roles


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Validate JWT token and extract user information.
    
    Args:
        credentials: HTTP Authorization credentials with Bearer token
        
    Returns:
        CurrentUser: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        logger.info("Attempting to decode token with configured secret key...")
        logger.info(f"Token (first 20 chars): {token[:20]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Token decoded successfully. Payload: {payload}")
        user_id: str = payload.get("sub")
        username: str = payload.get("sub")  # Use 'sub' for username as well
        roles: list = payload.get("roles", [])
        logger.info(f"Extracted - user_id: {user_id}, username: {username}, roles: {roles}")
        
        if user_id is None:
            logger.warning("user_id is None, raising exception")
            raise credentials_exception
            
        return CurrentUser(user_id=user_id, username=username, roles=roles)
        
    except JWTError as e:
        logger.error(f"JWTError occurred: {str(e)}")
        logger.error(f"Token that failed: {token[:50]}...")
        logger.error("A secret key was used for token validation (key not shown for security).")
        raise credentials_exception


async def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    Dependency that requires admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        CurrentUser: Current user if they have admin role
        
    Raises:
        HTTPException: If user does not have admin role
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. You do not have permission to access this resource."
        )
    return current_user


async def verify_token_with_auth_service(token: str) -> Optional[dict]:
    """
    Verify token with the auth service (alternative method).
    
    Args:
        token: JWT token to verify
        
    Returns:
        User information if token is valid, None otherwise
    """
    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

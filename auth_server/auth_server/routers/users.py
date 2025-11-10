from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..models.user import User
from ..models.role import Role
from .. import schemas
from ..database import get_db
from ..security import get_password_hash, oauth2_scheme, verify_token

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=schemas.UserResponse)
async def create_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # Check if user already exists
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    # Add roles
    for role_name in user_data.roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role:
            db_user.roles.append(role)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully"}

@router.get("/", response_model=schemas.UserList)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Verify admin access
    payload = verify_token(current_token)
    current_user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not current_user or "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can list all users"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return {
        "users": [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "roles": [role.name for role in user.roles]
        } for user in users]
    }

@router.get("/me", response_model=schemas.UserInDB)
async def read_users_me(
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Verify token
    payload = verify_token(current_token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Get user from database with roles eagerly loaded
    user = db.query(User).options(joinedload(User.roles)).filter(
        User.username == username
    ).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "roles": [role.name for role in user.roles]
    }

@router.get("/{username}", response_model=schemas.UserInDB)
async def read_user(
    username: str,
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Verify access (admin or self)
    payload = verify_token(current_token)
    current_user = db.query(User).filter(User.username == payload.get("sub")).first()
    is_admin = current_user and "admin" in [role.name for role in current_user.roles]
    
    if not is_admin and payload.get("sub") != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "roles": [role.name for role in user.roles]
    }

@router.put("/{username}", response_model=schemas.UserResponse)
async def update_user(
    username: str,
    user_update: schemas.UserUpdate,
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Verify access (admin or self)
    payload = verify_token(current_token)
    current_user = db.query(User).filter(User.username == payload.get("sub")).first()
    is_admin = current_user and "admin" in [role.name for role in current_user.roles]
    
    if not is_admin and payload.get("sub") != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)
    if user_update.is_active is not None and is_admin:  # Only admin can change active status
        user.is_active = user_update.is_active
    
    db.commit()
    return {"message": "User updated successfully"}

@router.delete("/{username}", response_model=schemas.UserResponse)
async def delete_user(
    username: str,
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Verify admin access
    payload = verify_token(current_token)
    current_user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not current_user or "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete users"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
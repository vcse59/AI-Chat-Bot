from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..models.user import User
from ..models.role import Role
from .. import schemas
from ..database import get_db
from ..security import get_password_hash, get_current_user

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
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    # Add roles - ensure at least "user" role is assigned
    roles_to_assign = user_data.roles if user_data.roles else ["user"]
    for role_name in roles_to_assign:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role:
            db_user.roles.append(role)
    
    # If no roles were assigned (e.g., all role names were invalid), assign "user" role
    if not db_user.roles:
        default_role = db.query(Role).filter(Role.name == "user").first()
        if default_role:
            db_user.roles.append(default_role)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully"}

@router.get("/", response_model=schemas.UserList)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify admin access - ensure roles are loaded
    user_roles = [role.name for role in current_user.roles] if current_user.roles else []
    if not current_user or "admin" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can list all users"
        )
    
    users = db.query(User).options(joinedload(User.roles)).offset(skip).limit(limit).all()
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
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{username}", response_model=schemas.UserInDB)
async def read_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify access (admin or self) - ensure roles are loaded
    user_roles = [role.name for role in current_user.roles] if current_user.roles else []
    is_admin = "admin" in user_roles
    
    if not is_admin and current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = db.query(User).options(joinedload(User.roles)).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.put("/{username}", response_model=schemas.UserResponse)
async def update_user(
    username: str,
    user_update: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify access (admin or self) - ensure roles are loaded
    user_roles = [role.name for role in current_user.roles] if current_user.roles else []
    is_admin = "admin" in user_roles
    
    if not is_admin and current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)
    if user_update.is_active is not None and is_admin:  # Only admin can change active status
        user.is_active = user_update.is_active
    if user_update.theme_preference is not None:
        user.theme_preference = user_update.theme_preference
    
    db.commit()
    return {"message": "User updated successfully"}

@router.put("/me/theme", response_model=schemas.UserResponse)
async def update_my_theme(
    theme_update: schemas.ThemeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's theme preference."""
    # Validate theme value
    if theme_update.theme_preference not in ["dark", "light"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Theme must be 'dark' or 'light'"
        )
    
    user = db.query(User).filter(User.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.theme_preference = theme_update.theme_preference
    db.commit()
    return {"message": "Theme updated successfully"}

@router.get("/me/theme")
async def get_my_theme(current_user: User = Depends(get_current_user)):
    """Get the current user's theme preference."""
    return {"theme_preference": current_user.theme_preference}

@router.delete("/{username}", response_model=schemas.UserResponse)
async def delete_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify admin access - ensure roles are loaded
    user_roles = [role.name for role in current_user.roles] if current_user.roles else []
    if "admin" not in user_roles:
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
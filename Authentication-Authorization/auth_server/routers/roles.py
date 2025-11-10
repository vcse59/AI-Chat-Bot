from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..models.user import User
from ..models.role import Role
from ..database import get_db
from ..security import oauth2_scheme, verify_token

router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)

@router.put("/{username}", response_model=schemas.UserResponse)
async def update_user_roles(
    username: str,
    roles_update: schemas.UpdateUserRoles,
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Verify token and get current user
    payload = verify_token(current_token)
    current_username = payload.get("sub")
    if not current_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # Check if current user has admin role
    current_user = db.query(User).filter(User.username == current_username).first()
    if not current_user or "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update user roles"
        )

    # Get target user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Clear existing roles
    user.roles = []

    # Add new roles
    for role_name in roles_update.roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role:
            user.roles.append(role)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role_name}' does not exist"
            )

    db.commit()
    return {"message": f"Roles updated successfully for user {username}"}
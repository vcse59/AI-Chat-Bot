from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload

from ..models.user import User
from ..security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .. import schemas
from ..database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
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
    return {"access_token": access_token, "token_type": "bearer"}
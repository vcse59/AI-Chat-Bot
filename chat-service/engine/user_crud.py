"""
User-specific CRUD operations using utility functions
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from engine import models, schemas
from utilities.database_utils import (
    get_entity_by_id, get_entity_by_field, get_entities_paginated,
    create_entity, update_entity, delete_entity, exists_by_field
)
from utilities.validation_utils import is_valid_email, validate_username
from utilities.logging_utils import log_database_operation
from utilities.hash_utils import generate_user_hash, validate_user_hash
import logging

logger = logging.getLogger(__name__)

def get_user(db: Session, user_id: str) -> Optional[models.User]:
    """Get user by ID"""
    user = get_entity_by_id(db, models.User, user_id)
    log_database_operation(logger, "read", "users", user_id, success=user is not None)
    return user

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    user = get_entity_by_field(db, models.User, "email", email)
    log_database_operation(logger, "read", "users", success=user is not None)
    return user

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username"""
    user = get_entity_by_field(db, models.User, "username", username)
    log_database_operation(logger, "read", "users", success=user is not None)
    return user

def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[models.User]:
    """Get users with pagination and filtering"""
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    
    users = get_entities_paginated(
        db, 
        models.User, 
        skip=skip, 
        limit=limit, 
        filters=filters,
        order_by="created_at"
    )
    
    log_database_operation(logger, "read", "users", success=True)
    return users

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create new user with validation"""
    try:
        # Validate email format
        if not is_valid_email(user.email):
            raise ValueError("Invalid email format")
        
        # Validate username format
        if not validate_username(user.username):
            raise ValueError("Invalid username format")
        
        # Check if email already exists
        if exists_by_field(db, models.User, "email", user.email):
            raise ValueError("Email already registered")
        
        # Check if username already exists
        if exists_by_field(db, models.User, "username", user.username):
            raise ValueError("Username already taken")
        
        # Generate hash ID for user
        user_id = generate_user_hash(user.email, user.username)
        
        # Create user with hash ID
        user_data = user.model_dump()
        user_data['id'] = user_id
        db_user = models.User(**user_data)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        log_database_operation(
            logger, "create", "users", db_user.id, success=True
        )
        return db_user
        
    except Exception as e:
        log_database_operation(
            logger, "create", "users", error=str(e), success=False
        )
        raise

def update_user(db: Session, user_id: str, user: schemas.UserUpdate) -> Optional[models.User]:
    """Update user with validation"""
    try:
        # Get existing user
        db_user = get_entity_by_id(db, models.User, user_id)
        if not db_user:
            return None
        
        # Prepare update data
        update_data = user.model_dump(exclude_unset=True)
        
        # Validate email if being updated
        if "email" in update_data:
            if not is_valid_email(update_data["email"]):
                raise ValueError("Invalid email format")
            
            # Check if new email is already taken by another user
            existing_user = get_user_by_email(db, update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already registered")
        
        # Validate username if being updated
        if "username" in update_data:
            if not validate_username(update_data["username"]):
                raise ValueError("Invalid username format")
            
            # Check if new username is already taken by another user
            existing_user = get_user_by_username(db, update_data["username"])
            if existing_user and existing_user.id != user_id:
                raise ValueError("Username already taken")
        
        # Update user
        updated_user = update_entity(db, db_user, update_data)
        
        log_database_operation(
            logger, "update", "users", user_id, success=True
        )
        return updated_user
        
    except Exception as e:
        log_database_operation(
            logger, "update", "users", user_id, error=str(e), success=False
        )
        raise

def delete_user(db: Session, user_id: str) -> bool:
    """Delete user"""
    try:
        success = delete_entity(db, models.User, user_id)
        log_database_operation(
            logger, "delete", "users", user_id, success=success
        )
        return success
        
    except Exception as e:
        log_database_operation(
            logger, "delete", "users", user_id, error=str(e), success=False
        )
        return False

def get_user_with_items(db: Session, user_id: str) -> Optional[models.User]:
    """Get user with their items (using relationship)"""
    user = get_entity_by_id(db, models.User, user_id)
    if user:
        # SQLAlchemy will lazy load the items relationship
        log_database_operation(logger, "read", "users", user_id, success=True)
    return user

def search_users(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Search users by username, email, or full name"""
    from utilities.database_utils import search_entities
    
    search_fields = ["username", "email", "full_name"]
    users = search_entities(db, models.User, search_fields, query, skip, limit)
    
    log_database_operation(logger, "search", "users", success=True)
    return users
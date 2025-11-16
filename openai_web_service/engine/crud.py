"""
Main CRUD module that imports and re-exports all CRUD operations
This maintains backward compatibility while using the new modular structure
"""

# Import all CRUD operations from specialized modules
from engine.user_crud import (
    get_user, get_user_by_email, get_user_by_username, get_users,
    create_user, update_user, delete_user, get_user_with_items,
    search_users
)

from engine.item_crud import (
    get_item, get_items, get_available_items, create_item,
    update_item, delete_item, search_items, get_items_by_title,
    get_items_by_owner, get_items_by_price_range
)

from engine.conversation_crud import (
    create_conversation, get_conversation, get_conversations,
    get_conversation_with_messages, update_conversation, end_conversation,
    delete_conversation, create_message, get_conversation_messages,
    get_message, delete_message, get_recent_messages, get_conversation_stats
)

# Category CRUD operations (keeping these here for now since they're simpler)
from sqlalchemy.orm import Session
from typing import List, Optional
from engine import models, schemas

def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    db_category = models.Category(
        name=category.name,
        description=category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate) -> Optional[models.Category]:
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        update_data = category.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> bool:
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False
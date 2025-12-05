"""
Item-specific CRUD operations using utility functions
"""
# pylint: disable=logging-fstring-interpolation,broad-exception-caught
from sqlalchemy.orm import Session
from typing import List, Optional
from engine import models, schemas
from utilities.database_utils import (
    get_entity_by_id, get_entities_paginated, create_entity, 
    update_entity, delete_entity, search_entities
)
from utilities.validation_utils import validate_price, sanitize_string
from utilities.logging_utils import log_database_operation
import logging

logger = logging.getLogger(__name__)

def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    """Get item by ID"""
    item = get_entity_by_id(db, models.Item, item_id)
    log_database_operation(logger, "read", "items", item_id, success=item is not None)
    return item

def get_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    owner_id: Optional[int] = None,
    is_available: Optional[bool] = None
) -> List[models.Item]:
    """Get items with pagination and filtering"""
    filters = {}
    if owner_id is not None:
        filters["owner_id"] = owner_id
    if is_available is not None:
        filters["is_available"] = is_available
    
    items = get_entities_paginated(
        db, 
        models.Item, 
        skip=skip, 
        limit=limit, 
        filters=filters,
        order_by="created_at"
    )
    
    log_database_operation(logger, "read", "items", success=True)
    return items

def get_available_items(db: Session, skip: int = 0, limit: int = 100) -> List[models.Item]:
    """Get only available items"""
    return get_items(db, skip, limit, is_available=True)

def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    """Create new item with validation"""
    try:
        # Validate and sanitize title
        title = sanitize_string(
            item.title, 
            max_length=255, 
            min_length=1,
            strip_whitespace=True
        )
        
        # Validate price if provided
        if item.price is not None and not validate_price(item.price):
            raise ValueError("Price must be a non-negative number")
        
        # Sanitize description if provided
        description = None
        if item.description:
            description = sanitize_string(
                item.description,
                max_length=2000,
                strip_whitespace=True
            )
        
        # Create item with sanitized data
        sanitized_item = schemas.ItemCreate(
            title=title,
            description=description,
            price=item.price,
            is_available=item.is_available,
            owner_id=item.owner_id
        )
        
        db_item = create_entity(db, models.Item, sanitized_item)
        
        log_database_operation(
            logger, "create", "items", db_item.id, success=True
        )
        return db_item
        
    except Exception as e:
        log_database_operation(
            logger, "create", "items", error=str(e), success=False
        )
        raise

def update_item(db: Session, item_id: int, item: schemas.ItemUpdate) -> Optional[models.Item]:
    """Update item with validation"""
    try:
        # Get existing item
        db_item = get_entity_by_id(db, models.Item, item_id)
        if not db_item:
            return None
        
        # Prepare update data with validation
        update_data = {}
        
        # Validate and sanitize title if being updated
        if item.title is not None:
            update_data["title"] = sanitize_string(
                item.title,
                max_length=255,
                min_length=1,
                strip_whitespace=True
            )
        
        # Validate and sanitize description if being updated
        if item.description is not None:
            update_data["description"] = sanitize_string(
                item.description,
                max_length=2000,
                strip_whitespace=True
            ) if item.description else None
        
        # Validate price if being updated
        if item.price is not None:
            if not validate_price(item.price):
                raise ValueError("Price must be a non-negative number")
            update_data["price"] = item.price
        
        # Update availability if specified
        if item.is_available is not None:
            update_data["is_available"] = item.is_available
        
        # Update item
        updated_item = update_entity(db, db_item, update_data)
        
        log_database_operation(
            logger, "update", "items", item_id, success=True
        )
        return updated_item
        
    except Exception as e:
        log_database_operation(
            logger, "update", "items", item_id, error=str(e), success=False
        )
        raise

def delete_item(db: Session, item_id: int) -> bool:
    """Delete item"""
    try:
        success = delete_entity(db, models.Item, item_id)
        log_database_operation(
            logger, "delete", "items", item_id, success=success
        )
        return success
        
    except Exception as e:
        log_database_operation(
            logger, "delete", "items", item_id, error=str(e), success=False
        )
        return False

def search_items(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[models.Item]:
    """Search items by title or description"""
    try:
        # Validate search query
        from utilities.validation_utils import validate_search_query
        sanitized_query = validate_search_query(query)
        
        search_fields = ["title", "description"]
        items = search_entities(db, models.Item, search_fields, sanitized_query, skip, limit)
        
        log_database_operation(logger, "search", "items", success=True)
        return items
        
    except Exception as e:
        log_database_operation(
            logger, "search", "items", error=str(e), success=False
        )
        raise

def get_items_by_title(db: Session, title: str) -> List[models.Item]:
    """Get items matching title (exact or partial)"""
    try:
        sanitized_title = sanitize_string(title, strip_whitespace=True)
        items = search_entities(db, models.Item, ["title"], sanitized_title, 0, 100)
        
        log_database_operation(logger, "read", "items", success=True)
        return items
        
    except Exception as e:
        log_database_operation(
            logger, "read", "items", error=str(e), success=False
        )
        return []

def get_items_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[models.Item]:
    """Get items belonging to a specific owner"""
    return get_items(db, skip, limit, owner_id=owner_id)

def get_items_by_price_range(
    db: Session, 
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[models.Item]:
    """Get items within a price range"""
    try:
        query = db.query(models.Item)
        
        if min_price is not None:
            if not validate_price(min_price):
                raise ValueError("Minimum price must be non-negative")
            query = query.filter(models.Item.price >= min_price)
        
        if max_price is not None:
            if not validate_price(max_price):
                raise ValueError("Maximum price must be non-negative")
            query = query.filter(models.Item.price <= max_price)
        
        items = query.offset(skip).limit(limit).all()
        
        log_database_operation(logger, "read", "items", success=True)
        return items
        
    except Exception as e:
        log_database_operation(
            logger, "read", "items", error=str(e), success=False
        )
        raise
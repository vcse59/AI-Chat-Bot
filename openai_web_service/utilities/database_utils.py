"""
Database utility functions for common database operations
"""
from sqlalchemy.orm import Session
from typing import TypeVar, Type, Optional, List, Dict, Any, Union
from pydantic import BaseModel

# Type variables for generic functions
ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType", bound=BaseModel)

def get_entity_by_id(
    db: Session, 
    model: Type[ModelType], 
    entity_id: Union[int, str]
) -> Optional[ModelType]:
    """
    Generic function to get an entity by ID
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        entity_id: Entity ID to search for
        
    Returns:
        Entity instance or None if not found
    """
    return db.query(model).filter(model.id == entity_id).first()

def get_entity_by_field(
    db: Session, 
    model: Type[ModelType], 
    field_name: str, 
    field_value: Any
) -> Optional[ModelType]:
    """
    Generic function to get an entity by any field
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        field_name: Name of the field to filter by
        field_value: Value to search for
        
    Returns:
        Entity instance or None if not found
    """
    field = getattr(model, field_name)
    return db.query(model).filter(field == field_value).first()

def get_entities_paginated(
    db: Session, 
    model: Type[ModelType], 
    skip: int = 0, 
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None
) -> List[ModelType]:
    """
    Generic function to get entities with pagination and filtering
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        skip: Number of records to skip
        limit: Maximum number of records to return
        filters: Optional dictionary of field filters
        order_by: Optional field name to order by
        
    Returns:
        List of entity instances
    """
    query = db.query(model)
    
    # Apply filters
    if filters:
        for field_name, field_value in filters.items():
            if hasattr(model, field_name) and field_value is not None:
                field = getattr(model, field_name)
                query = query.filter(field == field_value)
    
    # Apply ordering
    if order_by and hasattr(model, order_by):
        order_field = getattr(model, order_by)
        query = query.order_by(order_field)
    
    return query.offset(skip).limit(limit).all()

def create_entity(
    db: Session, 
    model: Type[ModelType], 
    schema_data: SchemaType
) -> ModelType:
    """
    Generic function to create an entity
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        schema_data: Pydantic schema with data to create
        
    Returns:
        Created entity instance
    """
    # Convert schema to dict and create model instance
    create_data = schema_data.model_dump(exclude_unset=True)
    db_entity = model(**create_data)
    
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity

def update_entity(
    db: Session, 
    db_entity: ModelType, 
    update_data: Dict[str, Any]
) -> ModelType:
    """
    Generic function to update an entity
    
    Args:
        db: Database session
        db_entity: Existing entity instance
        update_data: Dictionary of fields to update
        
    Returns:
        Updated entity instance
    """
    for field, value in update_data.items():
        if hasattr(db_entity, field):
            setattr(db_entity, field, value)
    
    db.commit()
    db.refresh(db_entity)
    return db_entity

def delete_entity(
    db: Session, 
    model: Type[ModelType], 
    entity_id: Union[int, str]
) -> bool:
    """
    Generic function to delete an entity by ID
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        entity_id: ID of entity to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_entity = db.query(model).filter(model.id == entity_id).first()
    if db_entity:
        db.delete(db_entity)
        db.commit()
        return True
    return False

def search_entities(
    db: Session, 
    model: Type[ModelType], 
    search_fields: List[str], 
    query: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[ModelType]:
    """
    Generic function to search entities across multiple text fields
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        search_fields: List of field names to search in
        query: Search query string
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of matching entity instances
    """
    db_query = db.query(model)
    
    # Build OR conditions for each search field
    conditions = []
    for field_name in search_fields:
        if hasattr(model, field_name):
            field = getattr(model, field_name)
            # Check if field supports contains (text fields)
            if hasattr(field.property.columns[0].type, 'length'):
                conditions.append(field.contains(query))
    
    if conditions:
        from sqlalchemy import or_
        db_query = db_query.filter(or_(*conditions))
    
    return db_query.offset(skip).limit(limit).all()

def count_entities(
    db: Session, 
    model: Type[ModelType], 
    filters: Optional[Dict[str, Any]] = None
) -> int:
    """
    Count entities with optional filtering
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        filters: Optional dictionary of field filters
        
    Returns:
        Count of matching entities
    """
    query = db.query(model)
    
    # Apply filters
    if filters:
        for field_name, field_value in filters.items():
            if hasattr(model, field_name) and field_value is not None:
                field = getattr(model, field_name)
                query = query.filter(field == field_value)
    
    return query.count()

def batch_create_entities(
    db: Session, 
    model: Type[ModelType], 
    entities_data: List[Dict[str, Any]]
) -> List[ModelType]:
    """
    Create multiple entities in a single transaction
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        entities_data: List of dictionaries with entity data
        
    Returns:
        List of created entity instances
    """
    db_entities = []
    for entity_data in entities_data:
        db_entity = model(**entity_data)
        db_entities.append(db_entity)
        db.add(db_entity)
    
    db.commit()
    
    # Refresh all entities
    for db_entity in db_entities:
        db.refresh(db_entity)
    
    return db_entities

def exists_by_field(
    db: Session, 
    model: Type[ModelType], 
    field_name: str, 
    field_value: Any
) -> bool:
    """
    Check if an entity exists by field value
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        field_name: Name of the field to check
        field_value: Value to check for
        
    Returns:
        True if entity exists, False otherwise
    """
    field = getattr(model, field_name)
    return db.query(model).filter(field == field_value).first() is not None
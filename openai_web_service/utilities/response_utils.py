"""
Response utility functions for formatting API responses
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel

def create_success_response(
    data: Any = None, 
    message: str = "Success", 
    status_code: int = 200
) -> Dict[str, Any]:
    """
    Create a standardized success response
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        Standardized success response dictionary
    """
    response = {
        "success": True,
        "message": message,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    return response

def create_error_response(
    error: str, 
    status_code: int = 400, 
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        error: Error message
        status_code: HTTP status code
        error_code: Optional error code for client handling
        details: Optional additional error details
        
    Returns:
        Standardized error response dictionary
    """
    response = {
        "success": False,
        "error": error,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if error_code:
        response["error_code"] = error_code
    
    if details:
        response["details"] = details
    
    return response

def create_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    size: int,
    message: str = "Success"
) -> Dict[str, Any]:
    """
    Create a paginated response
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number (0-indexed)
        size: Page size
        message: Success message
        
    Returns:
        Paginated response dictionary
    """
    total_pages = (total + size - 1) // size if size > 0 else 0
    
    return create_success_response(
        data={
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "size": size,
                "pages": total_pages,
                "has_next": page < total_pages - 1,
                "has_previous": page > 0
            }
        },
        message=message
    )

def serialize_model(model_instance: Any) -> Dict[str, Any]:
    """
    Serialize a SQLAlchemy model instance to dictionary
    
    Args:
        model_instance: SQLAlchemy model instance
        
    Returns:
        Dictionary representation of the model
    """
    if hasattr(model_instance, '__dict__'):
        result = {}
        for key, value in model_instance.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif hasattr(value, '__dict__'):
                    # Handle nested models
                    result[key] = serialize_model(value)
                else:
                    result[key] = value
        return result
    return model_instance

def serialize_models_list(models_list: List[Any]) -> List[Dict[str, Any]]:
    """
    Serialize a list of SQLAlchemy model instances
    
    Args:
        models_list: List of SQLAlchemy model instances
        
    Returns:
        List of dictionary representations
    """
    return [serialize_model(model) for model in models_list]

def format_validation_errors(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format Pydantic validation errors for API response
    
    Args:
        errors: List of Pydantic validation errors
        
    Returns:
        Formatted error response
    """
    formatted_errors = {}
    
    for error in errors:
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors[field_path] = {
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        }
    
    return create_error_response(
        error="Validation failed",
        status_code=422,
        error_code="VALIDATION_ERROR",
        details={"field_errors": formatted_errors}
    )

def create_websocket_response(
    type_name: str,
    success: bool,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized WebSocket response
    
    Args:
        type_name: Response type identifier
        success: Whether the operation was successful
        data: Optional response data
        error: Optional error message
        
    Returns:
        WebSocket response dictionary
    """
    response = {
        "type": type_name,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if success and data is not None:
        response["data"] = data
    
    if not success and error:
        response["error"] = error
    
    return response

def format_model_for_api(
    model_instance: Any,
    exclude_fields: Optional[List[str]] = None,
    include_relationships: bool = False
) -> Dict[str, Any]:
    """
    Format a model instance for API output with field control
    
    Args:
        model_instance: SQLAlchemy model instance
        exclude_fields: List of fields to exclude from output
        include_relationships: Whether to include relationship data
        
    Returns:
        Formatted dictionary for API response
    """
    if not model_instance:
        return {}
    
    exclude_fields = exclude_fields or []
    result = {}
    
    # Get all columns
    if hasattr(model_instance, '__table__'):
        for column in model_instance.__table__.columns:
            field_name = column.name
            if field_name not in exclude_fields:
                value = getattr(model_instance, field_name)
                if isinstance(value, datetime):
                    result[field_name] = value.isoformat()
                else:
                    result[field_name] = value
    
    # Include relationships if requested
    if include_relationships and hasattr(model_instance, '__mapper__'):
        for relationship in model_instance.__mapper__.relationships:
            rel_name = relationship.key
            if rel_name not in exclude_fields:
                rel_value = getattr(model_instance, rel_name)
                if rel_value is not None:
                    if hasattr(rel_value, '__iter__') and not isinstance(rel_value, str):
                        # Handle collections
                        result[rel_name] = [
                            format_model_for_api(item, exclude_fields, False) 
                            for item in rel_value
                        ]
                    else:
                        # Handle single relationship
                        result[rel_name] = format_model_for_api(
                            rel_value, exclude_fields, False
                        )
    
    return result

def create_health_check_response(
    status: str = "healthy",
    checks: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a health check response
    
    Args:
        status: Overall health status
        checks: Dictionary of individual health checks
        
    Returns:
        Health check response dictionary
    """
    response = {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"  # Could be made configurable
    }
    
    if checks:
        response["checks"] = checks
    
    return response

def format_exception_response(
    exception: Exception,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """
    Format an exception for API error response
    
    Args:
        exception: Exception instance
        include_traceback: Whether to include full traceback (for debugging)
        
    Returns:
        Formatted error response
    """
    response = create_error_response(
        error=str(exception),
        status_code=500,
        error_code=type(exception).__name__
    )
    
    if include_traceback:
        import traceback
        response["details"] = {
            "traceback": traceback.format_exc()
        }
    
    return response
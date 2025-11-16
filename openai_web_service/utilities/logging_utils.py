"""
Logging utility functions for consistent logging across the application
"""
import logging
import sys
from typing import Optional, Dict, Any, Union
from datetime import datetime
import json

def setup_logger(
    name: str,
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    include_timestamp: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent formatting
    
    Args:
        name: Logger name
        level: Logging level
        format_string: Custom format string
        include_timestamp: Whether to include timestamp in logs
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Set level
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    if format_string is None:
        if include_timestamp:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            format_string = '%(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def log_api_request(
    logger: logging.Logger,
    method: str,
    path: str,
    user_id: Optional[Union[int, str]] = None,
    request_data: Optional[Dict[str, Any]] = None
):
    """
    Log API request information
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        user_id: Optional user ID
        request_data: Optional request data (be careful with sensitive data)
    """
    log_data = {
        "type": "api_request",
        "method": method,
        "path": path,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if request_data:
        # Remove sensitive fields
        safe_data = sanitize_log_data(request_data)
        log_data["request_data"] = safe_data
    
    logger.info(json.dumps(log_data))

def log_api_response(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    response_time_ms: float,
    user_id: Optional[Union[int, str]] = None,
    error: Optional[str] = None
):
    """
    Log API response information
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        response_time_ms: Response time in milliseconds
        user_id: Optional user ID
        error: Optional error message
    """
    log_data = {
        "type": "api_response",
        "method": method,
        "path": path,
        "status_code": status_code,
        "response_time_ms": response_time_ms,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if error:
        log_data["error"] = error
    
    if status_code >= 400:
        logger.error(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))

def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table: str,
    record_id: Optional[Union[int, str]] = None,
    user_id: Optional[Union[int, str]] = None,
    success: bool = True,
    error: Optional[str] = None
):
    """
    Log database operations
    
    Args:
        logger: Logger instance
        operation: Type of operation (create, read, update, delete)
        table: Database table name
        record_id: Optional record ID
        user_id: Optional user ID who performed the operation
        success: Whether operation was successful
        error: Optional error message
    """
    log_data = {
        "type": "database_operation",
        "operation": operation,
        "table": table,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if record_id:
        log_data["record_id"] = record_id
    
    if user_id:
        log_data["user_id"] = user_id
    
    if error:
        log_data["error"] = error
    
    if success:
        logger.info(json.dumps(log_data))
    else:
        logger.error(json.dumps(log_data))

def log_websocket_event(
    logger: logging.Logger,
    event_type: str,
    user_id: Optional[Union[int, str]] = None,
    conversation_id: Optional[Union[int, str]] = None,
    message_type: Optional[str] = None,
    success: bool = True,
    error: Optional[str] = None
):
    """
    Log WebSocket events
    
    Args:
        logger: Logger instance
        event_type: Type of WebSocket event (connect, disconnect, message, etc.)
        user_id: Optional user ID
        conversation_id: Optional conversation ID
        message_type: Optional message type
        success: Whether event was handled successfully
        error: Optional error message
    """
    log_data = {
        "type": "websocket_event",
        "event_type": event_type,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if conversation_id:
        log_data["conversation_id"] = conversation_id
    
    if message_type:
        log_data["message_type"] = message_type
    
    if error:
        log_data["error"] = error
    
    if success:
        logger.info(json.dumps(log_data))
    else:
        logger.error(json.dumps(log_data))

def log_openai_api_call(
    logger: logging.Logger,
    model: str,
    tokens_used: Optional[int] = None,
    response_time_ms: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None
):
    """
    Log OpenAI API calls
    
    Args:
        logger: Logger instance
        model: OpenAI model used
        tokens_used: Number of tokens used
        response_time_ms: Response time in milliseconds
        success: Whether API call was successful
        error: Optional error message
    """
    log_data = {
        "type": "openai_api_call",
        "model": model,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if tokens_used:
        log_data["tokens_used"] = tokens_used
    
    if response_time_ms:
        log_data["response_time_ms"] = response_time_ms
    
    if error:
        log_data["error"] = error
    
    if success:
        logger.info(json.dumps(log_data))
    else:
        logger.error(json.dumps(log_data))

def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove sensitive information from log data
    
    Args:
        data: Original data dictionary
        
    Returns:
        Sanitized data dictionary
    """
    sensitive_fields = {
        'password', 'api_key', 'secret', 'token', 'private_key',
        'openai_api_key', 'database_url', 'secret_key'
    }
    
    sanitized = {}
    
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if field name contains sensitive keywords
        is_sensitive = any(sensitive in key_lower for sensitive in sensitive_fields)
        
        if is_sensitive:
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = sanitize_log_data(value)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            # Handle lists of dictionaries
            sanitized[key] = [sanitize_log_data(item) for item in value]
        else:
            sanitized[key] = value
    
    return sanitized

def create_performance_logger(name: str) -> logging.Logger:
    """
    Create a logger specifically for performance monitoring
    
    Args:
        name: Logger name
        
    Returns:
        Performance logger instance
    """
    return setup_logger(
        name=f"{name}.performance",
        level=logging.INFO,
        format_string='%(asctime)s - PERFORMANCE - %(message)s'
    )

def create_security_logger(name: str) -> logging.Logger:
    """
    Create a logger specifically for security events
    
    Args:
        name: Logger name
        
    Returns:
        Security logger instance
    """
    return setup_logger(
        name=f"{name}.security",
        level=logging.WARNING,
        format_string='%(asctime)s - SECURITY - %(levelname)s - %(message)s'
    )

def log_security_event(
    logger: logging.Logger,
    event_type: str,
    user_id: Optional[Union[int, str]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log security-related events
    
    Args:
        logger: Security logger instance
        event_type: Type of security event (login_attempt, access_denied, etc.)
        user_id: Optional user ID
        ip_address: Optional IP address
        user_agent: Optional user agent string
        details: Optional additional details
    """
    log_data = {
        "type": "security_event",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if ip_address:
        log_data["ip_address"] = ip_address
    
    if user_agent:
        log_data["user_agent"] = user_agent
    
    if details:
        log_data["details"] = sanitize_log_data(details)
    
    logger.warning(json.dumps(log_data))
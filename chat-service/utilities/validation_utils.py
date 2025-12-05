"""
Validation utility functions for data validation and sanitization
"""
import re
from typing import Any, Optional, List, Dict
from email_validator import validate_email, EmailNotValidError

def is_valid_email(email: str) -> bool:
    """
    Validate email address format (syntax only, not deliverability)
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    try:
        # Only check syntax, not deliverability for testing purposes
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False

def sanitize_string(
    value: str, 
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
    strip_whitespace: bool = True,
    remove_special_chars: bool = False
) -> str:
    """
    Sanitize and validate string input
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        min_length: Minimum required length
        strip_whitespace: Whether to strip leading/trailing whitespace
        remove_special_chars: Whether to remove special characters
        
    Returns:
        Sanitized string
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(value, str):
        raise ValueError("Value must be a string")
    
    # Strip whitespace if requested
    if strip_whitespace:
        value = value.strip()
    
    # Remove special characters if requested
    if remove_special_chars:
        value = re.sub(r'[^a-zA-Z0-9\s]', '', value)
    
    # Check length constraints
    if min_length is not None and len(value) < min_length:
        raise ValueError(f"String must be at least {min_length} characters long")
    
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"String must be at most {max_length} characters long")
    
    return value

def validate_username(username: str) -> bool:
    """
    Validate username format (alphanumeric and underscore only)
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid username, False otherwise
    """
    if not username:
        return False
    
    # Username should be 3-50 characters, alphanumeric and underscore only
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return bool(re.match(pattern, username))

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid phone number, False otherwise
    """
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits_only) <= 15

def sanitize_html(text: str) -> str:
    """
    Remove HTML tags from text
    
    Args:
        text: Text potentially containing HTML
        
    Returns:
        Text with HTML tags removed
    """
    # Simple HTML tag removal (for more complex needs, use bleach library)
    clean_text = re.sub(r'<[^>]+>', '', text)
    return clean_text.strip()

def validate_message_content(content: str, max_length: int = 10000) -> tuple:
    """
    Validate chat message content
    
    Args:
        content: Message content to validate
        max_length: Maximum allowed message length
        
    Returns:
        Tuple of (is_valid: bool, sanitized_content: str, error_message: Optional[str])
    """
    if not content:
        return False, "", "Message content cannot be empty"
    
    if not isinstance(content, str):
        return False, "", "Message content must be a string"
    
    # Strip whitespace
    content = content.strip()
    
    if len(content) == 0:
        return False, "", "Message content cannot be empty"
    
    if len(content) > max_length:
        return False, "", f"Message content exceeds maximum length of {max_length} characters"
    
    # Sanitize HTML
    sanitized = sanitize_html(content)
    
    return True, sanitized, None

def validate_price(price: Any) -> bool:
    """
    Validate price value (should be non-negative number)
    
    Args:
        price: Price value to validate
        
    Returns:
        True if valid price, False otherwise
    """
    try:
        price_float = float(price)
        return price_float >= 0
    except (ValueError, TypeError):
        return False

def validate_pagination_params(skip: int, limit: int, max_limit: int = 1000) -> tuple:
    """
    Validate and sanitize pagination parameters
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        max_limit: Maximum allowed limit
        
    Returns:
        Tuple of (validated_skip, validated_limit)
        
    Raises:
        ValueError: If parameters are invalid
    """
    if skip < 0:
        raise ValueError("Skip parameter must be non-negative")
    
    if limit <= 0:
        raise ValueError("Limit parameter must be positive")
    
    if limit > max_limit:
        raise ValueError(f"Limit parameter cannot exceed {max_limit}")
    
    return skip, limit

def validate_search_query(query: str, min_length: int = 2, max_length: int = 200) -> str:
    """
    Validate and sanitize search query
    
    Args:
        query: Search query string
        min_length: Minimum query length
        max_length: Maximum query length
        
    Returns:
        Sanitized query string
        
    Raises:
        ValueError: If query is invalid
    """
    if not query or not isinstance(query, str):
        raise ValueError("Search query must be a non-empty string")
    
    query = query.strip()
    
    if len(query) < min_length:
        raise ValueError(f"Search query must be at least {min_length} characters")
    
    if len(query) > max_length:
        raise ValueError(f"Search query must be at most {max_length} characters")
    
    # Remove potentially dangerous characters for SQL injection prevention
    # (Note: This is basic sanitization; proper parameterized queries are still essential)
    dangerous_chars = ['\'', '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
    for char in dangerous_chars:
        if char in query:
            raise ValueError("Search query contains invalid characters")
    
    return query

def validate_json_data(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that JSON data contains required fields
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if all required fields are present, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
    
    return True

def normalize_text(text: str) -> str:
    """
    Normalize text for consistent processing
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Convert to lowercase, strip whitespace, and normalize spaces
    normalized = re.sub(r'\s+', ' ', text.strip().lower())
    return normalized

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (e.g., ['.jpg', '.png'])
        
    Returns:
        True if extension is allowed, False otherwise
    """
    if not filename or '.' not in filename:
        return False
    
    extension = '.' + filename.rsplit('.', 1)[1].lower()
    return extension in [ext.lower() for ext in allowed_extensions]

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed_file"
    
    # Remove or replace invalid characters
    # Keep only alphanumeric characters, dots, dashes, and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9.\-_]', '_', filename)
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip('_.')
    
    # Ensure filename is not empty and not too long
    if not sanitized:
        sanitized = "unnamed_file"
    elif len(sanitized) > 255:
        # Keep extension if present
        if '.' in sanitized:
            name, ext = sanitized.rsplit('.', 1)
            sanitized = name[:250] + '.' + ext
        else:
            sanitized = sanitized[:255]
    
    return sanitized
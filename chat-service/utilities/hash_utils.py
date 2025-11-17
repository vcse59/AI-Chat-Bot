"""
Hash utilities for generating unique IDs
"""
import hashlib
import secrets
import time
from typing import Optional

def generate_user_hash(email: str, username: str) -> str:
    """
    Generate a unique hash for a user based on email, username, and timestamp
    
    Args:
        email: User's email address
        username: User's username
        
    Returns:
        A unique hash string for the user
    """
    # Combine email, username, current timestamp and a random salt
    timestamp = str(int(time.time() * 1000000))  # microsecond timestamp
    salt = secrets.token_hex(8)  # 16 character random hex string
    
    # Create the hash input string
    hash_input = f"{email.lower()}:{username.lower()}:{timestamp}:{salt}"
    
    # Generate SHA-256 hash
    hash_object = hashlib.sha256(hash_input.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    
    # Return first 16 characters for a shorter, more manageable ID
    return hash_hex[:16]

def generate_conversation_hash(user_id: str, title: Optional[str] = None) -> str:
    """
    Generate a unique hash for a conversation
    
    Args:
        user_id: The user's hash ID
        title: Optional conversation title
        
    Returns:
        A unique hash string for the conversation
    """
    timestamp = str(int(time.time() * 1000000))
    salt = secrets.token_hex(6)  # 12 character random hex string
    
    # Use title if provided, otherwise use a default
    title_part = title.lower() if title else "conversation"
    
    hash_input = f"{user_id}:{title_part}:{timestamp}:{salt}"
    
    hash_object = hashlib.sha256(hash_input.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    
    # Return first 12 characters for conversation IDs
    return hash_hex[:12]

def generate_message_hash(conversation_id: str, content: str, role: str) -> str:
    """
    Generate a unique hash for a message
    
    Args:
        conversation_id: The conversation's hash ID
        content: Message content
        role: Message role (user/assistant/system)
        
    Returns:
        A unique hash string for the message
    """
    timestamp = str(int(time.time() * 1000000))
    salt = secrets.token_hex(4)  # 8 character random hex string
    
    # Use first 50 characters of content for hash input
    content_snippet = content[:50].lower()
    
    hash_input = f"{conversation_id}:{role}:{content_snippet}:{timestamp}:{salt}"
    
    hash_object = hashlib.sha256(hash_input.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    
    # Return first 10 characters for message IDs
    return hash_hex[:10]

def is_valid_hash_id(hash_id: str, expected_length: int) -> bool:
    """
    Validate if a string is a valid hash ID
    
    Args:
        hash_id: The hash ID to validate
        expected_length: Expected length of the hash
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(hash_id, str):
        return False
    
    if len(hash_id) != expected_length:
        return False
    
    # Check if it's a valid hexadecimal string
    try:
        int(hash_id, 16)
        return True
    except ValueError:
        return False

def validate_user_hash(user_id: str) -> bool:
    """Validate user hash ID (16 characters)"""
    return is_valid_hash_id(user_id, 16)

def validate_conversation_hash(conversation_id: str) -> bool:
    """Validate conversation hash ID (12 characters)"""
    return is_valid_hash_id(conversation_id, 12)

def validate_message_hash(message_id: str) -> bool:
    """Validate message hash ID (10 characters)"""
    return is_valid_hash_id(message_id, 10)
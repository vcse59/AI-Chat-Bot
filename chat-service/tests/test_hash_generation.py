"""
Test script to verify hash generation functionality
"""
from utilities.hash_utils import (
    generate_user_hash, generate_conversation_hash, generate_message_hash,
    validate_user_hash, validate_conversation_hash, validate_message_hash
)

def test_hash_generation():
    """Test hash generation functions"""
    print("Testing Hash Generation Functions")
    print("=" * 40)
    
    # Test user hash generation
    email = "test@example.com"
    username = "testuser"
    user_hash1 = generate_user_hash(email, username)
    user_hash2 = generate_user_hash(email, username)
    
    print(f"User Hash 1: {user_hash1}")
    print(f"User Hash 2: {user_hash2}")
    print(f"User hashes are unique: {user_hash1 != user_hash2}")
    print(f"User hash 1 is valid: {validate_user_hash(user_hash1)}")
    print(f"User hash 2 is valid: {validate_user_hash(user_hash2)}")
    print()
    
    # Test conversation hash generation
    conversation_hash1 = generate_conversation_hash(user_hash1, "Test Conversation")
    conversation_hash2 = generate_conversation_hash(user_hash1, "Test Conversation")
    
    print(f"Conversation Hash 1: {conversation_hash1}")
    print(f"Conversation Hash 2: {conversation_hash2}")
    print(f"Conversation hashes are unique: {conversation_hash1 != conversation_hash2}")
    print(f"Conversation hash 1 is valid: {validate_conversation_hash(conversation_hash1)}")
    print(f"Conversation hash 2 is valid: {validate_conversation_hash(conversation_hash2)}")
    print()
    
    # Test message hash generation
    message_hash1 = generate_message_hash(conversation_hash1, "Hello, world!", "user")
    message_hash2 = generate_message_hash(conversation_hash1, "Hello, world!", "user")
    
    print(f"Message Hash 1: {message_hash1}")
    print(f"Message Hash 2: {message_hash2}")
    print(f"Message hashes are unique: {message_hash1 != message_hash2}")
    print(f"Message hash 1 is valid: {validate_message_hash(message_hash1)}")
    print(f"Message hash 2 is valid: {validate_message_hash(message_hash2)}")
    print()
    
    # Test validation with invalid hashes
    print("Testing validation with invalid hashes:")
    print(f"Invalid user hash (short): {validate_user_hash('abc123')}")
    print(f"Invalid conversation hash (long): {validate_conversation_hash('abcdef123456789')}")
    print(f"Invalid message hash (non-hex): {validate_message_hash('ghijklmnop')}")
    print()
    
    print("Hash generation test completed!")

if __name__ == "__main__":
    test_hash_generation()
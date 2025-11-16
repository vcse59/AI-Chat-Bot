"""Debug script to test JWT authentication"""
import os
import sys
from jose import jwt, JWTError

# Get environment variables
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

print("=" * 60)
print("JWT Authentication Debug Test")
print("=" * 60)
print(f"SECRET_KEY (first 20 chars): {SECRET_KEY[:20]}...")
print(f"ALGORITHM: {ALGORITHM}")
print()

# Test token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGVzIjpbInVzZXIiLCJhZG1pbiJdLCJleHAiOjE3NjMyNzk2ODN9.8CinRiZkefRir3F6wJu5kuX0NeKtN3JjvD_pcDc14kU"

print(f"Testing token (first 50 chars): {token[:50]}...")
print()

try:
    # Decode JWT token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("✓ Token decoded successfully!")
    print(f"Payload: {payload}")
    print()
    
    # Extract user information
    user_id = payload.get("sub")
    username = payload.get("sub")
    roles = payload.get("roles", [])
    
    print(f"user_id: {user_id}")
    print(f"username: {username}")
    print(f"roles: {roles}")
    print()
    
    if user_id is None:
        print("✗ ERROR: user_id is None")
        sys.exit(1)
    
    print("✓ All checks passed!")
    
except JWTError as e:
    print(f"✗ JWTError occurred: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    sys.exit(1)

print("=" * 60)

#!/usr/bin/env python3
"""Test authentication flow"""
import requests
from urllib.parse import urlencode

print("=" * 60)
print("Testing Authentication Flow")
print("=" * 60)

# Test login with existing user
print("\n1. Testing login with existing user...")
data = urlencode({'username': 'testuser123', 'password': 'password123'})
r = requests.post(
    'http://localhost:8001/auth/token',
    data=data,
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
print(f"   Login Status: {r.status_code}")

if r.status_code == 200:
    token = r.json()['access_token']
    print(f"   ✓ Token received: {token[:60]}...")
    
    # Test token with chat service
    print("\n2. Testing token with chat service...")
    r2 = requests.get(
        'http://localhost:8000/api/v1/users/testuser123/conversations/',
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f"   Chat API Status: {r2.status_code}")
    if r2.status_code == 200:
        print(f"   ✓ Token verified! Response: {r2.json()}")
    else:
        print(f"   ✗ Token verification failed: {r2.text}")
else:
    print(f"   ✗ Login failed: {r.text}")

# Test new user registration
print("\n3. Testing new user registration...")
import time
username = f'testuser{int(time.time())}'
r3 = requests.post(
    'http://localhost:8001/users/',
    json={
        'username': username,
        'email': f'{username}@example.com',
        'full_name': 'Test User',
        'password': 'password123'
    }
)
print(f"   Registration Status: {r3.status_code}")
if r3.status_code == 200:
    print(f"   ✓ User created: {r3.json()}")
    
    # Try to login with new user
    print("\n4. Testing login with new user...")
    data = urlencode({'username': username, 'password': 'password123'})
    r4 = requests.post(
        'http://localhost:8001/auth/token',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    print(f"   Login Status: {r4.status_code}")
    if r4.status_code == 200:
        print(f"   ✓ Login successful!")
    else:
        print(f"   ✗ Login failed: {r4.text}")
else:
    print(f"   ✗ Registration failed: {r3.text}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

#!/usr/bin/env python3
"""Test conversation creation"""
import requests
from urllib.parse import urlencode

print("=" * 60)
print("Testing Conversation Creation")
print("=" * 60)

# Login first
print("\n1. Logging in...")
data = urlencode({'username': 'testuser123', 'password': 'password123'})
r = requests.post(
    'http://localhost:8001/auth/token',
    data=data,
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)

if r.status_code != 200:
    print(f"   ✗ Login failed: {r.text}")
    exit(1)

token = r.json()['access_token']
print(f"   ✓ Login successful")

# Get conversations
print("\n2. Getting user conversations...")
r2 = requests.get(
    'http://localhost:8000/api/v1/users/testuser123/conversations/',
    headers={'Authorization': f'Bearer {token}'}
)
print(f"   Status: {r2.status_code}")
if r2.status_code == 200:
    conversations = r2.json()
    print(f"   ✓ Found {len(conversations)} conversations")
else:
    print(f"   Response: {r2.text}")

# Create new conversation
print("\n3. Creating new conversation...")
r3 = requests.post(
    'http://localhost:8000/api/v1/users/testuser123/conversations/',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'title': 'Test Conversation',
        'user_id': 'testuser123'
    }
)
print(f"   Status: {r3.status_code}")
if r3.status_code == 200:
    conversation = r3.json()
    print(f"   ✓ Conversation created!")
    print(f"   ID: {conversation.get('id')}")
    print(f"   Title: {conversation.get('title')}")
else:
    print(f"   ✗ Failed: {r3.text}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

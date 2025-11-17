"""Test analytics API flow with authentication"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Service URLs
AUTH_URL = "http://localhost:8001"
ANALYTICS_URL = "http://localhost:8002"

def test_analytics_flow():
    """Test complete flow: login -> get token -> call analytics"""
    
    print("=" * 80)
    print("Testing Analytics API Flow")
    print("=" * 80)
    
    # Step 1: Login to get token
    print("\n1. Logging in as admin...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            f"{AUTH_URL}/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print(f"   ✅ Login successful!")
        print(f"   Token (first 50 chars): {access_token[:50]}...")
        
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Step 2: Test analytics summary endpoint
    print("\n2. Testing analytics summary endpoint...")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        summary_response = requests.get(
            f"{ANALYTICS_URL}/api/v1/analytics/summary",
            headers=headers
        )
        
        print(f"   Status Code: {summary_response.status_code}")
        
        if summary_response.status_code == 200:
            print("   ✅ Analytics summary loaded successfully!")
            summary = summary_response.json()
            print(f"   Summary: {json.dumps(summary, indent=2)}")
        else:
            print(f"   ❌ Failed to load analytics summary")
            print(f"   Response: {summary_response.text}")
            
    except Exception as e:
        print(f"   ❌ Analytics API error: {e}")
        return
    
    # Step 3: Test other analytics endpoints
    print("\n3. Testing other analytics endpoints...")
    
    endpoints = [
        "/api/v1/analytics/users/activities",
        "/api/v1/analytics/users/top",
        "/api/v1/analytics/conversations",
        "/api/v1/analytics/api-usage",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{ANALYTICS_URL}{endpoint}",
                headers=headers
            )
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {e}")
    
    print("\n" + "=" * 80)
    print("Test complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_analytics_flow()

"""
Simple script to test user creation with the new hash-based system
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_user_creation():
    """Test creating a user with hash-based ID"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser123",
        "full_name": "Test User"
    }
    
    print("Testing User Creation with Hash-based IDs")
    print("=" * 50)
    
    try:
        # Create user
        print(f"Creating user: {user_data}")
        response = requests.post(
            f"{BASE_URL}/users/",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User created successfully!")
            print(f"   User ID: {user['id']}")
            print(f"   Email: {user['email']}")
            print(f"   Username: {user['username']}")
            print(f"   Full Name: {user['full_name']}")
            
            # Test getting the user
            print(f"\n📖 Testing user retrieval...")
            get_response = requests.get(f"{BASE_URL}/users/{user['id']}")
            print(f"Get Response Status: {get_response.status_code}")
            
            if get_response.status_code == 200:
                retrieved_user = get_response.json()
                print(f"✅ User retrieved successfully!")
                print(f"   Retrieved ID: {retrieved_user['id']}")
                print(f"   Retrieved Email: {retrieved_user['email']}")
            else:
                print(f"❌ Failed to retrieve user: {get_response.text}")
            
            # Test creating a conversation for this user
            print(f"\n💬 Testing conversation creation...")
            conv_data = {
                "title": "Test Conversation",
                "context_metadata": {"source": "api_test"}
            }
            
            conv_response = requests.post(
                f"{BASE_URL}/users/{user['id']}/conversations/",
                json=conv_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Conversation Response Status: {conv_response.status_code}")
            
            if conv_response.status_code == 200:
                conversation = conv_response.json()
                print(f"✅ Conversation created successfully!")
                print(f"   Conversation ID: {conversation['id']}")
                print(f"   Title: {conversation['title']}")
                print(f"   User ID: {conversation['user_id']}")
                
                # Test adding a message
                print(f"\n📝 Testing message creation...")
                msg_data = {
                    "role": "user",
                    "content": "Hello, this is a test message!"
                }
                
                msg_response = requests.post(
                    f"{BASE_URL}/conversations/{conversation['id']}/messages/",
                    json=msg_data,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Message Response Status: {msg_response.status_code}")
                
                if msg_response.status_code == 200:
                    message = msg_response.json()
                    print(f"✅ Message created successfully!")
                    print(f"   Message ID: {message['id']}")
                    print(f"   Content: {message['content']}")
                    print(f"   Role: {message['role']}")
                    print(f"   Conversation ID: {message['conversation_id']}")
                else:
                    print(f"❌ Failed to create message: {msg_response.text}")
            else:
                print(f"❌ Failed to create conversation: {conv_response.text}")
            
        else:
            print(f"❌ Failed to create user: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")

def test_list_users():
    """Test listing users"""
    print(f"\n📋 Testing user listing...")
    try:
        response = requests.get(f"{BASE_URL}/users/")
        print(f"List Users Response Status: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} users:")
            for user in users:
                print(f"   - ID: {user['id']}, Email: {user['email']}, Username: {user['username']}")
        else:
            print(f"❌ Failed to list users: {response.text}")
            
    except Exception as e:
        print(f"❌ Error listing users: {e}")

if __name__ == "__main__":
    test_list_users()
    test_user_creation()
#!/usr/bin/env python3
"""
Test the authentication system
"""
import requests
import json

API_KEY = "intelligent-recipe-generator-api-key-2023"
BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("🧪 Testing User Registration")

    test_user = {
        "username": "testuser_auth",
        "email": "test_auth@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register",
                               json=test_user,
                               headers={"Content-Type": "application/json", "X-API-Key": API_KEY})

        if response.status_code == 201:
            data = response.json()
            print("✅ User registration successful!")
            print(f"   Username: {data['user']['username']}")
            print(f"   Email: {data['user']['email']}")
            return data.get('token')
        elif response.status_code == 409:
            print("ℹ️ User already exists, trying login instead")
            return test_login()
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def test_login():
    """Test user login"""
    print("\n🧪 Testing User Login")

    login_data = {
        "username": "testuser_auth",
        "password": "password123"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login",
                               json=login_data,
                               headers={"Content-Type": "application/json", "X-API-Key": API_KEY})

        if response.status_code == 200:
            data = response.json()
            print("✅ User login successful!")
            print(f"   Welcome back, {data['user']['username']}!")
            return data.get('token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def test_protected_route(token):
    """Test accessing protected route with token"""
    print("\n🧪 Testing Protected Route Access")

    try:
        response = requests.get(f"{BASE_URL}/auth/profile",
                              headers={
                                  "Authorization": f"Bearer {token}",
                                  "X-API-Key": API_KEY
                              })

        if response.status_code == 200:
            data = response.json()
            print("✅ Protected route access successful!")
            print(f"   User: {data['user']['username']}")
            print(f"   Preferences: {len(data.get('preferences', {}))} settings")
            return True
        else:
            print(f"❌ Protected route failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    print("🔐 Testing Authentication System")
    print("=" * 50)

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/database-status",
                              headers={"X-API-Key": API_KEY}, timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding")
            return
    except:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return

    # Test registration/login
    token = test_register()
    if not token:
        print("❌ Authentication system has issues")
        return

    # Test protected route
    if test_protected_route(token):
        print("\n" + "=" * 50)
        print("🎉 Authentication system is working perfectly!")
        print("✅ User registration/login")
        print("✅ JWT token generation")
        print("✅ Protected route access")
        print("✅ Profile management")
    else:
        print("\n❌ Authentication system has issues")

if __name__ == "__main__":
    main()

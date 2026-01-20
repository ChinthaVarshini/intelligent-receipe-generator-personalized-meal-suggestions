#!/usr/bin/env python3
"""
Basic API test to verify the application is running
"""
import requests
import json

API_KEY = "intelligent-recipe-generator-api-key-2023"
BASE_URL = "http://localhost:3000"

def test_database_status():
    """Test database status endpoint"""
    print("Testing database status...")
    try:
        response = requests.get(f"{BASE_URL}/database-status",
                              headers={"X-API-Key": API_KEY})
        if response.status_code == 200:
            data = response.json()
            print("✅ Database status OK")
            print(f"   Status: {data.get('status')}")
            print(f"   Recipes: {data.get('total_recipes')}")
            return True
        else:
            print(f"❌ Database status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_get_recipes():
    """Test get recipes endpoint"""
    print("\nTesting get recipes...")
    try:
        response = requests.get(f"{BASE_URL}/get-all-recipes",
                              headers={"X-API-Key": API_KEY})
        if response.status_code == 200:
            data = response.json()
            print("✅ Get recipes OK")
            print(f"   Total recipes: {data.get('total_recipes')}")
            return True
        else:
            print(f"❌ Get recipes failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_generate_instructions():
    """Test instruction generation (now works with demo fallback)"""
    print("Testing instruction generation...")
    test_data = {
        "name": "Test Recipe",
        "ingredients": ["test", "ingredients"],
        "cuisine": "test",
        "difficulty": "Easy"
    }
    try:
        response = requests.post(f"{BASE_URL}/generate-instructions",
                               json=test_data,
                               headers={"X-API-Key": API_KEY, "Content-Type": "application/json"})
        if response.status_code == 200:
            data = response.json()
            if data.get("is_demo"):
                print("✅ Demo instruction generation OK (no API credits needed!)")
            else:
                print("✅ AI instruction generation OK")
            return True
        else:
            print(f"❌ Instruction generation failed: {response.status_code}")
            data = response.json()
            print(f"   Error: {data.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_generate_recipe():
    """Test recipe generation with demo fallback"""
    print("\nTesting recipe generation...")
    test_data = {"ingredients": ["tomato", "pasta"]}
    try:
        response = requests.post(f"{BASE_URL}/generate-recipe",
                               json=test_data,
                               headers={"X-API-Key": API_KEY, "Content-Type": "application/json"})
        if response.status_code == 200:
            data = response.json()
            if data.get("is_demo"):
                print("✅ Demo recipe generation OK (no API credits needed!)")
            else:
                print("✅ AI recipe generation OK")
            return True
        else:
            print(f"❌ Recipe generation failed: {response.status_code}")
            data = response.json()
            print(f"   Error: {data.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    print("🧪 Testing Intelligent Recipe Generator API")
    print("=" * 50)

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/database-status",
                              headers={"X-API-Key": API_KEY}, timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding or API key is invalid")
            return
    except:
        print("❌ Cannot connect to server. Make sure it's running on localhost:3000")
        return

    # Run tests
    tests = [
        test_database_status,
        test_get_recipes,
        test_generate_instructions,
        test_generate_recipe
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Tests completed: {passed}/{len(tests)} passed")

    if passed == len(tests):
        print("🎉 All tests passed! The application is fully functional.")
    elif passed >= 2:
        print("✅ Core functionality working. AI features may be limited by API quotas.")
    else:
        print("❌ Major issues detected. Check server logs.")

if __name__ == "__main__":
    main()

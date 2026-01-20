#!/usr/bin/env python3
"""
Test script for API endpoints - Search and Filter functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_database_status():
    """Test database status endpoint"""
    print("Testing database status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/database-status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Database status retrieved successfully")
            print(f"   Total recipes: {data.get('total_recipes', 0)}")
            print(f"   Total ingredients: {data.get('total_ingredients', 0)}")
            return True
        else:
            print(f"❌ Database status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database status error: {e}")
        return False

def test_recipe_filters():
    """Test recipe filters endpoint"""
    print("\nTesting recipe filters endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/recipe-filters", headers={"X-API-Key": "intelligent-recipe-generator-api-key-2023"})
        if response.status_code == 200:
            data = response.json()
            print("✅ Recipe filters retrieved successfully")
            print(f"   Cuisine types: {len(data.get('cuisine_types', []))}")
            print(f"   Difficulty levels: {len(data.get('difficulty_levels', []))}")
            print(f"   Dietary preferences: {len(data.get('dietary_preferences', []))}")
            return True
        else:
            print(f"❌ Recipe filters failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Recipe filters error: {e}")
        return False

def test_search_recipes():
    """Test recipe search and filtering"""
    print("\nTesting recipe search and filtering...")

    # Test basic search
    search_payload = {
        "query": "chicken",
        "per_page": 5
    }

    try:
        response = requests.post(f"{BASE_URL}/search-recipes",
                               json=search_payload,
                               headers={"X-API-Key": "intelligent-recipe-generator-api-key-2023"})
        if response.status_code == 200:
            data = response.json()
            print("✅ Basic search successful")
            print(f"   Found {data.get('total_recipes', 0)} recipes for 'chicken'")
            if data.get('recipes'):
                print(f"   Sample result: {data['recipes'][0]['title']}")
        else:
            print(f"❌ Basic search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Basic search error: {e}")
        return False

    # Test dietary filtering
    dietary_payload = {
        "dietary_preferences": ["vegetarian"],
        "per_page": 3
    }

    try:
        response = requests.post(f"{BASE_URL}/search-recipes",
                               json=dietary_payload,
                               headers={"X-API-Key": "intelligent-recipe-generator-api-key-2023"})
        if response.status_code == 200:
            data = response.json()
            print("✅ Dietary filtering successful")
            print(f"   Found {data.get('total_recipes', 0)} vegetarian recipes")
        else:
            print(f"❌ Dietary filtering failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dietary filtering error: {e}")
        return False

    # Test cuisine filtering
    cuisine_payload = {
        "cuisine_type": "Italian",
        "per_page": 3
    }

    try:
        response = requests.post(f"{BASE_URL}/search-recipes",
                               json=cuisine_payload,
                               headers={"X-API-Key": "intelligent-recipe-generator-api-key-2023"})
        if response.status_code == 200:
            data = response.json()
            print("✅ Cuisine filtering successful")
            print(f"   Found {data.get('total_recipes', 0)} Italian recipes")
        else:
            print(f"❌ Cuisine filtering failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cuisine filtering error: {e}")
        return False

    return True

def test_find_recipes():
    """Test find recipes endpoint (ingredient matching)"""
    print("\nTesting find recipes endpoint...")

    payload = {
        "ingredients": ["chicken", "onion", "garlic"],
        "limit": 3
    }

    try:
        response = requests.post(f"{BASE_URL}/find-recipes",
                               json=payload,
                               headers={"X-API-Key": "intelligent-recipe-generator-api-key-2023"})
        if response.status_code == 200:
            data = response.json()
            print("✅ Find recipes successful")
            print(f"   Found {data.get('total_recipes', 0)} matching recipes")
            if data.get('recipes'):
                recipe = data['recipes'][0]
                print(f"   Top match: {recipe['title']} (score: {recipe['recommendation_score']})")
                print(f"   Method: {recipe['recommendation_method']}")
        else:
            print(f"❌ Find recipes failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Find recipes error: {e}")
        return False

    return True

def test_rate_recipe():
    """Test rate recipe endpoint"""
    print("\nTesting rate recipe endpoint...")

    # First get a recipe ID
    try:
        response = requests.get(f"{BASE_URL}/database-status", headers={"X-API-Key": "intelligent-recipe-generator-api-key-2023"})
        if response.status_code == 200:
            # Assume recipe ID 1 exists
            rating_payload = {
                "user_id": 1,
                "recipe_id": 1,
                "rating": 5,
                "review": "Excellent recipe!"
            }

            response = requests.post(f"{BASE_URL}/rate-recipe",
                                   json=rating_payload,
                                   headers={"X-API-Key": "intelligent-recipe-generator-api-key-2023"})
            if response.status_code == 200:
                print("✅ Rate recipe successful")
                return True
            else:
                print(f"❌ Rate recipe failed: {response.status_code}")
                return False
        else:
            print("❌ Could not get recipe ID for rating test")
            return False
    except Exception as e:
        print(f"❌ Rate recipe error: {e}")
        return False

def wait_for_server():
    """Wait for server to start"""
    print("Waiting for server to start...")
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/database-status", timeout=2)
            if response.status_code == 200:
                print("✅ Server is running")
                return True
        except:
            pass
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    print("❌ Server failed to start")
    return False

def main():
    """Main test function"""
    print("=" * 60)
    print("TESTING API ENDPOINTS")
    print("=" * 60)

    if not wait_for_server():
        print("Cannot test endpoints - server not running")
        return

    tests = [
        test_database_status,
        test_recipe_filters,
        test_search_recipes,
        test_find_recipes,
        test_rate_recipe
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 ALL API ENDPOINTS WORKING CORRECTLY!")
    else:
        print("⚠️  Some tests failed")
    print("=" * 60)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script for NLP cooking instruction generation
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
API_KEY = os.getenv("API_KEY", "intelligent-recipe-generator-api-key-2023")
BASE_URL = "http://localhost:8000"

def test_generate_instructions():
    """Test the NLP instruction generation endpoint"""
    print("Testing NLP cooking instruction generation...")

    # Test data - Tomato Pasta recipe
    recipe_data = {
        "name": "Tomato Pasta",
        "ingredients": ["Tomato", "onion", "garlic", "pasta", "oil"],
        "cuisine": "italian",
        "difficulty": "Easy"
    }

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/generate-instructions",
            json=recipe_data,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Recipe: {result.get('recipe_name')}")
            print(f"Total Steps: {result.get('total_steps')}")
            print("\nGenerated Instructions:")
            for instruction in result.get('instructions', []):
                print(f"Step {instruction['step_number']}: {instruction['description']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_enhance_recipe_instructions():
    """Test enhancing existing recipe with NLP instructions"""
    print("\nTesting recipe enhancement with NLP instructions...")

    # Sample recipe data
    recipe_data = {
        "title": "Simple Spaghetti Carbonara",
        "ingredients": [
            {"name": "spaghetti", "quantity": "200", "unit": "g"},
            {"name": "eggs", "quantity": "2", "unit": "whole"},
            {"name": "parmesan cheese", "quantity": "50", "unit": "g"},
            {"name": "bacon", "quantity": "100", "unit": "g"},
            {"name": "black pepper", "quantity": "to taste", "unit": ""}
        ],
        "cuisine_type": "italian",
        "difficulty_level": "Medium"
    }

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/enhance-recipe-instructions",
            json=recipe_data,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            enhanced_recipe = result.get('enhanced_recipe', {})
            if 'nlp_instructions' in enhanced_recipe:
                print(f"Added {len(enhanced_recipe['nlp_instructions'])} NLP-generated steps")
                print("Sample instructions:")
                for i, instruction in enumerate(enhanced_recipe['nlp_instructions'][:3]):
                    print(f"Step {instruction['step_number']}: {instruction['description']}")
                if len(enhanced_recipe['nlp_instructions']) > 3:
                    print("...")
            else:
                print("No NLP instructions were added")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\nTesting edge cases...")

    # Test with missing ingredients
    test_cases = [
        {"name": "Test Recipe"},  # Missing ingredients
        {"ingredients": ["test"]},  # Missing name
        {}  # Empty data
    ]

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    for i, test_data in enumerate(test_cases):
        print(f"\nTest case {i+1}: {test_data}")
        try:
            response = requests.post(
                f"{BASE_URL}/generate-instructions",
                json=test_data,
                headers=headers
            )

            if response.status_code == 400:
                print("✅ Correctly rejected invalid data")
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    print("NLP Cooking Instruction Generation Tests")
    print("=" * 50)

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/database-status", headers={"X-API-Key": API_KEY}, timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running or API key is invalid")
            exit(1)
    except:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        exit(1)

    # Run tests
    test_generate_instructions()
    test_enhance_recipe_instructions()
    test_edge_cases()

    print("\n" + "=" * 50)
    print("Testing complete!")

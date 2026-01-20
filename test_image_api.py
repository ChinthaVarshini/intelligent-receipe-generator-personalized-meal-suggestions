#!/usr/bin/env python3
"""
Test script for AI Recipe Image Generation API
"""
import requests
import json

def test_ai_image_generation():
    """Test the AI recipe image generation endpoint"""
    url = "http://127.0.0.1:3000/generate-recipe-image"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "intelligent-recipe-generator-api-key-2023"
    }

    # Test data for image generation
    data = {
        "recipe_name": "Golden Saffron Chicken with Caramelized Onions",
        "ingredients": ["chicken", "rice", "onion", "saffron", "olive oil"],
        "cuisine": "Mediterranean",
        "style": "photorealistic"
    }

    print("🎨 Testing AI Recipe Image Generation API")
    print("=" * 50)
    print(f"📡 URL: {url}")
    print(f"📝 Recipe: {data['recipe_name']}")
    print(f"🏺 Cuisine: {data['cuisine']}, Style: {data['style']}")

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)  # Longer timeout for image generation
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")

            if result.get('success'):
                print("🎉 AI Image generated successfully!")
                print(f"🤖 AI Provider: {result.get('ai_provider', 'Unknown')}")
                print(f"🖼️ Image URL: {result.get('image_url', 'N/A')}")
                print(f"📏 Image Size: {result.get('image_size', 'N/A')}")
                print(f"📁 File Path: {result.get('file_path', 'N/A')}")

                # Test if the image URL is accessible
                if result.get('image_url'):
                    image_response = requests.head(result['image_url'], timeout=10)
                    if image_response.status_code == 200:
                        print("✅ Image URL is accessible!")
                    else:
                        print(f"⚠️ Image URL returned status: {image_response.status_code}")

            else:
                print("❌ Image generation failed")
                print(f"Error: {result}")

        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_image_generation_with_different_styles():
    """Test image generation with different styles"""
    styles = ["photorealistic", "artistic", "professional"]
    recipes = [
        {"name": "Classic Spaghetti Carbonara", "ingredients": ["pasta", "eggs", "bacon", "parmesan"], "cuisine": "Italian"},
        {"name": "Thai Green Curry", "ingredients": ["coconut milk", "green curry paste", "chicken", "vegetables"], "cuisine": "Thai"},
        {"name": "Chocolate Lava Cake", "ingredients": ["chocolate", "butter", "eggs", "flour"], "cuisine": "French"}
    ]

    for recipe in recipes:
        for style in styles[:1]:  # Test only one style per recipe to avoid rate limits
            print(f"\n🧪 Testing: {recipe['name']} ({style})")
            url = "http://127.0.0.1:3000/generate-recipe-image"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": "intelligent-recipe-generator-api-key-2023"
            }

            data = {
                "recipe_name": recipe["name"],
                "ingredients": recipe["ingredients"],
                "cuisine": recipe["cuisine"],
                "style": style
            }

            try:
                response = requests.post(url, headers=headers, json=data, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"✅ Success: {result.get('ai_provider')} generated image")
                    else:
                        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                else:
                    print(f"❌ HTTP {response.status_code}")

                # Add delay to avoid rate limits
                import time
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 AI Recipe Image Generation Tests")
    print("=" * 60)

    # Test basic functionality
    test_ai_image_generation()

    # Uncomment to test multiple styles/recipes (be careful of rate limits)
    # print("\n🔄 Testing Multiple Recipes and Styles...")
    # test_image_generation_with_different_styles()

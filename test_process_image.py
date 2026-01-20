#!/usr/bin/env python3
"""
Test script for image processing functionality
"""
import sys
import os
import requests
from PIL import Image
import io

# Add backend to path
sys.path.append('backend/app')

def test_process_image_endpoint():
    """Test the /process-image endpoint"""
    print("Testing /process-image endpoint...")

    # Create a simple test image (white background with some color)
    img = Image.new('RGB', (200, 200), color='white')
    # Add some color to make it more interesting
    for x in range(50, 150):
        for y in range(50, 150):
            img.putpixel((x, y), (255, 0, 0))  # Red square

    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes = img_bytes.getvalue()

    # Prepare the request
    files = {'file': ('test_image.jpg', img_bytes, 'image/jpeg')}
    headers = {'X-API-Key': 'intelligent-recipe-generator-api-key-2023'}

    try:
        response = requests.post('http://localhost:3000/process-image',
                               files=files,
                               headers=headers,
                               timeout=60)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(f"OCR Text: {result.get('ocr_text', 'N/A')[:100]}...")
            print(f"Ingredients detected: {result.get('ingredients', [])}")
            print(f"AI Recipes: {len(result.get('ai_generated_recipes', []))}")
            print(f"DB Recipes: {len(result.get('database_matching_recipes', []))}")
            print(f"Total Recipes: {result.get('total_matching_recipes', 0)}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Image Processing Pipeline")
    print("=" * 50)

    if test_process_image_endpoint():
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")

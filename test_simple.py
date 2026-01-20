#!/usr/bin/env python3

"""
Simple test script to verify OCR and ingredient detection functionality
"""

import sys
import os
sys.path.append('backend/app')

from PIL import Image
from model import extract_ingredients_from_text, get_predictions

def test_ingredient_detection():
    print("Testing ingredient detection...")

    # Test with known ingredient text
    test_texts = [
        "tomato chicken rice",
        "lays potato chips",
        "fresh lettuce and tomato salad",
        "chicken breast with garlic and onion",
        "pasta with tomato sauce"
    ]

    for text in test_texts:
        print(f"\n--- Testing text: '{text}' ---")
        try:
            result = extract_ingredients_from_text(text)
            print(f"Found ingredients: {result}")

            if result:
                print("✅ SUCCESS: Ingredients detected")
            else:
                print("❌ FAILED: No ingredients detected")

        except Exception as e:
            print(f"❌ ERROR: {e}")

    print("\n--- Testing with blank image (should fall back to image classification) ---")
    try:
        # Create a simple test image
        img = Image.new('RGB', (400, 200), color='white')
        prediction = get_predictions(img, "")
        ingredients = prediction.get('ingredients', [])
        print(f"Image classification result: {ingredients}")

        if ingredients:
            print("✅ SUCCESS: Image classification worked")
        else:
            print("ℹ️  INFO: No ingredients from image (expected for blank image)")

    except Exception as e:
        print(f"❌ ERROR in image classification: {e}")

if __name__ == "__main__":
    test_ingredient_detection()

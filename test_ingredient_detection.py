#!/usr/bin/env python3
"""
Test ingredient detection functionality directly
"""
import sys
import os
sys.path.append('backend/app')

from model import extract_ingredients_from_text, get_predictions
from PIL import Image
import io

def test_ingredient_extraction():
    """Test ingredient extraction from text"""
    print("Testing ingredient extraction from text...")

    test_texts = [
        'tomato onion garlic',
        'chicken breast with rice',
        'potato chips lays',
        'fresh lettuce and tomato salad',
        'spaghetti carbonara with eggs and cheese'
    ]

    for text in test_texts:
        ingredients = extract_ingredients_from_text(text)
        print(f'Text: "{text}"')
        print(f'Found ingredients: {ingredients}')
        print('---')

def test_image_processing():
    """Test image processing with a simple image"""
    print("\nTesting image processing...")

    # Create a simple test image (white background)
    img = Image.new('RGB', (200, 200), color='white')

    # Test get_predictions function
    result = get_predictions(img, "")

    print(f"Image processing result:")
    print(f"OCR Text: '{result.get('ocr_text', 'N/A')}'")
    print(f"Ingredients: {result.get('ingredients', [])}")

if __name__ == "__main__":
    print("🧪 Testing Ingredient Detection")
    print("=" * 50)

    test_ingredient_extraction()
    test_image_processing()

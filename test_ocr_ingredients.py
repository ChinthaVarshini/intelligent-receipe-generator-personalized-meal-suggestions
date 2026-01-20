#!/usr/bin/env python3
"""
Test OCR text processing for ingredients
"""
import sys
import os
sys.path.append('backend/app')

from model import extract_ingredients_from_text

def test_ocr_text_processing():
    """Test processing OCR text that might be poorly formatted"""
    print("Testing OCR text processing...")

    # Test the OCR output we got
    ocr_texts = [
        'TOMATOONION GARLIC',  # No spaces
        'TOMATO ONION GARLIC',  # Proper spacing
        'cry gcery oan OAS ONION GARo ae',  # Gibberish from failed OCR
        'chicken breast',  # Partial match
        'fresh lettuce tomato',  # With descriptors
    ]

    for text in ocr_texts:
        ingredients = extract_ingredients_from_text(text)
        print(f'OCR Text: "{text}"')
        print(f'Found ingredients: {ingredients}')
        ingredient_names = [ing[0] for ing in ingredients]
        print(f'Ingredient names: {ingredient_names}')
        print('---')

if __name__ == "__main__":
    print("🧪 Testing OCR Text Processing")
    print("=" * 50)

    test_ocr_text_processing()

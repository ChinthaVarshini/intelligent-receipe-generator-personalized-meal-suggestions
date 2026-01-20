#!/usr/bin/env python3

import sys
sys.path.append('backend/app')

from model import extract_ingredients_from_text
from ocr_utils import (
    perfect_ocr_text_correction,
    advanced_spell_check_with_context,
    ai_powered_text_enhancement,
    clean_extracted_text,
    calculate_text_quality_score
)

def test_advanced_ocr_corrections():
    """Test the advanced OCR correction capabilities"""

    # Test cases with various OCR errors
    test_cases = [
        'Chionira UITY, jor Mins fay',  # Original test case
        't0mat0es and 0nions',  # Number-letter confusion
        '2tsp salt, 1tbsp 011',  # Measurement corrections
        'chcken breast, beff stew',  # Common OCR misreads
        'potatos, carrots, and onlons',  # Plural corrections
        'fresh garllc and gnger',  # Missing letters
        'chocolte chip cookles',  # Multiple errors
        'tamatar pyaj lehsun adrak',  # Indian language ingredients
        'poulet, boeuf, riz, tomate',  # French ingredients
        'pollo, carne, arroz, pasta',  # Spanish/Italian ingredients
        'karotte, zwiebel, knoblauch',  # German ingredients
    ]

    print("=" * 80)
    print("ADVANCED OCR CORRECTION TEST SUITE")
    print("=" * 80)

    for i, ocr_text in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Original OCR Text: {repr(ocr_text)}")

        # Apply ultra-advanced OCR corrections
        corrected_ocr = perfect_ocr_text_correction(ocr_text)
        print(f"Ultra-corrected:    {repr(corrected_ocr)}")

        # Apply advanced spell checking
        spell_checked = advanced_spell_check_with_context(corrected_ocr)
        print(f"Spell-checked:      {repr(spell_checked)}")

        # Apply AI-powered enhancement
        ai_enhanced = ai_powered_text_enhancement(spell_checked)
        print(f"AI-enhanced:        {repr(ai_enhanced)}")

        # Calculate quality score
        quality_score = calculate_text_quality_score(ai_enhanced)
        print(f"Quality Score:      {quality_score:.2f}")

        # Extract ingredients
        ingredients = extract_ingredients_from_text(ai_enhanced)
        ingredient_names = [ing[0] for ing in ingredients]
        print(f"Detected Ingredients: {ingredient_names}")

def test_ocr_quality_scoring():
    """Test the OCR quality scoring system"""

    print("\n" + "=" * 80)
    print("OCR QUALITY SCORING TEST")
    print("=" * 80)

    quality_test_cases = [
        ("2 cups flour, 1 tsp salt, 3 eggs", "High quality recipe text"),
        ("onion tomato potato", "Simple ingredient list"),
        ("asdf qwer zxcv", "Gibberish text"),
        ("", "Empty text"),
        ("a b c d e f g", "Single letters"),
        ("INGREDIENTS: chicken breast, rice, vegetables, spices", "Structured recipe"),
        ("2g salt, 500ml water, 1kg chicken", "Measurements and ingredients"),
    ]

    for text, description in quality_test_cases:
        score = calculate_text_quality_score(text)
        print(f"{description:.<40} Score: {score:.2f}")

if __name__ == "__main__":
    test_advanced_ocr_corrections()
    test_ocr_quality_scoring()

    print("\n" + "=" * 80)
    print("TESTING COMPLETE - ADVANCED OCR SYSTEM READY")
    print("=" * 80)

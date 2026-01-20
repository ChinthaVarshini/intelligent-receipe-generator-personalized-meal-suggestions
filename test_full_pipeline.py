#!/usr/bin/env python3
"""
Test the full image processing pipeline
"""

import sys
import os
sys.path.append('backend/app')

from PIL import Image, ImageDraw, ImageFont
from model import get_predictions
from ocr_utils import extract_text

# Create a test image with some text
def create_test_image_with_text(text, filename):
    # Create a white image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)

    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Draw the text
    draw.text((50, 80), text, fill='black', font=font)
    img.save(filename)
    return img

# Test different scenarios
test_cases = [
    "tomato onion garlic",
    "chicken breast rice",
    "potato chips",
    "fresh lettuce tomato",
    "No ingredients here"
]

print("Testing full pipeline:")
print("=" * 50)

for i, text in enumerate(test_cases):
    filename = f'test_image_{i}.jpg'
    print(f"\nTest case {i+1}: '{text}'")

    # Create test image
    img = create_test_image_with_text(text, filename)

    # Extract text
    ocr_text = extract_text(img)
    print(f"OCR result: '{ocr_text}'")

    # Get predictions
    predictions = get_predictions(img, ocr_text)
    ingredients = predictions.get('ingredients', [])
    print(f"Detected ingredients: {ingredients}")

    # Clean up
    if os.path.exists(filename):
        os.remove(filename)

print("\n" + "=" * 50)
print("Pipeline test complete")

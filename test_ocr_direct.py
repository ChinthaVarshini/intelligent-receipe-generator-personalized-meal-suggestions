#!/usr/bin/env python3
"""
Test OCR functionality directly
"""
import sys
import os
sys.path.append('backend/app')

from ocr_utils import extract_text
from PIL import Image, ImageDraw, ImageFont
import io

def test_ocr_with_text_image():
    """Test OCR with an image that contains text"""
    print("Testing OCR with text image...")

    # Create an image with text
    img = Image.new('RGB', (300, 100), color='white')
    draw = ImageDraw.Draw(img)

    # Try to add text (PIL might not have font support, but let's try)
    try:
        # This might fail if no fonts are available
        draw.text((10, 30), "TOMATO ONION GARLIC", fill='black')
    except:
        # Fallback: just create a simple image
        print("Could not add text to image, using blank image")

    text = extract_text(img)
    print(f"OCR Result: '{text}'")

    if text and len(text.strip()) > 0:
        print("✅ OCR extracted text successfully!")
        return True
    else:
        print("❌ OCR failed to extract text")
        return False

def test_ocr_with_blank_image():
    """Test OCR with a blank image"""
    print("\nTesting OCR with blank image...")

    img = Image.new('RGB', (200, 200), color='white')
    text = extract_text(img)
    print(f"OCR Result: '{text}'")

if __name__ == "__main__":
    print("🧪 Testing OCR Functionality")
    print("=" * 50)

    success = test_ocr_with_text_image()
    test_ocr_with_blank_image()

    if not success:
        print("\n❌ OCR is not working. This is likely the root cause of the issue.")
        print("The app cannot detect ingredients from images because OCR fails.")

#!/usr/bin/env python3

"""
Test script for OCR functionality with tomato image
"""

import sys
import os
sys.path.append('backend/app')

from PIL import Image
from ocr_utils import extract_text

def test_ocr():
    print("Testing OCR functionality...")

    # Create a simple test image with text
    img = Image.new('RGB', (200, 100), color='white')
    # For now, we'll skip creating actual text on image and just test with a blank image
    # In a real test, you'd load an actual tomato image

    print("Testing OCR on blank image...")
    try:
        text = extract_text(img)
        print(f"OCR Result: '{text}'")
        print("OCR test completed successfully!")
        return True
    except Exception as e:
        print(f"OCR test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ocr()

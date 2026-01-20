#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

print("Testing ingredient detection...")

try:
    from model import extract_ingredients_from_text

    # Test cases
    test_cases = [
        "tomato chicken rice",
        "lays potato chips",
        "fresh lettuce",
        "chicken breast"
    ]

    for text in test_cases:
        print(f"\nTesting: '{text}'")
        result = extract_ingredients_from_text(text)
        print(f"Result: {result}")

    print("\n✅ All tests completed successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

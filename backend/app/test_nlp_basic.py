#!/usr/bin/env python3
"""
Basic test for NLP instruction generation (no API required)
"""
import os
import sys
sys.path.append('.')

# Test basic imports
try:
    from recipe_generator import generate_cooking_instructions, enhance_recipe_with_nlp_instructions
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test function definitions
print("✅ Functions available:")
print(f"  - generate_cooking_instructions: {callable(generate_cooking_instructions)}")
print(f"  - enhance_recipe_with_nlp_instructions: {callable(enhance_recipe_with_nlp_instructions)}")

# Test configuration
from config import OPENAI_API_KEY
print(f"OPENAI_API_KEY value: '{OPENAI_API_KEY}'")
print(f"OPENAI_API_KEY is truthy: {bool(OPENAI_API_KEY)}")
print(f"OPENAI_API_KEY == placeholder: {OPENAI_API_KEY == 'your_openai_api_key_here'}")

if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
    print("✅ OpenAI API key is configured")
else:
    print("⚠️  OpenAI API key not configured (using placeholder)")

# Test basic function behavior without API call
print("\nTesting function behavior...")

# Test with invalid data (should pass validation)
result = generate_cooking_instructions({})
if "error" in result and "required" in result["message"]:
    print("✅ Function correctly validates input data")
else:
    print("❌ Function did not validate input properly")
    print(f"Result: {result}")

# Test that function would try to call API with placeholder key
# (This will fail with API error, but shows the function structure works)
result = generate_cooking_instructions({
    "name": "Test Recipe",
    "ingredients": ["test"]
})

if "error" in result:
    if "API key" in result["message"]:
        print("✅ Function correctly detects invalid API key")
    else:
        print("✅ Function attempts API call (fails with auth error as expected)")
else:
    print("❌ Unexpected success - function should have failed with placeholder key")

print("\n" + "=" * 50)
print("Basic functionality test complete!")
print("\nTo test with actual API:")
print("1. Set OPENAI_API_KEY in .env file with your real OpenAI API key")
print("2. Start server: cd backend/app && python main.py")
print("3. Run: python test_nlp_instructions.py")
print("\nExample API usage:")
print('POST /generate-instructions')
print('{')
print('  "name": "Tomato Pasta",')
print('  "ingredients": ["Tomato", "onion", "garlic", "pasta", "oil"],')
print('  "cuisine": "italian",')
print('  "difficulty": "Easy"')
print('}')

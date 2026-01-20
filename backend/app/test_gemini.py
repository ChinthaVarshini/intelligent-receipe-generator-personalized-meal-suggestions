#!/usr/bin/env python3
"""
Test script for Gemini API integration
"""
import sys
sys.path.append('.')

from recipe_generator import generate_recipe

def test_gemini_integration():
    """Test the Gemini API integration with sample ingredients"""
    print("🧪 Testing Gemini API Integration")
    print("=" * 40)

    # Test with sample ingredients
    ingredients = ['chicken', 'rice', 'onion']
    print(f"📝 Testing with ingredients: {ingredients}")

    try:
        result = generate_recipe(ingredients)
        print("✅ Function executed successfully!")

        if 'success' in result and result['success']:
            print("🎉 Gemini API call successful!")
            print(f"🤖 AI Provider used: {result.get('ai_provider', 'Unknown')}")
            print(f"📄 Recipe preview: {result['recipe'][:200]}...")
        else:
            print("❌ Gemini API call failed or returned error")
            print(f"Error: {result}")

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_integration()

#!/usr/bin/env python3
"""
Direct test of NLP cooking instruction generation (no server required)
"""
import sys
sys.path.append('.')

from recipe_generator import generate_cooking_instructions

def test_nlp_direct():
    """Test NLP instruction generation directly"""
    print("🧠 Testing NLP Cooking Instruction Generation")
    print("=" * 50)

    # Test case 1: Tomato Pasta
    print("\n🍝 Test 1: Tomato Pasta Recipe")
    recipe_data = {
        "name": "Tomato Pasta",
        "ingredients": ["Tomato", "onion", "garlic", "pasta", "oil"],
        "cuisine": "italian",
        "difficulty": "Easy"
    }

    print(f"Input: {recipe_data}")
    result = generate_cooking_instructions(recipe_data)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        print(f"Message: {result['message']}")
    else:
        print("✅ Success!")
        print(f"Recipe: {result.get('recipe_name')}")
        print(f"Total Steps: {result.get('total_steps')}")
        print("\n📋 Generated Instructions:")
        for instruction in result.get('instructions', []):
            print(f"   Step {instruction['step_number']}: {instruction['description']}")

    # Test case 2: Chicken Stir Fry
    print("\n🍗 Test 2: Chicken Stir Fry Recipe")
    recipe_data2 = {
        "name": "Chicken Stir Fry",
        "ingredients": ["chicken", "vegetables", "soy sauce", "rice"],
        "cuisine": "chinese",
        "difficulty": "Medium"
    }

    print(f"Input: {recipe_data2}")
    result2 = generate_cooking_instructions(recipe_data2)

    if "error" in result2:
        print(f"❌ Error: {result2['error']}")
        print(f"Message: {result2['message']}")
    else:
        print("✅ Success!")
        print(f"Recipe: {result2.get('recipe_name')}")
        print(f"Total Steps: {result2.get('total_steps')}")
        print("\n📋 Generated Instructions:")
        for instruction in result2.get('instructions', []):
            print(f"   Step {instruction['step_number']}: {instruction['description']}")

    # Test case 3: Invalid input
    print("\n❌ Test 3: Invalid Input (should fail)")
    result3 = generate_cooking_instructions({})
    if "error" in result3:
        print("✅ Correctly rejected invalid input")
        print(f"Error: {result3['error']}")
    else:
        print("❌ Should have failed with invalid input")

    print("\n" + "=" * 50)
    print("🎉 NLP Testing Complete!")
    print("\n💡 Note: To use real OpenAI API, set OPENAI_API_KEY in .env file")
    print("   Current status: Using placeholder API key (will fail gracefully)")

if __name__ == "__main__":
    test_nlp_direct()

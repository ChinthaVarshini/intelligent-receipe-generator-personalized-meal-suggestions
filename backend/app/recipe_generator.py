"""
Recipe generation using Claude API (primary) with OpenAI, Google Gemini, Hugging Face fallback and NLP instruction generation
"""
from openai import OpenAI
import anthropic
import google.generativeai as genai
import requests
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_GEMINI_API_KEY, HUGGINGFACE_API_KEY
import re


def generate_recipe(ingredients, cuisine='General'):
    """
    Generate recipes based on detected ingredients using Claude API (primary), OpenAI (fallback), or demo data

    Args:
        ingredients (list): List of ingredient names
        cuisine (str): Preferred cuisine type

    Returns:
        dict: Generated recipe with name, instructions, and additional details
    """
    if not ingredients or len(ingredients) == 0:
        return {
            "error": "No ingredients provided",
            "message": "Please provide at least one ingredient to generate a recipe"
        }

    # Try Claude first (has free credits)
    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your_claude_api_key_here":
        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

            # Create a prompt for recipe generation
            ingredients_str = ", ".join(ingredients)
            prompt = f"""You are a professional chef. Create a detailed recipe using the following ingredients: {ingredients_str}

Please provide:
1. Recipe Name
2. Cooking Time (preparation and cooking)
3. Difficulty Level (Easy/Medium/Hard)
4. Servings
5. Complete list of ingredients with measurements (including the detected ingredients and any additional ingredients needed)
6. Step-by-step cooking instructions
7. Pro Tips

Format the response in a clear, structured way."""

            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            recipe_text = response.content[0].text

            return {
                "success": True,
                "recipe": recipe_text,
                "ingredients_used": ingredients,
                "ai_provider": "claude"
            }

        except Exception as e:
            print(f"Claude API failed: {e}. Trying OpenAI fallback.")

    # Try OpenAI as secondary option
    if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)

            # Create a prompt for recipe generation
            ingredients_str = ", ".join(ingredients)
            prompt = f"""You are a professional chef. Create a detailed recipe using the following ingredients: {ingredients_str}

Please provide:
1. Recipe Name
2. Cooking Time (preparation and cooking)
3. Difficulty Level (Easy/Medium/Hard)
4. Servings
5. Complete list of ingredients with measurements (including the detected ingredients and any additional ingredients needed)
6. Step-by-step cooking instructions
7. Pro Tips

Format the response in a clear, structured way."""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful cooking assistant that creates delicious recipes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            recipe_text = response.choices[0].message.content

            return {
                "success": True,
                "recipe": recipe_text,
                "ingredients_used": ingredients,
                "ai_provider": "openai"
            }

        except Exception as e:
            print(f"OpenAI API failed: {e}. Trying Google Gemini fallback.")

    # Try Google Gemini as third option
    if GOOGLE_GEMINI_API_KEY and GOOGLE_GEMINI_API_KEY != "your_google_gemini_api_key_here":
        try:
            genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')

            # Create a prompt for recipe generation
            ingredients_str = ", ".join(ingredients)
            prompt = f"""You are a professional chef. Create a detailed recipe using the following ingredients: {ingredients_str}

Please provide:
1. Recipe Name
2. Cooking Time (preparation and cooking)
3. Difficulty Level (Easy/Medium/Hard)
4. Servings
5. Complete list of ingredients with measurements (including the detected ingredients and any additional ingredients needed)
6. Step-by-step cooking instructions
7. Pro Tips

Format the response in a clear, structured way."""

            response = model.generate_content(prompt)
            recipe_text = response.text

            return {
                "success": True,
                "recipe": recipe_text,
                "ingredients_used": ingredients,
                "ai_provider": "gemini"
            }

        except Exception as e:
            print(f"Google Gemini API failed: {e}. Trying Hugging Face fallback.")

    # Try Hugging Face as fourth option (free!)
    if HUGGINGFACE_API_KEY and HUGGINGFACE_API_KEY != "your_huggingface_api_key_here":
        try:
            # Use direct HTTP request to Hugging Face API for better reliability
            ingredients_str = ", ".join(ingredients)

            # Use a reliable text generation model
            api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            headers = {
                "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "inputs": f"Create a simple recipe using {ingredients_str}. Here is the recipe:",
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.8,
                    "do_sample": True,
                    "pad_token_id": 50256
                }
            }

            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()

            # Extract the generated text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
                # Clean up the response - remove the input prompt
                recipe_text = generated_text.replace(payload['inputs'], '').strip()

                if len(recipe_text) > 20:  # If we got meaningful content
                    recipe_text = f"""🍳 AI Recipe with {ingredients_str}

{recipe_text}

*Generated using Hugging Face AI*"""
                else:
                    # Create a structured recipe if the AI response was too short
                    recipe_text = f"""🍳 Simple Recipe with {ingredients_str}

⏱️ Prep Time: 10 minutes
🔥 Cook Time: 15 minutes
📊 Difficulty: Easy
🍽️ Servings: 2-4

📝 Ingredients:
• {ingredients_str}
• Salt, pepper, oil as needed

👨‍🍳 Instructions:
1. Prepare your ingredients: {ingredients_str}
2. Heat oil in a pan over medium heat
3. Add ingredients and cook until done
4. Season with salt and pepper
5. Serve hot

💡 Pro Tips:
• Adjust cooking time based on ingredient types
• Taste and adjust seasoning as needed

*Generated using Hugging Face AI*"""

            return {
                "success": True,
                "recipe": recipe_text,
                "ingredients_used": ingredients,
                "ai_provider": "huggingface"
            }

        except Exception as e:
            print(f"Hugging Face API failed: {e}. Using demo fallback.")

    # Final fallback to demo recipes
    return generate_demo_recipe(ingredients)


def generate_demo_recipe(ingredients):
    """
    Generate a demo recipe when OpenAI is not available (for students/demo purposes)

    Args:
        ingredients (list): List of ingredient names

    Returns:
        dict: Demo recipe data
    """
    # Sample recipes based on common ingredients
    demo_recipes = {
        "tomato": {
            "name": "Classic Tomato Pasta 🍝",
            "prep_time": 10,
            "cook_time": 20,
            "difficulty": "Easy",
            "servings": 4,
            "ingredients": [
                "400g pasta",
                "6 ripe tomatoes, chopped",
                "3 cloves garlic, minced",
                "1/4 cup olive oil",
                "Fresh basil leaves",
                "Salt and pepper to taste",
                "Grated Parmesan cheese (optional)"
            ],
            "instructions": [
                "Cook pasta according to package directions until al dente.",
                "While pasta cooks, heat olive oil in a large pan over medium heat.",
                "Add minced garlic and cook for 1-2 minutes until fragrant.",
                "Add chopped tomatoes, salt, and pepper. Cook for 10-15 minutes, stirring occasionally.",
                "Drain pasta and add to the tomato sauce.",
                "Toss everything together and garnish with fresh basil.",
                "Serve hot with grated Parmesan cheese if desired."
            ],
            "tips": [
                "Use ripe, juicy tomatoes for the best flavor.",
                "Don't overcook the garlic - it can become bitter.",
                "Reserve some pasta water to loosen the sauce if needed."
            ]
        },
        "chicken": {
            "name": "Simple Chicken Stir-Fry 🐔",
            "prep_time": 15,
            "cook_time": 15,
            "difficulty": "Easy",
            "servings": 4,
            "ingredients": [
                "500g chicken breast, sliced",
                "2 cups mixed vegetables (broccoli, carrots, bell peppers)",
                "3 tbsp soy sauce",
                "2 tbsp vegetable oil",
                "2 cloves garlic, minced",
                "1 tbsp ginger, grated",
                "Cooked rice for serving"
            ],
            "instructions": [
                "Heat 1 tbsp oil in a large wok or skillet over high heat.",
                "Add chicken slices and stir-fry for 5-7 minutes until cooked through.",
                "Remove chicken and set aside.",
                "Add remaining oil, garlic, and ginger. Stir-fry for 30 seconds.",
                "Add vegetables and stir-fry for 3-4 minutes until tender-crisp.",
                "Return chicken to pan, add soy sauce, and toss everything together.",
                "Cook for 1-2 more minutes to combine flavors.",
                "Serve hot over cooked rice."
            ],
            "tips": [
                "Cut all ingredients to similar sizes for even cooking.",
                "Have all ingredients ready before starting - stir-frying goes fast!",
                "Adjust soy sauce amount based on your salt preference."
            ]
        },
        "default": {
            "name": "Creative Ingredient Medley 🥘",
            "prep_time": 15,
            "cook_time": 25,
            "difficulty": "Medium",
            "servings": 4,
            "ingredients": [
                f"Your detected ingredients: {', '.join(ingredients)}",
                "Additional complementary ingredients as needed",
                "Basic seasonings (salt, pepper, herbs)",
                "Oil or butter for cooking"
            ],
            "instructions": [
                "Prepare all your ingredients by washing, chopping, and measuring.",
                "Heat oil or butter in a large pan over medium heat.",
                "Start with aromatic ingredients like onions, garlic, or ginger.",
                "Add your main ingredients in order of cooking time needed.",
                "Season with salt, pepper, and herbs as you cook.",
                "Stir occasionally and adjust heat as needed.",
                "Taste and adjust seasonings before serving.",
                "Let rest for a few minutes before serving."
            ],
            "tips": [
                "Hard vegetables take longer to cook than soft ones.",
                "Start with higher heat, then reduce for simmering.",
                "Taste as you go - you can always add more seasoning!",
                "Don't be afraid to experiment with your ingredients."
            ]
        }
    }

    # Find best matching demo recipe
    ingredients_str = " ".join(ingredients).lower()

    if "tomato" in ingredients_str:
        recipe_data = demo_recipes["tomato"]
    elif "chicken" in ingredients_str:
        recipe_data = demo_recipes["chicken"]
    else:
        recipe_data = demo_recipes["default"]

    # Calculate basic nutritional information based on ingredients
    nutrition_info = calculate_basic_nutrition(recipe_data['ingredients'], recipe_data['servings'])

    # Format the recipe as text for display
    recipe_text = f"""🍳 {recipe_data['name']}

⏱️ Prep Time: {recipe_data['prep_time']} minutes
🔥 Cook Time: {recipe_data['cook_time']} minutes
📊 Difficulty: {recipe_data['difficulty']}
🍽️ Servings: {recipe_data['servings']}

📝 Ingredients:
{chr(10).join(f"• {ing}" for ing in recipe_data['ingredients'])}

👨‍🍳 Instructions:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(recipe_data['instructions']))}

🥗 Nutrition per serving (approx.):
• Calories: {nutrition_info['calories']}
• Protein: {nutrition_info['protein']}g
• Carbohydrates: {nutrition_info['carbohydrates']}g
• Fat: {nutrition_info['fat']}g

💡 Pro Tips:
{chr(10).join(f"• {tip}" for tip in recipe_data['tips'])}

*This is a demo recipe. Add OpenAI API credits for personalized AI-generated recipes!*
"""

    return {
        "success": True,
        "recipe": recipe_text,
        "ingredients_used": ingredients,
        "nutrition": nutrition_info,
        "ai_provider": "demo",
        "is_demo": True,
        "message": "Demo recipe generated! Add OpenAI API credits for personalized AI recipes."
    }


def generate_multiple_recipes(ingredients, num_recipes=3):
    """
    Generate multiple recipe suggestions based on detected ingredients

    Args:
        ingredients (list): List of ingredient names
        num_recipes (int): Number of recipe suggestions to generate

    Returns:
        dict: Multiple recipe suggestions
    """
    if not ingredients or len(ingredients) == 0:
        return {
            "error": "No ingredients provided",
            "message": "Please provide at least one ingredient to generate recipes"
        }

    # Try OpenAI first, fallback to demo if unavailable
    if OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)

            ingredients_str = ", ".join(ingredients)
            prompt = f"""You are a professional chef. Suggest {num_recipes} different recipes using the following ingredients: {ingredients_str}

For each recipe, provide:
1. Recipe Name
2. Brief Description (1-2 sentences)
3. Cooking Time
4. Difficulty Level

Keep each recipe suggestion concise but informative."""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful cooking assistant that suggests creative recipes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )

            recipes_text = response.choices[0].message.content

            return {
                "success": True,
                "suggestions": recipes_text,
                "ingredients_used": ingredients,
                "count": num_recipes
            }

        except Exception as e:
            # If OpenAI fails, use demo fallback
            print(f"OpenAI API failed: {e}. Using demo fallback.")
            return generate_demo_suggestions(ingredients, num_recipes)
    else:
        # No API key, use demo
        return generate_demo_suggestions(ingredients, num_recipes)


def generate_demo_suggestions(ingredients, num_recipes=3):
    """
    Generate demo recipe suggestions when OpenAI is not available

    Args:
        ingredients (list): List of ingredient names
        num_recipes (int): Number of suggestions to generate

    Returns:
        dict: Demo suggestions
    """
    ingredients_str = ", ".join(ingredients)

    demo_suggestions = f"""Here are {num_recipes} recipe ideas using your ingredients ({ingredients_str}):

🍝 **Simple Pasta Dish**
A comforting pasta recipe with your detected ingredients plus basic pantry staples. Ready in 25 minutes. Easy difficulty.

🥘 **One-Pan Meal**
Everything cooks together in one pan for easy cleanup. Quick 20-minute preparation with your fresh ingredients. Easy to medium difficulty.

🥗 **Fresh Salad Bowl**
Light and healthy option featuring your vegetables with a simple dressing. Just 15 minutes to prepare. Very easy difficulty.

*These are demo suggestions. Add OpenAI API credits for personalized AI-generated recipe ideas!*
"""

    return {
        "success": True,
        "suggestions": demo_suggestions,
        "ingredients_used": ingredients,
        "count": num_recipes,
        "is_demo": True,
        "message": "Demo suggestions generated! Add OpenAI API credits for personalized AI suggestions."
    }


def generate_cooking_instructions(recipe_data):
    """
    Generate simple, beginner-friendly step-by-step cooking instructions using NLP or demo fallback

    Args:
        recipe_data (dict): Recipe data containing name, ingredients, cuisine, difficulty

    Returns:
        dict: Generated instructions with numbered steps
    """
    if not recipe_data or 'name' not in recipe_data or 'ingredients' not in recipe_data:
        return {
            "error": "Incomplete recipe data",
            "message": "Recipe name and ingredients are required"
        }

    # Try OpenAI first, fallback to demo if unavailable
    if OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)

            # Prepare recipe information
            recipe_name = recipe_data.get('name', 'Unknown Recipe')
            ingredients = recipe_data.get('ingredients', [])
            cuisine = recipe_data.get('cuisine', 'General')
            difficulty = recipe_data.get('difficulty', 'Easy')

            ingredients_str = ", ".join(ingredients) if isinstance(ingredients, list) else str(ingredients)

            # Create a detailed prompt for instruction generation
            prompt = f'''Act as a professional chef teaching beginners to cook.

Generate clear, step-by-step cooking instructions for this recipe:

Recipe Name: {recipe_name}
Cuisine: {cuisine}
Difficulty: {difficulty}
Ingredients: {ingredients_str}

IMPORTANT RULES:
- Use extremely simple language that a beginner can understand
- Number each step clearly (Step 1, Step 2, etc.)
- Keep instructions short and easy to follow
- No advanced cooking terms - explain everything simply
- Include preparation and cooking steps in logical sequence
- Don't skip any important steps
- Limit to maximum 10 steps
- Focus on basic cooking methods: boil, fry, bake, mix, chop, etc.
- End with serving suggestion if appropriate

Format your response as numbered steps only, like:
Step 1: [instruction]
Step 2: [instruction]
...'''

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use GPT-3.5-turbo (more widely available)
                messages=[
                    {"role": "system", "content": "You are a patient cooking teacher who explains recipes in the simplest possible way for complete beginners."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3  # Lower temperature for more consistent, clear instructions
            )

            instructions_text = response.choices[0].message.content

            # Parse the instructions into a structured format
            instructions = []
            step_pattern = r'Step\s*(\d+):\s*(.+)'

            for line in instructions_text.split('\n'):
                line = line.strip()
                if line:
                    match = re.match(step_pattern, line, re.IGNORECASE)
                    if match:
                        step_number = int(match.group(1))
                        description = match.group(2).strip()
                        instructions.append({
                            "step_number": step_number,
                            "description": description
                        })

            # If no structured steps found, return raw text
            if not instructions:
                instructions = [{
                    "step_number": 1,
                    "description": instructions_text
                }]

            return {
                "success": True,
                "instructions": instructions,
                "recipe_name": recipe_name,
                "total_steps": len(instructions)
            }

        except Exception as e:
            # If OpenAI fails, use demo fallback
            print(f"OpenAI API failed: {e}. Using demo fallback.")
            return generate_demo_instructions(recipe_data)
    else:
        # No API key, use demo
        return generate_demo_instructions(recipe_data)


def generate_demo_instructions(recipe_data):
    """
    Generate demo cooking instructions when OpenAI is not available

    Args:
        recipe_data (dict): Recipe data containing name, ingredients, etc.

    Returns:
        dict: Demo instructions
    """
    recipe_name = recipe_data.get('name', 'Your Recipe')
    ingredients = recipe_data.get('ingredients', [])

    # Basic cooking instructions template
    demo_instructions = [
        {
            "step_number": 1,
            "description": f"Prepare all your ingredients for {recipe_name}. Wash, chop, and measure everything you'll need."
        },
        {
            "step_number": 2,
            "description": "Heat oil, butter, or water in a pan over medium heat. This creates the base for your cooking."
        },
        {
            "step_number": 3,
            "description": "Add aromatic ingredients first (like onions, garlic, or spices) and cook for 2-3 minutes until fragrant."
        },
        {
            "step_number": 4,
            "description": "Add your main ingredients. Cook harder vegetables first, then softer ones. Stir occasionally."
        },
        {
            "step_number": 5,
            "description": "Season with salt, pepper, and any herbs or spices. Taste as you go and adjust seasonings."
        },
        {
            "step_number": 6,
            "description": "Continue cooking until everything is done. Stir frequently and check that ingredients are cooked through."
        },
        {
            "step_number": 7,
            "description": "Turn off the heat and let your dish rest for 2-3 minutes. This helps flavors develop."
        },
        {
            "step_number": 8,
            "description": "Serve hot and enjoy your homemade meal!"
        }
    ]

    return {
        "success": True,
        "instructions": demo_instructions,
        "recipe_name": recipe_name,
        "total_steps": len(demo_instructions),
        "is_demo": True,
        "message": "Demo instructions generated! Add OpenAI API credits for personalized AI instructions."
    }


def calculate_basic_nutrition(ingredients, servings=4):
    """
    Calculate basic nutritional information based on common ingredients

    Args:
        ingredients (list): List of ingredient strings
        servings (int): Number of servings

    Returns:
        dict: Basic nutritional information per serving
    """
    # Basic nutritional data for common ingredients (per 100g)
    nutrition_db = {
        # Proteins
        "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
        "beef": {"calories": 250, "protein": 26, "carbs": 0, "fat": 17},
        "fish": {"calories": 206, "protein": 22, "carbs": 0, "fat": 12},
        "tofu": {"calories": 76, "protein": 8, "carbs": 2, "fat": 4.8},
        "eggs": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11},
        "cheese": {"calories": 402, "protein": 7, "carbs": 1.3, "fat": 33},

        # Vegetables
        "tomato": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
        "onion": {"calories": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1},
        "garlic": {"calories": 149, "protein": 6.4, "carbs": 33, "fat": 0.5},
        "carrot": {"calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2},
        "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
        "spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
        "potato": {"calories": 77, "protein": 2, "carbs": 17, "fat": 0.1},

        # Fruits
        "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
        "banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
        "orange": {"calories": 47, "protein": 0.9, "carbs": 12, "fat": 0.1},

        # Grains/Carbs
        "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
        "pasta": {"calories": 371, "protein": 13, "carbs": 75, "fat": 1.5},
        "bread": {"calories": 265, "protein": 9, "carbs": 49, "fat": 3.2},
        "flour": {"calories": 364, "protein": 10, "carbs": 76, "fat": 1},

        # Dairy
        "milk": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3},
        "yogurt": {"calories": 61, "protein": 3.5, "carbs": 4.7, "fat": 3.3},
        "butter": {"calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81},

        # Oils/Condiments
        "oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100},
        "olive oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100},

        # Default values for unknown ingredients
        "default": {"calories": 100, "protein": 2, "carbs": 10, "fat": 5}
    }

    total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()

        # Find matching ingredient in nutrition database
        nutrition_data = None
        for key, data in nutrition_db.items():
            if key in ingredient_lower:
                nutrition_data = data
                break

        # Use default if no match found
        if not nutrition_data:
            nutrition_data = nutrition_db["default"]

        # Estimate quantity (simplified - assumes average portion)
        quantity_factor = 1.0  # Assume 100g portions

        # Adjust for quantity indicators in ingredient string
        if any(word in ingredient_lower for word in ['cup', 'cups']):
            quantity_factor = 2.0  # Roughly 200g for a cup
        elif any(word in ingredient_lower for word in ['tbsp', 'tablespoon']):
            quantity_factor = 0.2  # Roughly 20g for a tbsp
        elif any(word in ingredient_lower for word in ['tsp', 'teaspoon']):
            quantity_factor = 0.1  # Roughly 10g for a tsp
        elif any(word in ingredient_lower for word in ['lb', 'pound']):
            quantity_factor = 5.0  # Roughly 500g for a pound
        elif 'kg' in ingredient_lower:
            quantity_factor = 10.0  # 1kg

        total_nutrition["calories"] += nutrition_data["calories"] * quantity_factor
        total_nutrition["protein"] += nutrition_data["protein"] * quantity_factor
        total_nutrition["carbs"] += nutrition_data["carbs"] * quantity_factor
        total_nutrition["fat"] += nutrition_data["fat"] * quantity_factor

    # Calculate per serving values
    per_serving = {
        "calories": round(total_nutrition["calories"] / servings),
        "protein": round(total_nutrition["protein"] / servings, 1),
        "carbohydrates": round(total_nutrition["carbs"] / servings, 1),
        "fat": round(total_nutrition["fat"] / servings, 1),
        "fiber": round(total_nutrition["carbs"] * 0.1 / servings, 1),  # Estimate fiber as 10% of carbs
        "sugar": round(total_nutrition["carbs"] * 0.2 / servings, 1),  # Estimate sugar as 20% of carbs
        "sodium": round(500 / servings, 1)  # Rough estimate of sodium per serving
    }

    return per_serving


def enhance_recipe_with_nlp_instructions(recipe_data):
    """
    Enhance existing recipe data with NLP-generated cooking instructions

    Args:
        recipe_data (dict): Complete recipe data including name, ingredients, etc.

    Returns:
        dict: Recipe data with added NLP-generated instructions
    """
    # Extract basic recipe info for instruction generation
    basic_recipe = {
        "name": recipe_data.get("title") or recipe_data.get("name"),
        "ingredients": [ing["name"] if isinstance(ing, dict) else str(ing)
                       for ing in recipe_data.get("ingredients", [])],
        "cuisine": recipe_data.get("cuisine_type", "General"),
        "difficulty": recipe_data.get("difficulty_level", "Easy")
    }

    # Generate instructions
    instructions_result = generate_cooking_instructions(basic_recipe)

    if "error" in instructions_result:
        # Return original recipe data if instruction generation fails
        return recipe_data

    # Add generated instructions to recipe data
    enhanced_recipe = recipe_data.copy()
    enhanced_recipe["nlp_instructions"] = instructions_result["instructions"]
    enhanced_recipe["instructions_generated"] = True

    return enhanced_recipe

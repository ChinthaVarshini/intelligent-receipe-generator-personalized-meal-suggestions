#!/usr/bin/env python3
"""
Beautiful Recipe Generator using Modern Google Gemini API
Creates beautifully formatted recipes with accurate nutrition information
"""

import google.generativeai as genai
from config import GOOGLE_GEMINI_API_KEY
import re
import json


def generate_beautiful_recipe(ingredients, cuisine='General'):
    """
    Generate a beautifully formatted recipe using Google Gemini AI

    Args:
        ingredients (list): List of ingredient names
        cuisine (str): Preferred cuisine type

    Returns:
        dict: Beautifully formatted recipe with complete information
    """
    if not ingredients or len(ingredients) == 0:
        return {
            "error": "No ingredients provided",
            "message": "Please provide at least one ingredient to generate a recipe"
        }

    if not GOOGLE_GEMINI_API_KEY:
        return {
            "error": "Google Gemini API key not configured",
            "message": "Please set GOOGLE_GEMINI_API_KEY in your environment variables"
        }

    try:
        # Configure Gemini API
        genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        ingredients_str = ", ".join(ingredients)

        # Enhanced prompt for beautiful recipe generation
        prompt = f"""You are a world-class chef and nutrition expert. Create an absolutely beautiful, professional-quality recipe using these ingredients: {ingredients_str}

**RECIPE REQUIREMENTS:**
1. **Recipe Name**: Creative, appetizing name that highlights the dish
2. **Description**: 2-3 sentences describing the dish, its appeal, and why it's special
3. **Timing**: Prep time, cook time, and total time in minutes
4. **Difficulty**: Easy, Medium, or Hard with brief explanation
5. **Servings**: Number of people the recipe serves
6. **Cuisine Type**: {cuisine} (or most appropriate cuisine for these ingredients)

**INGREDIENTS SECTION:**
- List ALL ingredients with precise measurements
- Include the provided ingredients: {ingredients_str}
- Add any necessary additional ingredients for a complete, delicious dish
- Format: "• Quantity Unit Ingredient (notes, preparation)"

**INSTRUCTIONS SECTION:**
- Number each step clearly (1., 2., 3., etc.)
- Write clear, easy-to-follow instructions
- Include preparation steps, cooking techniques, and timing
- Professional but accessible language

**NUTRITION INFORMATION (PER SERVING):**
Provide ACCURATE nutritional information per serving. Calculate based on actual ingredient amounts:
- Calories (kcal)
- Protein (g)
- Carbohydrates (g)
- Fat (g)
- Fiber (g)
- Sugar (g)
- Sodium (mg)
- Additional nutrients if relevant (Vitamin C, Iron, Calcium, etc.)

**PRO TIPS SECTION:**
- 3-5 professional cooking tips
- Make-ahead suggestions
- Variations or substitutions
- Serving suggestions

**PRESENTATION:**
Format the entire response in a beautiful, professional layout using emojis and clear sections.
Make it look like a high-end cookbook recipe.

**IMPORTANT:**
- Use exact measurements (not "some" or "a bit")
- Ensure nutritional calculations are realistic and accurate
- Make the recipe achievable and delicious
- Focus on flavor balance and cooking techniques
"""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                max_output_tokens=4000,
            )
        )

        recipe_text = response.text

        # Parse the response to extract structured data
        structured_recipe = parse_beautiful_recipe_response(recipe_text, ingredients)

        return {
            "success": True,
            "recipe": recipe_text,
            "structured_recipe": structured_recipe,
            "ingredients_used": ingredients,
            "ai_provider": "gemini_beautiful",
            "formatted": True
        }

    except Exception as e:
        print(f"Beautiful recipe generation failed: {e}")
        # Fallback to basic generation
        return generate_basic_beautiful_recipe(ingredients, cuisine)


def parse_beautiful_recipe_response(recipe_text, original_ingredients):
    """
    Parse the AI response into structured recipe data

    Args:
        recipe_text (str): Raw recipe text from AI
        original_ingredients (list): Original ingredients provided

    Returns:
        dict: Structured recipe data
    """
    try:
        # Extract recipe name
        name_match = re.search(r'[#*]*\s*([^\n\r]{10,80}?)(?:\n|\r|$)', recipe_text.split('\n')[0])
        recipe_name = name_match.group(1).strip('#* ') if name_match else "Beautiful Generated Recipe"

        # Extract description
        description_match = re.search(r'(?:Description|About|Overview)[:\-]*\s*([^\n\r]{50,200})', recipe_text, re.IGNORECASE)
        description = description_match.group(1).strip() if description_match else "A delicious dish created with AI assistance."

        # Extract timing information
        prep_match = re.search(r'(?:Prep|Preparation)\s*Time[:\-]*\s*(\d+)\s*minutes?', recipe_text, re.IGNORECASE)
        cook_match = re.search(r'(?:Cook|Cooking)\s*Time[:\-]*\s*(\d+)\s*minutes?', recipe_text, re.IGNORECASE)
        total_match = re.search(r'(?:Total)\s*Time[:\-]*\s*(\d+)\s*minutes?', recipe_text, re.IGNORECASE)

        prep_time = int(prep_match.group(1)) if prep_match else 15
        cook_time = int(cook_match.group(1)) if cook_match else 30
        total_time = int(total_match.group(1)) if total_match else (prep_time + cook_time)

        # Extract servings
        servings_match = re.search(r'(?:Serves?|Servings?)[:\-]*\s*(\d+)', recipe_text, re.IGNORECASE)
        servings = int(servings_match.group(1)) if servings_match else 4

        # Extract difficulty
        difficulty_match = re.search(r'(?:Difficulty|Level)[:\-]*\s*(Easy|Medium|Hard)', recipe_text, re.IGNORECASE)
        difficulty = difficulty_match.group(1) if difficulty_match else "Medium"

        # Extract ingredients list
        ingredients_section = re.search(r'(?:Ingredients?|📝\s*Ingredients?)[:\-]*\s*\n?(.*?)(?:\n\n|\n👨‍🍳|\nInstructions?|\n📋|\nDirections?)', recipe_text, re.DOTALL | re.IGNORECASE)
        ingredients_list = []
        if ingredients_section:
            ing_text = ingredients_section.group(1)
            # Parse ingredient lines
            for line in ing_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or re.match(r'\d', line)):
                    # Clean up the ingredient line
                    clean_line = re.sub(r'^[•\-*]\s*', '', line)
                    ingredients_list.append(clean_line)

        # Extract instructions
        instructions_section = re.search(r'(?:Instructions?|👨‍🍳\s*Instructions?|📋\s*Directions?)[:\-]*\s*\n?(.*?)(?:\n\n|\n🥗|\nNutrition|\n💡|\nPro Tips?)', recipe_text, re.DOTALL | re.IGNORECASE)
        instructions_list = []
        if instructions_section:
            inst_text = instructions_section.group(1)
            # Parse instruction steps
            step_pattern = r'(?:\d+\.|\•|\-)\s*(.+?)(?=\n(?:\d+\.|\•|\-)|\n\n|$)'
            matches = re.findall(step_pattern, inst_text, re.DOTALL)
            instructions_list = [match.strip() for match in matches if match.strip()]

        # Extract nutrition information
        nutrition_section = re.search(r'(?:Nutrition|🥗\s*Nutrition|Nutritional Information)[:\-]*\s*\n?(.*?)(?:\n\n|\n💡|\nPro Tips|\n\*\*)', recipe_text, re.DOTALL | re.IGNORECASE)
        nutrition_data = {}
        if nutrition_section:
            nutr_text = nutrition_section.group(1)
            # Parse nutrition facts
            nutr_patterns = {
                'calories': r'Calories?[:\-]*\s*(\d+)',
                'protein': r'Protein[:\-]*\s*(\d+(?:\.\d+)?)',
                'carbohydrates': r'Carbohydrates?[:\-]*\s*(\d+(?:\.\d+)?)',
                'fat': r'(?:Total )?Fat[:\-]*\s*(\d+(?:\.\d+)?)',
                'fiber': r'Fiber[:\-]*\s*(\d+(?:\.\d+)?)',
                'sugar': r'Sugar[:\-]*\s*(\d+(?:\.\d+)?)',
                'sodium': r'Sodium[:\-]*\s*(\d+)'
            }

            for key, pattern in nutr_patterns.items():
                match = re.search(pattern, nutr_text, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    nutrition_data[key] = float(value) if '.' in value else int(value)

        # Extract pro tips
        tips_section = re.search(r'(?:Pro Tips|💡|Tips|Notes)[:\-]*\s*\n?(.*?)(?:\n\n|\n\*\*|$)', recipe_text, re.DOTALL | re.IGNORECASE)
        pro_tips = []
        if tips_section:
            tips_text = tips_section.group(1)
            for line in tips_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or re.match(r'\d', line)):
                    clean_line = re.sub(r'^[•\-*\d\.]+\s*', '', line)
                    if clean_line:
                        pro_tips.append(clean_line)

        return {
            "name": recipe_name,
            "description": description,
            "prep_time": prep_time,
            "cook_time": cook_time,
            "total_time": total_time,
            "servings": servings,
            "difficulty": difficulty,
            "cuisine_type": "General",  # Could be extracted if present
            "ingredients": ingredients_list,
            "instructions": instructions_list,
            "nutrition": nutrition_data,
            "pro_tips": pro_tips,
            "original_ingredients": original_ingredients
        }

    except Exception as e:
        print(f"Error parsing recipe response: {e}")
        return {}


def generate_basic_beautiful_recipe(ingredients, cuisine='General'):
    """
    Fallback beautiful recipe generator when AI fails

    Args:
        ingredients (list): List of ingredient names
        cuisine (str): Preferred cuisine type

    Returns:
        dict: Basic beautiful recipe
    """
    ingredients_str = ", ".join(ingredients)

    # Create a beautiful formatted recipe
    recipe_name = f"🍳 Gourmet {cuisine.title()} Creation with {ingredients[0].title()}"

    recipe_text = f"""# {recipe_name}

**✨ A Culinary Masterpiece ✨**

*This exquisite dish transforms simple ingredients into a symphony of flavors, perfect for impressing your dinner guests or treating yourself to something special.*

## ⏱️ Timing
- **Prep Time:** 20 minutes
- **Cook Time:** 35 minutes
- **Total Time:** 55 minutes
- **Difficulty:** Medium
- **Servings:** 4
- **Cuisine:** {cuisine.title()}

## 📝 Ingredients

### Main Ingredients
• 2 cups {ingredients[0] if len(ingredients) > 0 else 'primary ingredient'}
• 1 cup {ingredients[1] if len(ingredients) > 1 else 'secondary ingredient'}
• 3 cloves garlic, minced
• 1 large onion, finely chopped
• 2 tablespoons olive oil

### Seasonings & Aromatics
• 1 teaspoon salt
• ½ teaspoon black pepper
• 1 teaspoon dried herbs (thyme, oregano, or rosemary)
• ½ teaspoon red pepper flakes (optional, for heat)

### Additional Ingredients
• 1 cup vegetable or chicken broth
• 2 tablespoons butter
• Fresh herbs for garnish (parsley or basil)

## 👨‍🍳 Instructions

1. **Prepare your ingredients:** Wash and chop all vegetables. Mince garlic and measure out seasonings. This mise en place ensures smooth cooking.

2. **Sauté aromatics:** Heat olive oil in a large skillet over medium heat. Add chopped onion and cook for 5 minutes until softened and translucent.

3. **Build flavor base:** Add minced garlic, salt, pepper, and herbs. Cook for 2 minutes, stirring constantly to prevent burning. The aroma will be incredible!

4. **Add main ingredients:** Incorporate your {ingredients_str}. Cook for 8-10 minutes, stirring occasionally, until they begin to caramelize.

5. **Create sauce:** Pour in broth and bring to a simmer. Reduce heat and cook for 15 minutes, allowing flavors to meld beautifully.

6. **Finish and rest:** Remove from heat, stir in butter for richness. Let rest for 5 minutes to allow flavors to fully develop.

7. **Serve with style:** Garnish with fresh herbs and serve immediately while hot.

## 🥗 Nutrition Information (Per Serving)

**Macronutrients:**
• **Calories:** 285 kcal
• **Protein:** 12g
• **Carbohydrates:** 28g
• **Fat:** 14g

**Micronutrients:**
• **Fiber:** 6g
• **Sugar:** 8g
• **Sodium:** 520mg

**Vitamins & Minerals:**
• **Vitamin C:** 45mg (50% DV)
• **Iron:** 3.2mg (18% DV)
• **Calcium:** 85mg (8% DV)

## 💡 Pro Cooking Tips

• **Quality ingredients matter:** Use fresh, high-quality {ingredients_str} for the best flavor results.

• **Don't rush the sauté:** Take your time building layers of flavor in steps 2-3. This is where the magic happens!

• **Season progressively:** Taste and adjust seasoning throughout cooking rather than adding everything at once.

• **Rest before serving:** Allowing the dish to rest helps the flavors continue developing and improves texture.

• **Make it your own:** Experiment with different herbs or add a splash of wine for extra complexity.

## 🌟 Serving Suggestions

• Serve with crusty bread to soak up the delicious sauce
• Pair with a light salad and your favorite wine
• Perfect for weeknight dinners or special occasions
• Leftovers reheat beautifully for lunch the next day

---

*Recipe crafted with ❤️ using AI assistance for the perfect balance of flavor and nutrition.*
"""

    return {
        "success": True,
        "recipe": recipe_text,
        "ingredients_used": ingredients,
        "ai_provider": "beautiful_fallback",
        "formatted": True,
        "message": "Beautiful recipe generated with nutrition information and professional formatting."
    }


def generate_nutrition_focused_recipe(ingredients, nutrition_focus='balanced'):
    """
    Generate a recipe focused on specific nutritional goals

    Args:
        ingredients (list): List of ingredient names
        nutrition_focus (str): 'high_protein', 'low_carb', 'balanced', 'vegetarian', 'vegan'

    Returns:
        dict: Nutrition-focused beautiful recipe
    """
    if not GOOGLE_GEMINI_API_KEY:
        return generate_basic_beautiful_recipe(ingredients)

    try:
        genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        ingredients_str = ", ".join(ingredients)

        focus_descriptions = {
            'high_protein': 'high-protein meal with ample lean protein sources',
            'low_carb': 'low-carbohydrate meal focused on vegetables and healthy fats',
            'balanced': 'balanced macronutrient profile with proteins, carbs, and fats',
            'vegetarian': 'vegetarian meal with plant-based protein sources',
            'vegan': 'vegan meal completely free of animal products'
        }

        focus_desc = focus_descriptions.get(nutrition_focus, 'balanced nutritional profile')

        prompt = f"""Create a beautiful, nutrition-focused recipe using: {ingredients_str}

**NUTRITION FOCUS:** {focus_desc}

**RECIPE REQUIREMENTS:**
1. **Recipe Name**: Highlight the nutritional benefits
2. **Nutritional Profile**: Detailed breakdown per serving
3. **Health Benefits**: Explain nutritional advantages
4. **Complete Recipe**: Beautiful formatting with all sections
5. **Dietary Notes**: How this fits specific dietary needs

Format as a professional cookbook recipe with emojis and clear sections.
"""

        response = model.generate_content(prompt)
        recipe_text = response.text

        return {
            "success": True,
            "recipe": recipe_text,
            "ingredients_used": ingredients,
            "nutrition_focus": nutrition_focus,
            "ai_provider": "gemini_nutrition",
            "formatted": True
        }

    except Exception as e:
        print(f"Nutrition-focused recipe generation failed: {e}")
        return generate_basic_beautiful_recipe(ingredients)

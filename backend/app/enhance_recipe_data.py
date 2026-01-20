#!/usr/bin/env python3
"""
Enhance Recipe Data with Recommendation Fields
Adds cuisine_type, difficulty_level, dietary_preferences, and other fields needed for recommendations.
"""

from database_models import init_db, db, Recipe, Ingredient
from flask import Flask
from config import DATABASE_URL
import json
import random

# Create Flask app for database operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

# Cuisine mapping based on recipe titles and ingredients
CUISINE_MAPPING = {
    'italian': ['pasta', 'pizza', 'risotto', 'carbonara', 'primavera', 'alfredo', 'pesto', 'aglio', 'olio', 'arrabbiata'],
    'indian': ['curry', 'masala', 'tikka', 'biryani', 'tandoori', 'naan', 'cumin', 'turmeric', 'garam masala'],
    'chinese': ['wok', 'stir fry', 'dumpling', 'noodle', 'soy sauce', 'sesame', 'ginger', 'tofu'],
    'mexican': ['taco', 'burrito', 'enchilada', 'salsa', 'guacamole', 'cumin', 'chili', 'lime'],
    'mediterranean': ['falafel', 'hummus', 'tzatziki', 'olive oil', 'feta', 'oregano', 'quinoa'],
    'american': ['burger', 'hot dog', 'mac and cheese', 'grilled', 'bbq'],
    'french': ['crepe', 'ratatouille', 'baguette', 'butter', 'cream'],
    'thai': ['thai', 'pad thai', 'curry', 'coconut milk', 'lemongrass'],
    'japanese': ['sushi', 'ramen', 'tempura', 'miso', 'wasabi']
}

DIFFICULTY_MAPPING = {
    'easy': ['simple', 'basic', 'quick', 'easy'],
    'medium': ['moderate', 'intermediate'],
    'hard': ['advanced', 'complex', 'difficult', 'expert']
}

def determine_cuisine(title, ingredients):
    """Determine cuisine type based on title and ingredients"""
    title_lower = title.lower()
    ingredient_names = [ing.name.lower() for ing in ingredients]

    # Check title first
    for cuisine, keywords in CUISINE_MAPPING.items():
        if any(keyword in title_lower for keyword in keywords):
            return cuisine.title()

    # Check ingredients
    for cuisine, keywords in CUISINE_MAPPING.items():
        if any(any(keyword in ing for ing in ingredient_names) for keyword in keywords):
            return cuisine.title()

    # Default cuisines
    return random.choice(['Italian', 'Chinese', 'Indian', 'Mexican', 'American'])

def determine_difficulty(prep_time, cook_time, ingredient_count):
    """Determine difficulty level based on time and complexity"""
    total_time = (prep_time or 0) + (cook_time or 0)

    if total_time <= 30 and ingredient_count <= 8:
        return 'Easy'
    elif total_time <= 60 and ingredient_count <= 12:
        return 'Medium'
    else:
        return 'Hard'

def determine_dietary_preferences(ingredients):
    """Determine dietary preferences based on ingredients"""
    preferences = []
    ingredient_names = [ing.name.lower() for ing in ingredients]

    # Check for meat
    meat_ingredients = ['chicken', 'beef', 'pork', 'fish', 'lamb', 'turkey', 'bacon', 'sausage', 'pancetta']
    has_meat = any(any(meat in ing for meat in meat_ingredients) for ing in ingredient_names)

    # Check for dairy
    dairy_ingredients = ['cheese', 'milk', 'cream', 'butter', 'yogurt', 'feta']
    has_dairy = any(any(dairy in ing for dairy in dairy_ingredients) for ing in ingredient_names)

    if not has_meat:
        preferences.append('vegetarian')
        if not has_dairy:
            preferences.append('vegan')

    # Check for gluten
    gluten_ingredients = ['flour', 'pasta', 'bread', 'wheat', 'barley']
    has_gluten = any(any(gluten in ing for gluten in gluten_ingredients) for ing in ingredient_names)

    if not has_gluten:
        preferences.append('gluten-free')

    return preferences

def enhance_recipes():
    """Enhance existing recipes with recommendation fields"""
    print("Enhancing recipe data for recommendations...")

    with app.app_context():
        recipes = Recipe.query.all()
        updated_count = 0

        for recipe in recipes:
            # Get ingredients for analysis
            ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()

            # Determine cuisine
            cuisine = determine_cuisine(recipe.title, ingredients)

            # Determine difficulty
            difficulty = determine_difficulty(recipe.prep_time, recipe.cook_time, len(ingredients))

            # Determine dietary preferences
            dietary_prefs = determine_dietary_preferences(ingredients)
            dietary_prefs_json = json.dumps(dietary_prefs) if dietary_prefs else None

            # Calculate total time
            total_time = (recipe.prep_time or 0) + (recipe.cook_time or 0)

            # Update recipe
            recipe.cuisine_type = cuisine
            recipe.difficulty_level = difficulty
            recipe.dietary_preferences = dietary_prefs_json
            recipe.total_time = total_time
            recipe.source = 'sample_data'

            updated_count += 1

            if updated_count % 10 == 0:
                print(f"Updated {updated_count} recipes...")

        # Commit changes
        db.session.commit()

        print(f"Successfully enhanced {updated_count} recipes!")
        print("\nSample enhanced recipes:")

        sample_recipes = Recipe.query.limit(3).all()
        for recipe in sample_recipes:
            print(f"- {recipe.title}: {recipe.cuisine_type} | {recipe.difficulty_level} | {recipe.dietary_preferences}")

def main():
    """Main function"""
    print("Recipe Data Enhancement for Recommendations")
    print("=" * 45)

    enhance_recipes()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Recipe Data Collection and Population Script
Collects recipe data from public APIs and populates the database.
Supports Spoonacular, Edamam, and TheMealDB APIs.
"""

import requests
import json
import time
import random
from datetime import datetime
from config import (
    SPOONACULAR_API_KEY, EDAMAM_APP_ID, EDAMAM_APP_KEY, THEMEALDB_API_KEY,
    DATABASE_URL
)
from database_models import (
    init_db, db, create_user, create_recipe, add_ingredient,
    add_instruction, add_nutrition, get_db
)
from flask import Flask

# Create Flask app for database operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

class RecipeDataCollector:
    """Collects recipe data from various APIs"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Intelligent-Recipe-Generator/1.0'
        })

    def collect_spoonacular_recipes(self, limit=200):
        """Collect recipes from Spoonacular API"""
        recipes = []
        base_url = "https://api.spoonacular.com/recipes"

        if not SPOONACULAR_API_KEY:
            print("Spoonacular API key not configured, skipping...")
            return recipes

        # Get random recipes
        params = {
            'apiKey': SPOONACULAR_API_KEY,
            'number': min(limit, 100),  # API limit is 100 per request
            'sort': 'random'
        }

        try:
            response = self.session.get(f"{base_url}/random", params=params)
            response.raise_for_status()
            data = response.json()

            for recipe_data in data.get('recipes', []):
                recipe = self._parse_spoonacular_recipe(recipe_data)
                if recipe:
                    recipes.append(recipe)

            print(f"Collected {len(recipes)} recipes from Spoonacular")

        except Exception as e:
            print(f"Error collecting from Spoonacular: {e}")

        return recipes

    def collect_edamam_recipes(self, limit=200):
        """Collect recipes from Edamam API"""
        recipes = []
        base_url = "https://api.edamam.com/api/recipes/v2"

        if not EDAMAM_APP_ID or not EDAMAM_APP_KEY:
            print("Edamam API credentials not configured, skipping...")
            return recipes

        params = {
            'type': 'public',
            'app_id': EDAMAM_APP_ID,
            'app_key': EDAMAM_APP_KEY,
            'random': 'true'
        }

        collected = 0
        while collected < limit:
            try:
                response = self.session.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()

                for hit in data.get('hits', []):
                    recipe_data = hit.get('recipe', {})
                    recipe = self._parse_edamam_recipe(recipe_data)
                    if recipe:
                        recipes.append(recipe)
                        collected += 1
                        if collected >= limit:
                            break

                # Get next page if available
                if '_links' in data and 'next' in data['_links']:
                    next_url = data['_links']['next']['href']
                    response = self.session.get(next_url)
                    response.raise_for_status()
                    data = response.json()
                else:
                    break

                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"Error collecting from Edamam: {e}")
                break

        print(f"Collected {len(recipes)} recipes from Edamam")
        return recipes

    def collect_themealdb_recipes(self, limit=100):
        """Collect recipes from TheMealDB API"""
        recipes = []
        base_url = "https://www.themealdb.com/api/json/v1"

        api_key = THEMEALDB_API_KEY or "1"  # Default API key for TheMealDB

        try:
            # Get all categories first
            response = self.session.get(f"{base_url}/{api_key}/categories.php")
            response.raise_for_status()
            categories_data = response.json()

            categories = [cat['strCategory'] for cat in categories_data.get('categories', [])]

            collected = 0
            for category in categories:
                if collected >= limit:
                    break

                # Get recipes by category
                response = self.session.get(f"{base_url}/{api_key}/filter.php",
                                          params={'c': category})
                response.raise_for_status()
                data = response.json()

                meals = data.get('meals', [])[:10]  # Limit per category

                for meal in meals:
                    if collected >= limit:
                        break

                    # Get detailed recipe
                    response = self.session.get(f"{base_url}/{api_key}/lookup.php",
                                              params={'i': meal['idMeal']})
                    response.raise_for_status()
                    detail_data = response.json()

                    if detail_data.get('meals'):
                        recipe = self._parse_themealdb_recipe(detail_data['meals'][0])
                        if recipe:
                            recipes.append(recipe)
                            collected += 1

                time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"Error collecting from TheMealDB: {e}")

        print(f"Collected {len(recipes)} recipes from TheMealDB")
        return recipes

    def _parse_spoonacular_recipe(self, data):
        """Parse Spoonacular recipe data"""
        try:
            recipe = {
                'title': data.get('title', '').strip(),
                'description': data.get('summary', ''),
                'prep_time': data.get('preparationMinutes') or data.get('readyInMinutes', 30),
                'cook_time': data.get('cookingMinutes') or data.get('readyInMinutes', 30),
                'servings': data.get('servings', 4),
                'source': 'spoonacular',
                'source_id': str(data.get('id')),
                'image_url': data.get('image'),
                'ingredients': [],
                'instructions': [],
                'nutrition': {}
            }

            # Parse ingredients
            for ingredient in data.get('extendedIngredients', []):
                recipe['ingredients'].append({
                    'name': ingredient.get('name', ''),
                    'quantity': ingredient.get('amount'),
                    'unit': ingredient.get('unit', ''),
                    'notes': ingredient.get('original', '')
                })

            # Parse instructions
            for step in data.get('analyzedInstructions', []):
                for instruction in step.get('steps', []):
                    recipe['instructions'].append({
                        'step_number': instruction.get('number', 1),
                        'description': instruction.get('step', '')
                    })

            # Parse nutrition
            if 'nutrition' in data:
                nutrition = data['nutrition']
                recipe['nutrition'] = {
                    'calories': nutrition.get('nutrients', {}).get('calories', {}).get('amount'),
                    'protein': nutrition.get('nutrients', {}).get('protein', {}).get('amount'),
                    'carbohydrates': nutrition.get('nutrients', {}).get('carbohydrates', {}).get('amount'),
                    'fat': nutrition.get('nutrients', {}).get('fat', {}).get('amount'),
                    'fiber': nutrition.get('nutrients', {}).get('fiber', {}).get('amount'),
                    'sugar': nutrition.get('nutrients', {}).get('sugar', {}).get('amount'),
                    'sodium': nutrition.get('nutrients', {}).get('sodium', {}).get('amount')
                }

            return recipe if recipe['title'] and recipe['ingredients'] else None

        except Exception as e:
            print(f"Error parsing Spoonacular recipe: {e}")
            return None

    def _parse_edamam_recipe(self, data):
        """Parse Edamam recipe data"""
        try:
            recipe = {
                'title': data.get('label', '').strip(),
                'description': f"A {', '.join(data.get('healthLabels', [])[:3])} recipe",
                'prep_time': 30,  # Edamam doesn't provide prep time
                'cook_time': 30,
                'servings': data.get('yield', 4),
                'source': 'edamam',
                'source_id': data.get('uri', '').split('#')[1] if '#' in str(data.get('uri', '')) else '',
                'image_url': data.get('image'),
                'ingredients': [],
                'instructions': [],
                'nutrition': {}
            }

            # Parse ingredients
            for ingredient in data.get('ingredients', []):
                recipe['ingredients'].append({
                    'name': ingredient.get('food', ''),
                    'quantity': ingredient.get('quantity'),
                    'unit': ingredient.get('measure', ''),
                    'notes': ingredient.get('text', '')
                })

            # Edamam doesn't provide instructions, add a placeholder
            recipe['instructions'].append({
                'step_number': 1,
                'description': 'Follow standard cooking procedures for this recipe type.'
            })

            # Parse nutrition
            if 'totalNutrients' in data:
                nutrients = data['totalNutrients']
                recipe['nutrition'] = {
                    'calories': data.get('calories'),
                    'protein': nutrients.get('PROCNT', {}).get('quantity'),
                    'carbohydrates': nutrients.get('CHOCDF', {}).get('quantity'),
                    'fat': nutrients.get('FAT', {}).get('quantity'),
                    'fiber': nutrients.get('FIBTG', {}).get('quantity'),
                    'sugar': nutrients.get('SUGAR', {}).get('quantity'),
                    'sodium': nutrients.get('NA', {}).get('quantity')
                }

            return recipe if recipe['title'] and recipe['ingredients'] else None

        except Exception as e:
            print(f"Error parsing Edamam recipe: {e}")
            return None

    def _parse_themealdb_recipe(self, data):
        """Parse TheMealDB recipe data"""
        try:
            recipe = {
                'title': data.get('strMeal', '').strip(),
                'description': f"{data.get('strCategory', '')} recipe from {data.get('strArea', '')}",
                'prep_time': 30,
                'cook_time': 30,
                'servings': 4,
                'source': 'themealdb',
                'source_id': data.get('idMeal'),
                'image_url': data.get('strMealThumb'),
                'ingredients': [],
                'instructions': [],
                'nutrition': {}
            }

            # Parse ingredients (TheMealDB has up to 20 ingredients)
            for i in range(1, 21):
                ingredient = data.get(f'strIngredient{i}')
                measure = data.get(f'strMeasure{i}')

                if ingredient and ingredient.strip():
                    recipe['ingredients'].append({
                        'name': ingredient.strip(),
                        'quantity': None,
                        'unit': '',
                        'notes': measure.strip() if measure else ''
                    })

            # Parse instructions
            instructions_text = data.get('strInstructions', '')
            if instructions_text:
                # Split by periods and create steps
                steps = [step.strip() for step in instructions_text.split('.') if step.strip()]
                for i, step in enumerate(steps, 1):
                    recipe['instructions'].append({
                        'step_number': i,
                        'description': step + '.'
                    })

            return recipe if recipe['title'] and recipe['ingredients'] else None

        except Exception as e:
            print(f"Error parsing TheMealDB recipe: {e}")
            return None

def populate_database(recipes):
    """Populate the database with collected recipes"""
    print(f"Starting database population with {len(recipes)} recipes...")

    with app.app_context():
        # Create or get a default user
        user = db.session.query(get_db().User).filter_by(username='recipe_collector').first()
        if not user:
            user = create_user('recipe_collector', 'collector@example.com')

        successful = 0
        failed = 0

        for recipe_data in recipes:
            try:
                # Check if recipe already exists
                existing = db.session.query(get_db().Recipe).filter_by(
                    title=recipe_data['title'],
                    user_id=user.id
                ).first()

                if existing:
                    continue

                # Create recipe
                recipe = create_recipe(
                    user_id=user.id,
                    title=recipe_data['title'],
                    description=recipe_data['description'],
                    prep_time=recipe_data['prep_time'],
                    cook_time=recipe_data['cook_time'],
                    servings=recipe_data['servings']
                )

                # Add ingredients
                for ingredient_data in recipe_data['ingredients']:
                    add_ingredient(
                        recipe_id=recipe.id,
                        name=ingredient_data['name'],
                        quantity=ingredient_data['quantity'],
                        unit=ingredient_data['unit'],
                        notes=ingredient_data['notes']
                    )

                # Add instructions
                for instruction_data in recipe_data['instructions']:
                    add_instruction(
                        recipe_id=recipe.id,
                        step_number=instruction_data['step_number'],
                        description=instruction_data['description']
                    )

                # Add nutrition if available
                if recipe_data['nutrition']:
                    add_nutrition(
                        recipe_id=recipe.id,
                        calories=recipe_data['nutrition'].get('calories'),
                        protein=recipe_data['nutrition'].get('protein'),
                        carbohydrates=recipe_data['nutrition'].get('carbohydrates'),
                        fat=recipe_data['nutrition'].get('fat'),
                        fiber=recipe_data['nutrition'].get('fiber'),
                        sugar=recipe_data['nutrition'].get('sugar'),
                        sodium=recipe_data['nutrition'].get('sodium')
                    )

                successful += 1
                if successful % 50 == 0:
                    print(f"Processed {successful} recipes...")

            except Exception as e:
                print(f"Error saving recipe '{recipe_data.get('title', 'Unknown')}': {e}")
                failed += 1
                continue

        db.session.commit()
        print(f"Database population complete!")
        print(f"Successfully added: {successful} recipes")
        print(f"Failed to add: {failed} recipes")
        print(f"Total recipes in database: {db.session.query(get_db().Recipe).count()}")

def main():
    """Main function to collect and populate recipe data"""
    print("Starting Recipe Data Collection and Population")
    print("=" * 50)

    collector = RecipeDataCollector()
    all_recipes = []

    # Collect from Spoonacular
    print("\n1. Collecting from Spoonacular API...")
    spoonacular_recipes = collector.collect_spoonacular_recipes(limit=200)
    all_recipes.extend(spoonacular_recipes)

    # Collect from Edamam
    print("\n2. Collecting from Edamam API...")
    edamam_recipes = collector.collect_edamam_recipes(limit=200)
    all_recipes.extend(edamam_recipes)

    # Collect from TheMealDB
    print("\n3. Collecting from TheMealDB API...")
    themealdb_recipes = collector.collect_themealdb_recipes(limit=100)
    all_recipes.extend(themealdb_recipes)

    print(f"\nTotal recipes collected: {len(all_recipes)}")

    # Remove duplicates based on title
    unique_recipes = []
    seen_titles = set()
    for recipe in all_recipes:
        title = recipe['title'].lower().strip()
        if title not in seen_titles and len(recipe['ingredients']) > 0:
            seen_titles.add(title)
            unique_recipes.append(recipe)

    print(f"Unique recipes after deduplication: {len(unique_recipes)}")

    # Populate database
    if unique_recipes:
        populate_database(unique_recipes)
    else:
        print("No recipes to populate database with.")

if __name__ == "__main__":
    main()

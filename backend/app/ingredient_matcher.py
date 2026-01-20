"""
Advanced Ingredient Matching Algorithm
Implements fuzzy matching techniques and calculates match percentages.
"""

import re
from difflib import SequenceMatcher
from collections import defaultdict
import math
from database_models import db, Recipe, Ingredient

class IngredientMatcher:
    """Advanced ingredient matching with fuzzy logic and scoring"""

    def __init__(self):
        # Common ingredient variations and synonyms
        self.ingredient_synonyms = {
            'tomato': ['tomatoes', 'tomato paste', 'cherry tomatoes', 'roma tomatoes'],
            'onion': ['onions', 'red onion', 'white onion', 'yellow onion', 'shallots'],
            'garlic': ['garlic cloves', 'garlic clove', 'minced garlic'],
            'chicken': ['chicken breast', 'chicken thighs', 'chicken meat', 'chicken pieces'],
            'beef': ['ground beef', 'beef chunks', 'beef strips', 'steak'],
            'potato': ['potatoes', 'sweet potato', 'sweet potatoes'],
            'carrot': ['carrots', 'baby carrots'],
            'bell pepper': ['bell peppers', 'red pepper', 'green pepper', 'capsicum'],
            'cheese': ['cheddar', 'mozzarella', 'parmesan', 'feta'],
            'milk': ['whole milk', 'skim milk', '2% milk'],
            'flour': ['all-purpose flour', 'wheat flour', 'bread flour'],
            'rice': ['white rice', 'brown rice', 'basmati rice', 'jasmine rice'],
            'pasta': ['spaghetti', 'penne', 'macaroni', 'fusilli'],
            'egg': ['eggs', 'egg whites', 'egg yolks'],
            'butter': ['unsalted butter', 'salted butter', 'margarine'],
            'oil': ['olive oil', 'vegetable oil', 'canola oil', 'cooking oil'],
            'salt': ['sea salt', 'kosher salt', 'table salt'],
            'pepper': ['black pepper', 'white pepper'],
            'sugar': ['white sugar', 'brown sugar', 'powdered sugar'],
            'bread': ['white bread', 'whole wheat bread', 'sourdough'],
            'lettuce': ['iceberg lettuce', 'romaine lettuce', 'leaf lettuce'],
            'spinach': ['baby spinach', 'fresh spinach'],
            'broccoli': ['broccoli florets', 'broccoli crowns'],
            'mushroom': ['mushrooms', 'button mushrooms', 'portobello mushrooms'],
            'fish': ['salmon', 'tuna', 'cod', 'tilapia'],
            'shrimp': ['prawns', 'large shrimp', 'small shrimp'],
            'tofu': ['firm tofu', 'soft tofu', 'silken tofu'],
            'bean': ['beans', 'black beans', 'kidney beans', 'pinto beans'],
            'lentil': ['red lentils', 'green lentils', 'brown lentils'],
            'pea': ['peas', 'green peas', 'split peas'],
            'corn': ['corn kernels', 'sweet corn', 'corn on the cob'],
            'apple': ['apples', 'granny smith apples', 'red apples'],
            'banana': ['bananas', 'ripe bananas'],
            'orange': ['oranges', 'navel oranges'],
            'lemon': ['lemons', 'lemon juice'],
            'lime': ['limes', 'lime juice'],
            'strawberry': ['strawberries', 'fresh strawberries'],
            'blueberry': ['blueberries', 'fresh blueberries'],
            'chocolate': ['dark chocolate', 'milk chocolate', 'chocolate chips'],
            'vanilla': ['vanilla extract', 'vanilla essence'],
            'cinnamon': ['ground cinnamon', 'cinnamon sticks'],
            'cumin': ['ground cumin', 'cumin seeds'],
            'paprika': ['sweet paprika', 'smoked paprika'],
            'oregano': ['dried oregano', 'fresh oregano'],
            'basil': ['fresh basil', 'dried basil'],
            'thyme': ['fresh thyme', 'dried thyme'],
            'rosemary': ['fresh rosemary', 'dried rosemary'],
            'parsley': ['fresh parsley', 'dried parsley'],
            'cilantro': ['fresh cilantro', 'coriander'],
            'ginger': ['fresh ginger', 'ground ginger', 'ginger root'],
            'soy sauce': ['light soy sauce', 'dark soy sauce', 'low sodium soy sauce'],
            'vinegar': ['white vinegar', 'apple cider vinegar', 'rice vinegar'],
            'honey': ['raw honey', 'pure honey'],
            'maple syrup': ['pure maple syrup', 'maple syrup'],
            'mustard': ['dijon mustard', 'yellow mustard', 'whole grain mustard'],
            'mayonnaise': ['mayo', 'light mayonnaise'],
            'ketchup': ['tomato ketchup', 'catsup'],
            'hot sauce': ['tabasco', 'sriracha', 'cholula'],
            'worcestershire sauce': ['worcestershire', 'worcester sauce']
        }

        # Build reverse mapping for faster lookup
        self.synonym_map = {}
        for canonical, variations in self.ingredient_synonyms.items():
            for variation in variations:
                self.synonym_map[variation.lower()] = canonical.lower()
            self.synonym_map[canonical.lower()] = canonical.lower()

    def normalize_ingredient(self, ingredient_name):
        """Normalize ingredient name for better matching"""
        if not ingredient_name:
            return ""

        # Convert to lowercase and strip whitespace
        normalized = ingredient_name.lower().strip()

        # Remove common descriptors that don't affect matching
        descriptors_to_remove = [
            'fresh', 'dried', 'ground', 'chopped', 'minced', 'sliced', 'diced',
            'grated', 'shredded', 'crushed', 'whole', 'large', 'medium', 'small',
            'extra large', 'baby', 'ripe', 'raw', 'cooked', 'frozen', 'canned',
            'low sodium', 'reduced fat', 'fat free', 'organic', 'wild caught'
        ]

        for descriptor in descriptors_to_remove:
            normalized = re.sub(r'\b' + descriptor + r'\b', '', normalized)

        # Remove quantities and units
        normalized = re.sub(r'\d+\s*(cup|cups|tbsp|tsp|oz|lb|lbs|g|kg|ml|l|quart|liter)s?\b', '', normalized)

        # Clean up extra spaces
        normalized = ' '.join(normalized.split())

        # Check if this is a synonym and map to canonical form
        if normalized in self.synonym_map:
            return self.synonym_map[normalized]

        return normalized

    def calculate_similarity(self, ingredient1, ingredient2):
        """Calculate similarity between two ingredient names"""
        # Normalize both ingredients
        norm1 = self.normalize_ingredient(ingredient1)
        norm2 = self.normalize_ingredient(ingredient2)

        if norm1 == norm2:
            return 1.0

        # Check if one is a synonym of the other
        if norm1 in self.synonym_map and self.synonym_map[norm1] == norm2:
            return 0.95
        if norm2 in self.synonym_map and self.synonym_map[norm2] == norm1:
            return 0.95

        # Use sequence matcher for fuzzy matching
        similarity = SequenceMatcher(None, norm1, norm2).ratio()

        # Boost similarity if one ingredient contains the other
        if norm1 in norm2 or norm2 in norm1:
            similarity = max(similarity, 0.8)

        # Check for partial matches (e.g., "chicken breast" and "chicken")
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        word_overlap = len(words1.intersection(words2)) / max(len(words1), len(words2)) if words1 or words2 else 0

        return max(similarity, word_overlap)

    def match_ingredients(self, user_ingredients, recipe_ingredients, threshold=0.6):
        """Match user ingredients against recipe ingredients"""
        matches = []
        matched_user_ingredients = set()
        matched_recipe_ingredients = set()

        # Create normalized versions
        user_norm = [(i, self.normalize_ingredient(i)) for i in user_ingredients]
        recipe_norm = [(i, self.normalize_ingredient(i)) for i in recipe_ingredients]

        # Find best matches
        for user_ing, user_norm_name in user_norm:
            best_match = None
            best_score = 0

            for recipe_ing, recipe_norm_name in recipe_norm:
                if recipe_ing in matched_recipe_ingredients:
                    continue

                score = self.calculate_similarity(user_ing, recipe_ing)

                if score >= threshold and score > best_score:
                    best_match = recipe_ing
                    best_score = score

            if best_match:
                matches.append({
                    'user_ingredient': user_ing,
                    'recipe_ingredient': best_match,
                    'similarity_score': best_score
                })
                matched_user_ingredients.add(user_ing)
                matched_recipe_ingredients.add(best_match)

        return matches

    def calculate_match_percentage(self, user_ingredients, recipe_ingredients, matches=None):
        """Calculate overall match percentage for a recipe"""
        if matches is None:
            matches = self.match_ingredients(user_ingredients, recipe_ingredients)

        if not user_ingredients:
            return 0.0

        # Count matched ingredients
        matched_count = len(matches)

        # Calculate weighted score based on similarity
        total_score = sum(match['similarity_score'] for match in matches)

        # Base percentage on number of matches
        match_percentage = (matched_count / len(user_ingredients)) * 100

        # Boost score for high similarity matches
        similarity_bonus = (total_score / len(user_ingredients)) * 20  # Up to 20% bonus

        final_score = min(match_percentage + similarity_bonus, 100.0)

        return {
            'match_percentage': round(final_score, 2),
            'matched_ingredients': matched_count,
            'total_user_ingredients': len(user_ingredients),
            'matches': matches
        }

    def find_matching_recipes(self, user_ingredients, limit=10, min_match_percentage=20):
        """Find recipes that match user ingredients"""
        try:
            recipes = Recipe.query.all()
            recipe_matches = []

            for recipe in recipes:
                # Get recipe ingredients
                recipe_ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()
                recipe_ingredient_names = [ing.name for ing in recipe_ingredients]

                # Calculate match
                match_result = self.calculate_match_percentage(
                    user_ingredients,
                    recipe_ingredient_names
                )

                if match_result['match_percentage'] >= min_match_percentage:
                    recipe_matches.append({
                        'recipe': recipe,
                        'match_percentage': match_result['match_percentage'],
                        'matched_ingredients': match_result['matched_ingredients'],
                        'matches': match_result['matches']
                    })

            # Sort by match percentage (highest first)
            recipe_matches.sort(key=lambda x: x['match_percentage'], reverse=True)

            return recipe_matches[:limit]

        except Exception as e:
            print(f"Error finding matching recipes: {e}")
            return []

    def get_ingredient_suggestions(self, partial_ingredient, limit=5):
        """Suggest ingredient completions based on partial input"""
        partial_norm = self.normalize_ingredient(partial_ingredient)

        suggestions = []
        seen = set()

        # Check direct matches in synonyms
        for canonical, variations in self.ingredient_synonyms.items():
            if partial_norm in canonical.lower() and canonical not in seen:
                suggestions.append(canonical)
                seen.add(canonical)
            for variation in variations:
                if partial_norm in variation.lower() and variation not in seen:
                    suggestions.append(variation)
                    seen.add(variation)

        # Limit suggestions
        return suggestions[:limit]

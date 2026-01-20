#!/usr/bin/env python3
"""
Test script for the recommendation engine and ingredient matcher
"""

from ingredient_matcher import IngredientMatcher
from recommendation_engine import HybridRecommender
from database_models import init_db, db, Recipe, Ingredient
from config import DATABASE_URL

# Initialize database
from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

def test_ingredient_matcher():
    """Test the ingredient matcher functionality"""
    print("=" * 50)
    print("TESTING INGREDIENT MATCHER")
    print("=" * 50)

    with app.app_context():
        matcher = IngredientMatcher()
        user_ingredients = ['chicken', 'onion', 'garlic', 'tomato']
        recipes = Recipe.query.limit(10).all()

        print(f"Testing with user ingredients: {user_ingredients}")
        print()

        for recipe in recipes:
            recipe_ingredients = [ing.name for ing in Ingredient.query.filter_by(recipe_id=recipe.id).all()]
            match_result = matcher.calculate_match_percentage(user_ingredients, recipe_ingredients)

            if match_result['match_percentage'] > 0:
                print(f"Recipe: {recipe.title}")
                print(f"  Match: {match_result['match_percentage']}%")
                print(f"  Matched ingredients: {len(match_result['matches'])}")
                if match_result['matches']:
                    print("  Matches:")
                    for match in match_result['matches'][:3]:  # Show first 3 matches
                        print(f"    {match['user_ingredient']} -> {match['recipe_ingredient']} ({match['similarity_score']:.2f})")
                print()

def test_recommendation_engine():
    """Test the recommendation engine"""
    print("=" * 50)
    print("TESTING RECOMMENDATION ENGINE")
    print("=" * 50)

    with app.app_context():
        user_ingredients = ['chicken', 'onion', 'garlic', 'tomato']
        user_preferences = {'dietary_preferences': ['gluten-free']}

        print(f"Testing recommendations for ingredients: {user_ingredients}")
        print(f"User preferences: {user_preferences}")
        print()

        # Initialize and fit the recommender
        recommender = HybridRecommender()
        recipes = Recipe.query.all()
        recommender.fit(recipes)

        # Test content-based recommendations
        print("CONTENT-BASED RECOMMENDATIONS:")
        content_recs = recommender.recommend(
            user_ingredients=user_ingredients,
            user_preferences=user_preferences,
            top_n=5
        )

        for i, rec in enumerate(content_recs, 1):
            recipe = rec['recipe']
            print(f"{i}. {recipe.title}")
            print(f"   Score: {rec['score']:.2f}")
            print(f"   Cuisine: {recipe.cuisine_type or 'Not specified'}")
            print(f"   Difficulty: {recipe.difficulty_level or 'Not specified'}")
            if rec['method'] == 'content_based':
                details = rec['details']
                print(f"   Ingredient match: {details['match_percentage']}%")
                print(f"   Similarity score: {details['similarity_score']:.3f}")
                print(f"   Preference bonus: {details['preference_bonus']}")
            print()

        # Test collaborative filtering for a user
        print("\nCOLLABORATIVE FILTERING RECOMMENDATIONS:")
        from database_models import User
        test_user = User.query.filter_by(username='user_1').first()
        if test_user:
            collab_recs = recommender.recommend(
                user_id=test_user.id,
                top_n=3
            )

            print(f"Recommendations for user '{test_user.username}' (who likes Italian and Indian food):")
            for i, rec in enumerate(collab_recs, 1):
                recipe = rec['recipe']
                print(f"{i}. {recipe.title}")
                print(f"   Score: {rec['score']:.2f}")
                print(f"   Method: {rec['method']}")
                print(f"   Cuisine: {recipe.cuisine_type or 'Not specified'}")
                print()
        else:
            print("No test user found for collaborative filtering test.")

        # Test hybrid recommendations
        print("\nHYBRID RECOMMENDATIONS (content-based + collaborative):")
        if test_user:
            hybrid_recs = recommender.recommend(
                user_id=test_user.id,
                user_ingredients=user_ingredients,
                user_preferences=user_preferences,
                top_n=5
            )

            for i, rec in enumerate(hybrid_recs, 1):
                recipe = rec['recipe']
                print(f"{i}. {recipe.title}")
                print(f"   Score: {rec['score']:.2f}")
                print(f"   Method: {rec['method']}")
                print(f"   Cuisine: {recipe.cuisine_type or 'Not specified'}")
                print()

def test_similarity():
    """Test ingredient similarity"""
    print("=" * 50)
    print("TESTING INGREDIENT SIMILARITY")
    print("=" * 50)

    matcher = IngredientMatcher()

    test_pairs = [
        ('chicken', 'chicken breast'),
        ('onion', 'red onion'),
        ('garlic', 'garlic cloves'),
        ('tomato', 'cherry tomatoes'),
        ('beef', 'ground beef'),
        ('potato', 'sweet potato'),
        ('carrot', 'baby carrots'),
        ('chicken', 'fish'),  # Should have low similarity
        ('onion', 'potato'),  # Should have low similarity
    ]

    print("Ingredient similarity scores:")
    print()

    for ing1, ing2 in test_pairs:
        similarity = matcher.calculate_similarity(ing1, ing2)
        print(f"'{ing1}' vs '{ing2}': {similarity:.3f}")

if __name__ == "__main__":
    try:
        test_similarity()
        test_ingredient_matcher()
        test_recommendation_engine()
        print("=" * 50)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 50)
    except Exception as e:
        print(f"ERROR DURING TESTING: {e}")
        import traceback
        traceback.print_exc()

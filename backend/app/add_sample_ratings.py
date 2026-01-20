#!/usr/bin/env python3
"""
Add sample user ratings for testing collaborative filtering
"""

from database_models import init_db, db, RecipeRating, User, Recipe, create_user
from flask import Flask
from config import DATABASE_URL
import random

# Create Flask app for database operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

def add_sample_ratings():
    """Add sample ratings for collaborative filtering testing"""
    print("Adding sample user ratings...")

    with app.app_context():
        # Create some sample users
        users = []
        for i in range(1, 6):  # Users 1-5
            username = f"user_{i}"
            email = f"user{i}@example.com"
            user = db.session.query(User).filter_by(username=username).first()
            if not user:
                user = create_user(username, email)
            users.append(user)

        # Get all recipes
        recipes = Recipe.query.all()

        if not recipes:
            print("No recipes found. Please populate the database first.")
            return

        # Create ratings (simulating user behavior)
        ratings_data = [
            # User 1: Likes Italian and Indian food
            {"user_id": users[0].id, "recipe_ids": [1, 2, 3, 4], "ratings": [5, 4, 5, 3]},
            # User 2: Prefers Mexican and American
            {"user_id": users[1].id, "recipe_ids": [5, 6, 7, 8], "ratings": [4, 5, 4, 3]},
            # User 3: Vegetarian preferences
            {"user_id": users[2].id, "recipe_ids": [9, 10, 11, 12], "ratings": [5, 4, 3, 5]},
            # User 4: Likes quick meals
            {"user_id": users[3].id, "recipe_ids": [13, 14, 15], "ratings": [4, 5, 4]},
            # User 5: Mixed preferences
            {"user_id": users[4].id, "recipe_ids": [1, 5, 9, 13], "ratings": [3, 4, 5, 4]},
        ]

        total_ratings = 0
        for user_data in ratings_data:
            user_id = user_data["user_id"]
            recipe_ids = user_data["recipe_ids"]
            ratings = user_data["ratings"]

            for i, recipe_id in enumerate(recipe_ids):
                if recipe_id <= len(recipes):
                    recipe = recipes[recipe_id - 1]  # 0-indexed

                    # Check if rating already exists
                    existing = RecipeRating.query.filter_by(
                        user_id=user_id, recipe_id=recipe.id
                    ).first()

                    if not existing:
                        rating_value = ratings[i] if i < len(ratings) else random.randint(3, 5)
                        new_rating = RecipeRating(
                            user_id=user_id,
                            recipe_id=recipe.id,
                            rating=rating_value,
                            review=f"Sample rating {rating_value}/5 for {recipe.title}"
                        )
                        db.session.add(new_rating)
                        total_ratings += 1

        # Add some random ratings to create more data
        for _ in range(20):
            user = random.choice(users)
            recipe = random.choice(recipes)
            rating_value = random.randint(1, 5)

            # Check if rating already exists
            existing = RecipeRating.query.filter_by(
                user_id=user.id, recipe_id=recipe.id
            ).first()

            if not existing:
                new_rating = RecipeRating(
                    user_id=user.id,
                    recipe_id=recipe.id,
                    rating=rating_value,
                    review=f"Random rating {rating_value}/5"
                )
                db.session.add(new_rating)
                total_ratings += 1

        db.session.commit()

        print(f"Successfully added {total_ratings} sample ratings!")
        print(f"Total ratings in database: {RecipeRating.query.count()}")

        # Show rating statistics
        ratings = RecipeRating.query.all()
        if ratings:
            avg_rating = sum(r.rating for r in ratings) / len(ratings)
            print(".1f")
            print(f"Rating distribution: {dict((i, sum(1 for r in ratings if r.rating == i)) for i in range(1, 6))}")

if __name__ == "__main__":
    add_sample_ratings()

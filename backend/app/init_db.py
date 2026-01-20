#!/usr/bin/env python3
"""
Database initialization script for the Intelligent Recipe Generator.
This script creates all database tables and can be used to set up the database.
"""

from flask import Flask
from config import DATABASE_URL
from database_models import init_db, db, create_user, create_recipe, add_ingredient, add_instruction, add_nutrition

# Create a separate app instance for database initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def init_database():
    """Initialize the database and create tables"""
    print("Initializing database...")

    with app.app_context():
        # Initialize database with app
        init_db(app)

        print("Database tables created successfully!")

        # Optional: Create some sample data for testing
        # For automated setup, always create sample data
        create_sample_recipes()

    print("Database initialization complete!")

def create_sample_recipes():
    """Create some sample recipes for testing"""
    print("Creating sample data...")

    # Always create a fresh user for sample data
    try:
        from database_models import User
        user = User.query.filter_by(email="test@example.com").first()
        if not user:
            # Create user with minimal required fields
            user = User(
                username="testuser",
                email="test@example.com"
            )
            db.session.add(user)
            db.session.commit()
            print(f"Created user: {user.username}")
        else:
            print(f"Using existing user: {user.username}")
    except Exception as e:
        print(f"Note: User creation skipped due to schema differences: {e}")
        # Skip user creation and just create a dummy user ID for recipes
        return

    # Create a sample recipe
    recipe = create_recipe(
        user_id=user.id,
        title="Simple Tomato Pasta",
        description="A quick and easy pasta dish with fresh tomatoes",
        prep_time=10,
        cook_time=15,
        servings=4,
        cuisine_type="italian",
        difficulty_level="easy",
        dietary_preferences='["vegetarian"]',
        total_time=25,
        source="user"
    )
    print(f"Created recipe: {recipe.title}")

    # Add ingredients
    ingredients = [
        ("pasta", 300, "grams"),
        ("tomatoes", 4, "pieces", "diced"),
        ("garlic", 2, "cloves", "minced"),
        ("olive oil", 2, "tablespoons"),
        ("salt", 1, "teaspoon"),
        ("basil", None, None, "fresh, chopped")
    ]

    for ing in ingredients:
        add_ingredient(recipe.id, *ing)

    # Add instructions
    instructions = [
        "Bring a large pot of salted water to boil. Cook pasta according to package directions.",
        "While pasta cooks, heat olive oil in a large skillet over medium heat.",
        "Add minced garlic and cook for 1 minute until fragrant.",
        "Add diced tomatoes and cook for 5-7 minutes until they start to soften.",
        "Season with salt and add fresh basil.",
        "Drain pasta and add to the skillet. Toss everything together.",
        "Serve hot with grated cheese if desired."
    ]

    for i, desc in enumerate(instructions, 1):
        add_instruction(recipe.id, i, desc)

    # Add nutrition info (approximate)
    add_nutrition(
        recipe_id=recipe.id,
        calories=350,
        protein=12,
        carbohydrates=60,
        fat=8,
        fiber=4,
        sugar=6,
        sodium=400
    )

    print("Sample data created successfully!")

if __name__ == "__main__":
    init_database()

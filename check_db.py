#!/usr/bin/env python3
"""Quick script to check current database state"""

import sys
import os
sys.path.append('backend')

from app.database_models import init_db, db
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///intelligent_recipe.db'
init_db(app)

with app.app_context():
    from app.database_models import Recipe, User, Ingredient
    recipe_count = Recipe.query.count()
    user_count = User.query.count()

    print(f"Current recipes in database: {recipe_count}")
    print(f"Current users in database: {user_count}")

    if recipe_count > 0:
        # Show a few example recipes
        recipes = Recipe.query.limit(3).all()
        print("\nSample recipes:")
        for recipe in recipes:
            ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).count()
            print(f"- {recipe.title} ({recipe.cuisine_type}) - {ingredients} ingredients")

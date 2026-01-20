#!/usr/bin/env python3
"""
Check database status
"""

from flask import Flask
from config import DATABASE_URL
from database_models import db, Recipe, Ingredient, Instruction, Nutrition

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print(f"Recipes: {Recipe.query.count()}")
    print(f"Ingredients: {Ingredient.query.count()}")
    print(f"Instructions: {Instruction.query.count()}")
    print(f"Nutrition: {Nutrition.query.count()}")

    # Show some sample recipes
    recipes = Recipe.query.limit(3).all()
    if recipes:
        print("\nSample recipes:")
        for recipe in recipes:
            print(f"- {recipe.title}")
    else:
        print("No recipes found!")

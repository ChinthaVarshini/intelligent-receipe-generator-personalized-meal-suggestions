#!/usr/bin/env python3

import sys
import os
sys.path.append('backend/app')

from database_models import Recipe, init_db
from config import DATABASE_URL
from flask import Flask

# Create Flask app for database context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

with app.app_context():
    recipes = Recipe.query.all()
    print("Recipe Names:")
    print("=" * 50)
    for recipe in recipes:
        print(f"- {recipe.title}")
    print(f"\nTotal recipes: {len(recipes)}")

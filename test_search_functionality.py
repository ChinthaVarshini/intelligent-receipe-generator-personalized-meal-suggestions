#!/usr/bin/env python3
"""Test search functionality on collected recipes"""

import sys
import os
sys.path.append('backend')

from app.database_models import init_db, db
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///intelligent_recipe.db'
init_db(app)

with app.app_context():
    from app.database_models import Recipe, Ingredient, Instruction, Nutrition

    print("🔍 Testing Search Functionality")
    print("=" * 40)

    # Test 1: Search by cuisine
    print("\n📊 Recipes by cuisine:")
    cuisines = db.session.execute(db.text("SELECT cuisine_type, COUNT(*) as count FROM recipes GROUP BY cuisine_type ORDER BY count DESC")).fetchall()
    for cuisine, count in cuisines:
        print(f"  {cuisine}: {count} recipes")

    # Test 2: Search by source
    print("\n📊 Recipes by source:")
    sources = db.session.execute(db.text("SELECT source, COUNT(*) as count FROM recipes GROUP BY source ORDER BY count DESC")).fetchall()
    for source, count in sources:
        print(f"  {source}: {count} recipes")

    # Test 3: Sample recipes with full details
    print("\n📋 Sample recipe details:")
    recipes = Recipe.query.limit(2).all()
    for recipe in recipes:
        print(f"\n🍳 {recipe.title}")
        print(f"   Cuisine: {recipe.cuisine_type}")
        print(f"   Difficulty: {recipe.difficulty_level}")
        print(f"   Prep time: {recipe.prep_time} min")
        print(f"   Cook time: {recipe.cook_time} min")
        print(f"   Servings: {recipe.servings}")
        print(f"   Source: {recipe.source}")

        # Ingredients
        ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()
        print(f"   Ingredients ({len(ingredients)}):")
        for ing in ingredients[:3]:  # Show first 3
            print(f"     - {ing.name} ({ing.quantity} {ing.unit})")
        if len(ingredients) > 3:
            print(f"     ... and {len(ingredients) - 3} more")

        # Instructions
        instructions = Instruction.query.filter_by(recipe_id=recipe.id).all()
        print(f"   Instructions ({len(instructions)} steps):")
        for instr in instructions[:2]:  # Show first 2
            desc = instr.description[:50] + "..." if len(instr.description) > 50 else instr.description
            print(f"     {instr.step_number}. {desc}")
        if len(instructions) > 2:
            print(f"     ... and {len(instructions) - 2} more steps")

        # Nutrition
        nutrition = Nutrition.query.filter_by(recipe_id=recipe.id).first()
        if nutrition:
            print(f"   Nutrition: {nutrition.calories} cal, {nutrition.protein}g protein")

        print("\n✅ Search functionality test complete!")

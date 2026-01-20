from backend.app.database_models import init_db, db, Recipe, Nutrition, get_recipe_with_details
from backend.app.config import DATABASE_URL
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

with app.app_context():
    print('Total recipes:', Recipe.query.count())
    print('Recipes with nutrition:', Nutrition.query.count())

    recipes = Recipe.query.limit(3).all()
    for r in recipes:
        full_recipe = get_recipe_with_details(r.id)
        nutrition = full_recipe.nutrition_info
        print(f'{r.title}: {nutrition.calories if nutrition else None} cal, protein: {nutrition.protein if nutrition else None}g')

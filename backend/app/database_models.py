from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    profile_image = db.Column(db.String(500))
    oauth_provider = db.Column(db.String(20))  # 'google', 'facebook', or None for local auth
    oauth_id = db.Column(db.String(100))  # OAuth provider's user ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipes = db.relationship('Recipe', backref='user', lazy=True)
    preferences = db.relationship('UserPreference', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    cooking_history = db.relationship('CookingHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    dietary_preferences = db.relationship('UserDietaryPreference', backref='user', lazy=True, cascade='all, delete-orphan')

    # Indexes
    __table_args__ = (
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_username', 'username'),
    )

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    preference_key = db.Column(db.String(100), nullable=False)
    preference_value = db.Column(db.Text, nullable=False)  # Can store JSON strings

    # Indexes
    __table_args__ = (
        db.Index('idx_user_pref_user_key', 'user_id', 'preference_key'),
    )

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    prep_time = db.Column(db.Integer)  # in minutes
    cook_time = db.Column(db.Integer)  # in minutes
    servings = db.Column(db.Integer)

    # New fields for recommendation engine
    cuisine_type = db.Column(db.String(50))  # e.g., 'italian', 'indian', 'chinese', 'mexican'
    difficulty_level = db.Column(db.String(20))  # 'easy', 'medium', 'hard'
    dietary_preferences = db.Column(db.Text)  # JSON string: ['vegetarian', 'vegan', 'gluten-free', 'dairy-free']
    total_time = db.Column(db.Integer)  # prep_time + cook_time
    source = db.Column(db.String(50))  # 'user', 'spoonacular', 'edamam', 'themealdb'
    source_id = db.Column(db.String(100))  # ID from external API
    image_url = db.Column(db.Text)  # URL to recipe image

    # Relationships
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True, cascade='all, delete-orphan')
    instructions = db.relationship('Instruction', backref='recipe', lazy=True, cascade='all, delete-orphan')
    nutrition = db.relationship('Nutrition', backref='recipe', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('RecipeRating', backref='recipe', lazy=True, cascade='all, delete-orphan')

    # Indexes
    __table_args__ = (
        db.Index('idx_recipe_user_id', 'user_id'),
        db.Index('idx_recipe_title', 'title'),
        db.Index('idx_recipe_created_at', 'created_at'),
        db.Index('idx_recipe_cuisine', 'cuisine_type'),
        db.Index('idx_recipe_difficulty', 'difficulty_level'),
        db.Index('idx_recipe_total_time', 'total_time'),
        db.Index('idx_recipe_source', 'source'),
    )

class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(50))  # e.g., 'cups', 'grams', 'pieces'
    notes = db.Column(db.Text)  # e.g., 'chopped', 'diced'

    # Indexes
    __table_args__ = (
        db.Index('idx_ingredient_recipe_id', 'recipe_id'),
        db.Index('idx_ingredient_name', 'name'),
    )

class Instruction(db.Model):
    __tablename__ = 'instructions'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Indexes
    __table_args__ = (
        db.Index('idx_instruction_recipe_id', 'recipe_id'),
        db.Index('idx_instruction_step', 'recipe_id', 'step_number'),
    )

class Nutrition(db.Model):
    __tablename__ = 'nutrition'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    calories = db.Column(db.Integer)
    protein = db.Column(db.Float)  # in grams
    carbohydrates = db.Column(db.Float)  # in grams
    fat = db.Column(db.Float)  # in grams
    fiber = db.Column(db.Float)  # in grams
    sugar = db.Column(db.Float)  # in grams
    sodium = db.Column(db.Float)  # in mg

    # Indexes
    __table_args__ = (
        db.Index('idx_nutrition_recipe_id', 'recipe_id'),
    )

class RecipeRating(db.Model):
    __tablename__ = 'recipe_ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)  # Optional review text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure one rating per user per recipe
    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_rating'),
        db.Index('idx_rating_user_id', 'user_id'),
        db.Index('idx_rating_recipe_id', 'recipe_id'),
        db.Index('idx_rating_rating', 'rating'),
    )

class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure one favorite per user per recipe
    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_favorite'),
        db.Index('idx_favorite_user_id', 'user_id'),
        db.Index('idx_favorite_recipe_id', 'recipe_id'),
    )

class CookingHistory(db.Model):
    __tablename__ = 'cooking_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    cooked_at = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer)  # Optional rating after cooking
    notes = db.Column(db.Text)  # User notes about the cooking experience

    # Indexes
    __table_args__ = (
        db.Index('idx_history_user_id', 'user_id'),
        db.Index('idx_history_recipe_id', 'recipe_id'),
        db.Index('idx_history_cooked_at', 'cooked_at'),
    )

class UserDietaryPreference(db.Model):
    __tablename__ = 'user_dietary_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    preference = db.Column(db.String(100), nullable=False)  # e.g., 'vegetarian', 'vegan', 'gluten-free'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure one preference per user per type
    __table_args__ = (
        db.UniqueConstraint('user_id', 'preference', name='unique_user_dietary_preference'),
        db.Index('idx_dietary_user_id', 'user_id'),
        db.Index('idx_dietary_preference', 'preference'),
    )

# Database initialization functions
def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)

    with app.app_context():
        db.create_all()

def get_db():
    """Get database instance"""
    return db

# Helper functions for data manipulation
def create_user(username, email):
    """Create a new user"""
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user

def create_recipe(user_id, title, description=None, prep_time=None, cook_time=None, servings=None,
                 cuisine_type=None, difficulty_level=None, dietary_preferences=None, total_time=None,
                 source=None, source_id=None, image_url=None):
    """Create a new recipe"""
    recipe = Recipe(
        user_id=user_id,
        title=title,
        description=description,
        prep_time=prep_time,
        cook_time=cook_time,
        servings=servings,
        cuisine_type=cuisine_type,
        difficulty_level=difficulty_level,
        dietary_preferences=dietary_preferences,
        total_time=total_time,
        source=source,
        source_id=source_id,
        image_url=image_url
    )
    db.session.add(recipe)
    db.session.commit()
    return recipe

def add_ingredient(recipe_id, name, quantity=None, unit=None, notes=None):
    """Add an ingredient to a recipe"""
    ingredient = Ingredient(
        recipe_id=recipe_id,
        name=name,
        quantity=quantity,
        unit=unit,
        notes=notes
    )
    db.session.add(ingredient)
    db.session.commit()
    return ingredient

def add_instruction(recipe_id, step_number, description):
    """Add an instruction step to a recipe"""
    instruction = Instruction(
        recipe_id=recipe_id,
        step_number=step_number,
        description=description
    )
    db.session.add(instruction)
    db.session.commit()
    return instruction

def add_nutrition(recipe_id, calories=None, protein=None, carbohydrates=None, fat=None,
                 fiber=None, sugar=None, sodium=None):
    """Add nutritional information to a recipe"""
    nutrition = Nutrition(
        recipe_id=recipe_id,
        calories=calories,
        protein=protein,
        carbohydrates=carbohydrates,
        fat=fat,
        fiber=fiber,
        sugar=sugar,
        sodium=sodium
    )
    db.session.add(nutrition)
    db.session.commit()
    return nutrition

def set_user_preference(user_id, key, value):
    """Set a user preference"""
    # Check if preference already exists
    pref = UserPreference.query.filter_by(user_id=user_id, preference_key=key).first()
    if pref:
        pref.preference_value = value
    else:
        pref = UserPreference(user_id=user_id, preference_key=key, preference_value=value)
        db.session.add(pref)
    db.session.commit()
    return pref

def get_user_preferences(user_id):
    """Get all preferences for a user"""
    prefs = UserPreference.query.filter_by(user_id=user_id).all()
    return {pref.preference_key: pref.preference_value for pref in prefs}

# Query functions
def get_recipes_by_user(user_id):
    """Get all recipes for a user"""
    return Recipe.query.filter_by(user_id=user_id).order_by(Recipe.created_at.desc()).all()

def search_recipes(query):
    """Search recipes by title"""
    return Recipe.query.filter(Recipe.title.ilike(f'%{query}%')).all()

def get_recipe_with_details(recipe_id):
    """Get a recipe with all its ingredients, instructions, and nutrition"""
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        recipe.ingredients_list = Ingredient.query.filter_by(recipe_id=recipe_id).order_by(Ingredient.id).all()
        recipe.instructions_list = Instruction.query.filter_by(recipe_id=recipe_id).order_by(Instruction.step_number).all()
        recipe.nutrition_info = Nutrition.query.filter_by(recipe_id=recipe_id).first()
    return recipe

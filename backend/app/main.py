from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
from PIL import Image
import io
import os
import jwt
import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from authlib.integrations.flask_client import OAuth

# Delay importing heavy ML modules until they're needed in route handlers.
preprocess_image = None
get_predictions = None
extract_text = None
from config import (
    API_KEY, REQUIRED_API_KEY, DATABASE_URL, JWT_SECRET_KEY,
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
    FRONTEND_URL
)
from recipe_generator import generate_multiple_recipes, generate_cooking_instructions, enhance_recipe_with_nlp_instructions
from beautiful_recipe_generator import generate_beautiful_recipe
from database_models import (
    init_db, db, User, UserPreference, Recipe, Ingredient, Instruction, Nutrition,
    RecipeRating, Favorite, CookingHistory, get_recipe_with_details, create_user, set_user_preference, get_user_preferences
)
from ingredient_matcher import IngredientMatcher
from recommendation_engine import HybridRecommender

app = Flask(__name__,
            static_folder='../../frontend/build',
            static_url_path='/')
CORS(app, origins=['http://localhost:8000', 'http://127.0.0.1:8000', 'http://localhost:3000', 'http://127.0.0.1:3000'])

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Image upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'recipes')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# OAuth configuration
oauth = OAuth(app)

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    google = oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

if FACEBOOK_APP_ID and FACEBOOK_APP_SECRET:
    facebook = oauth.register(
        name='facebook',
        client_id=FACEBOOK_APP_ID,
        client_secret=FACEBOOK_APP_SECRET,
        access_token_url='https://graph.facebook.com/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={
            'scope': 'email public_profile'
        }
    )

# Initialize database
init_db(app)

def require_api_key(f):
    """Decorator to require API key authentication"""
    def decorated_function(*args, **kwargs):
        if REQUIRED_API_KEY:
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            if not api_key or api_key != API_KEY:
                return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def token_required(f):
    """Decorator to require JWT token authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_recipe_image(file, recipe_id):
    """Save uploaded recipe image and return the URL"""
    if not file or not allowed_file(file.filename):
        return None

    # Generate unique filename
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"recipe_{recipe_id}_{uuid.uuid4().hex}.{file_extension}"

    # Save file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)

    # Return URL path (relative to static folder)
    return f"/uploads/recipes/{unique_filename}"

@app.route("/upload-recipe-image/<int:recipe_id>", methods=["POST"])
@token_required
def upload_recipe_image(current_user, recipe_id):
    """Upload image for a specific recipe"""
    try:
        # Check if recipe exists and belongs to user
        recipe = Recipe.query.filter_by(id=recipe_id, user_id=current_user.id).first()
        if not recipe:
            return jsonify({"error": "Recipe not found or access denied"}), 404

        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No image selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed. Use: PNG, JPG, JPEG, GIF, WebP"}), 400

        # Save the image
        image_url = save_recipe_image(file, recipe_id)
        if not image_url:
            return jsonify({"error": "Failed to save image"}), 500

        # Update recipe with image URL
        recipe.image_url = image_url
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Recipe image uploaded successfully",
            "image_url": image_url
        })

    except Exception as e:
        db.session.rollback()
        print(f"Image upload error: {e}")
        return jsonify({"error": "Failed to upload image"}), 500

@app.route("/uploads/recipes/<filename>")
def get_recipe_image(filename):
    """Serve recipe images"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Image serving error: {e}")
        return jsonify({"error": "Image not found"}), 404

@app.route("/uploads/ai_images/<filename>")
def get_ai_recipe_image(filename):
    """Serve AI-generated recipe images"""
    try:
        ai_images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'ai_images')
        return send_from_directory(ai_images_dir, filename)
    except Exception as e:
        print(f"AI Image serving error: {e}")
        return jsonify({"error": "AI Image not found"}), 404

@app.route("/process-image", methods=["POST"])
@require_api_key
def process_image_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    img_bytes = file.read()
    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # Import OCR and model code lazily so the server can start without
    # heavy ML dependencies installed. Errors will occur here if the
    # required libraries are missing when this route is invoked.
    global extract_text, get_predictions
    if extract_text is None or get_predictions is None:
        from ocr_utils import extract_text as _extract_text
        from model import get_predictions as _get_predictions
        extract_text = _extract_text
        get_predictions = _get_predictions

    # OCR
    text = extract_text(pil_img)

    # Check if OCR text is gibberish (reading food texture instead of actual text)
    from ocr_utils import is_gibberish_text
    ocr_is_gibberish = is_gibberish_text(text)

    print(f"OCR text quality check: {'GIBBERISH' if ocr_is_gibberish else 'VALID'}")

    # Get predictions with enhanced logic for gibberish OCR
    prediction = get_predictions(pil_img, text)

    # Extract ingredients list
    ingredients_list = prediction.get("ingredients", [])
    ingredients_names = [ing.get("name", "Unknown") for ing in ingredients_list if ing.get("name", "Unknown") != "Unknown"]

    # If no ingredients found, try image classification as fallback
    if not ingredients_names:
        # Look for image classification results in the prediction
        image_classifications = prediction.get("image_classifications", [])
        if image_classifications:
            print(f"No OCR ingredients found, using image classification: {image_classifications}")
            # Convert image classifications to ingredient format
            ingredients_list = [{"name": cls["name"], "confidence": cls["confidence"]}
                              for cls in image_classifications[:5] if cls.get("name")]  # Top 5
            ingredients_names = [ing["name"] for ing in ingredients_list]

    # Filter out "Unknown" entries
    ingredients_names = [ing for ing in ingredients_names if ing and ing.lower() != "unknown"]
    
    print(f"Detected ingredients: {ingredients_names}")
    print(f"OCR Text: {text[:100]}")

    # Generate beautiful recipe from detected ingredients
    generated_recipes = []
    try:
        print("Generating AI recipe suggestions...")

        if len(ingredients_names) > 0:
            # Generate one beautiful recipe using the detected ingredients
            cuisine = "General"  # Could be enhanced to detect cuisine from ingredients

            recipe_result = generate_beautiful_recipe(ingredients_names, cuisine)

            if recipe_result.get("success", False):
                # Format the recipe for the response
                recipe_data = {
                    "id": f"ai_generated_{uuid.uuid4().hex[:8]}",
                    "title": recipe_result.get("structured_recipe", {}).get("name", "AI Generated Recipe"),
                    "description": recipe_result.get("structured_recipe", {}).get("description", "A delicious recipe created from your ingredients"),
                    "source": "ai_generated",
                    "recommendation_score": 0.95,
                    "recommendation_method": "ingredient_detection",
                    "ingredients": recipe_result.get("structured_recipe", {}).get("ingredients", []),
                    "instructions": recipe_result.get("structured_recipe", {}).get("instructions", []),
                    "nutrition": recipe_result.get("structured_recipe", {}).get("nutrition", {}),
                    "prep_time": recipe_result.get("structured_recipe", {}).get("prep_time", 15),
                    "cook_time": recipe_result.get("structured_recipe", {}).get("cook_time", 30),
                    "servings": recipe_result.get("structured_recipe", {}).get("servings", 4),
                    "cuisine_type": recipe_result.get("structured_recipe", {}).get("cuisine_type", "General"),
                    "difficulty_level": recipe_result.get("structured_recipe", {}).get("difficulty", "Medium")
                }
                generated_recipes = [recipe_data]
                print(f"✅ Generated beautiful recipe: {recipe_data['title']}")
            else:
                print(f"⚠️ Recipe generation failed: {recipe_result.get('error', 'Unknown error')}")
        else:
            print("⚠️ No ingredients detected - cannot generate recipe")

    except Exception as e:
        print(f"❌ Error generating recipe: {e}")

    # Also try to find matching recipes from database if available
    database_recipes = []
    try:
        # Try database matching as fallback/secondary option
        recommender = HybridRecommender()
        recipes = Recipe.query.all()
        recommender.fit(recipes)

        db_matches = recommender.recommend(
            user_ingredients=ingredients_names,
            top_n=3  # Limit to 3 database matches
        )

        for rec in db_matches:
            recipe = rec['recipe']
            full_recipe = get_recipe_with_details(recipe.id)
            recipe_ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()

            recipe_data = {
                "id": recipe.id,
                "title": recipe.title,
                "description": recipe.description,
                "source": "database",
                "recommendation_score": round(rec['score'], 2),
                "recommendation_method": rec['method'],
                "ingredients": [
                    {
                        "name": ing.name,
                        "quantity": ing.quantity,
                        "unit": ing.unit,
                        "notes": ing.notes
                    } for ing in recipe_ingredients
                ],
                "instructions": [
                    {
                        "step_number": inst.step_number,
                        "description": inst.description
                    } for inst in full_recipe.instructions_list
                ] if full_recipe.instructions_list else [],
                "nutrition": {
                    "calories": full_recipe.nutrition_info.calories if full_recipe.nutrition_info else None,
                    "protein": full_recipe.nutrition_info.protein if full_recipe.nutrition_info else None,
                    "carbohydrates": full_recipe.nutrition_info.carbohydrates if full_recipe.nutrition_info else None,
                    "fat": full_recipe.nutrition_info.fat if full_recipe.nutrition_info else None,
                } if full_recipe.nutrition_info else None
            }
            database_recipes.append(recipe_data)

    except Exception as e:
        print(f"Database recipe matching skipped: {e}")

    # Combine AI-generated recipes with database matches
    all_recipes = generated_recipes + database_recipes
    total_recipes = len(all_recipes)

    print(f"✅ Image processing completed successfully!")
    print(f"   - OCR Text: {text[:50]}...")
    print(f"   - Detected Ingredients: {ingredients_names}")
    print(f"   - Generated Recipes: {len(generated_recipes)}")
    print(f"   - Database Matches: {len(database_recipes)}")
    print(f"   - Total Recipes: {total_recipes}")

    return jsonify({
        "ocr_text": text,
        "ingredients": ingredients_names,  # List of ingredient names
        "detected_items": ingredients_list,  # List of dicts with name and confidence
        "ai_generated_recipes": generated_recipes,
        "database_matching_recipes": database_recipes,
        "matching_recipes": all_recipes,  # Combined list for backward compatibility
        "total_matching_recipes": total_recipes,
        "message": f"Ingredients detected successfully! Generated {len(generated_recipes)} AI recipes and found {len(database_recipes)} matching recipes from database.",
        "processing_status": "success"
    })

@app.route("/generate-recipe", methods=["POST"])
@require_api_key
def generate_recipe_route():
    """Generate a beautiful, detailed recipe from ingredients using Google Gemini"""
    data = request.get_json()

    if not data or 'ingredients' not in data:
        return jsonify({"error": "No ingredients provided"}), 400

    ingredients = data['ingredients']
    cuisine = data.get('cuisine', 'General')

    if not isinstance(ingredients, list):
        return jsonify({"error": "Ingredients must be a list"}), 400

    # Use the beautiful recipe generator with Google Gemini
    result = generate_beautiful_recipe(ingredients, cuisine)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/generate-recipe-image", methods=["POST"])
@require_api_key
def generate_recipe_image_route():
    """Generate an AI image for a recipe"""
    data = request.get_json()

    if not data or 'recipe_name' not in data:
        return jsonify({"error": "Recipe name is required"}), 400

    recipe_name = data['recipe_name']
    ingredients = data.get('ingredients', [])
    cuisine = data.get('cuisine', 'General')
    style = data.get('style', 'photorealistic')  # photorealistic, artistic, cartoon, etc.

    # Lazy import to avoid startup-time dependency
    from recipe_image_generator import generate_recipe_image

    result = generate_recipe_image(recipe_name, ingredients, cuisine, style)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/generate-recipe-suggestions", methods=["POST"])
@require_api_key
def generate_recipe_suggestions_route():
    """Generate multiple recipe suggestions from ingredients"""
    data = request.get_json()
    
    if not data or 'ingredients' not in data:
        return jsonify({"error": "No ingredients provided"}), 400
    
    ingredients = data['ingredients']
    num_recipes = data.get('num_recipes', 3)
    
    if not isinstance(ingredients, list):
        return jsonify({"error": "Ingredients must be a list"}), 400
    
    # Lazy import of recipe generator to avoid startup-time dependency on OpenAI libs
    from recipe_generator import generate_multiple_recipes

    result = generate_multiple_recipes(ingredients, num_recipes)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route("/generate-instructions", methods=["POST"])
@require_api_key
def generate_instructions_route():
    """Generate simple, beginner-friendly cooking instructions using NLP"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract recipe data from request
    recipe_data = {
        "name": data.get("name") or data.get("title"),
        "ingredients": data.get("ingredients", []),
        "cuisine": data.get("cuisine") or data.get("cuisine_type", "General"),
        "difficulty": data.get("difficulty") or data.get("difficulty_level", "Easy")
    }

    if not recipe_data["name"] or not recipe_data["ingredients"]:
        return jsonify({"error": "Recipe name and ingredients are required"}), 400

    # Generate instructions using NLP
    result = generate_cooking_instructions(recipe_data)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/enhance-recipe-instructions", methods=["POST"])
@require_api_key
def enhance_recipe_instructions_route():
    """Enhance existing recipe data with NLP-generated instructions"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No recipe data provided"}), 400

    # Enhance the recipe with NLP instructions
    enhanced_recipe = enhance_recipe_with_nlp_instructions(data)

    return jsonify({
        "success": True,
        "enhanced_recipe": enhanced_recipe
    })

@app.route("/find-recipes", methods=["POST"])
@require_api_key
def find_recipes_route():
    """Find recipes from database that match detected ingredients using advanced matching"""
    data = request.get_json()

    if not data or 'ingredients' not in data:
        return jsonify({"error": "No ingredients provided"}), 400

    ingredients = data['ingredients']
    if not isinstance(ingredients, list):
        return jsonify({"error": "Ingredients must be a list"}), 400

    user_id = data.get('user_id')  # Optional for collaborative filtering
    preferences = data.get('preferences', {})  # Optional user preferences
    limit = data.get('limit', 10)

    try:
        # Initialize the hybrid recommender
        recommender = HybridRecommender()

        # Fit the models with all recipes
        recipes = Recipe.query.all()
        recommender.fit(recipes)

        # Get recommendations
        recommendations = recommender.recommend(
            user_id=user_id,
            user_ingredients=ingredients,
            user_preferences=preferences,
            top_n=limit
        )

        # Format response
        formatted_recipes = []
        for rec in recommendations:
            recipe = rec['recipe']
            full_recipe = get_recipe_with_details(recipe.id)
            recipe_ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()

            recipe_data = {
                "id": recipe.id,
                "title": recipe.title,
                "description": recipe.description,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "servings": recipe.servings,
                "cuisine_type": recipe.cuisine_type,
                "difficulty_level": recipe.difficulty_level,
                "dietary_preferences": recipe.dietary_preferences,
                "total_time": recipe.total_time,
                "source": recipe.source,
                "image_url": recipe.image_url,
                "ingredients": [
                    {
                        "name": ing.name,
                        "quantity": ing.quantity,
                        "unit": ing.unit,
                        "notes": ing.notes
                    } for ing in recipe_ingredients
                ],
                "instructions": [
                    {
                        "step_number": inst.step_number,
                        "description": inst.description
                    } for inst in full_recipe.instructions_list
                ] if full_recipe.instructions_list else [],
                "nutrition": {
                    "calories": full_recipe.nutrition_info.calories if full_recipe.nutrition_info else None,
                    "protein": full_recipe.nutrition_info.protein if full_recipe.nutrition_info else None,
                    "carbohydrates": full_recipe.nutrition_info.carbohydrates if full_recipe.nutrition_info else None,
                    "fat": full_recipe.nutrition_info.fat if full_recipe.nutrition_info else None,
                    "fiber": full_recipe.nutrition_info.fiber if full_recipe.nutrition_info else None,
                    "sugar": full_recipe.nutrition_info.sugar if full_recipe.nutrition_info else None,
                    "sodium": full_recipe.nutrition_info.sodium if full_recipe.nutrition_info else None,
                } if full_recipe.nutrition_info else None,
                "recommendation_score": round(rec['score'], 2),
                "recommendation_method": rec['method'],
                "recommendation_details": rec['details']
            }

            formatted_recipes.append(recipe_data)

        return jsonify({
            "total_recipes": len(formatted_recipes),
            "recipes": formatted_recipes,
            "detected_ingredients": ingredients
        })

    except Exception as e:
        print(f"Error finding recipes: {e}")
        return jsonify({"error": "Failed to search recipes"}), 500

@app.route("/get-all-recipes", methods=["GET"])
@require_api_key
def get_all_recipes_route():
    """Get all recipes from database"""
    try:
        recipes = Recipe.query.limit(50).all()  # Limit to 50 for performance
        recipe_list = []

        for recipe in recipes:
            full_recipe = get_recipe_with_details(recipe.id)
            recipe_ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()

            recipe_data = {
                "id": recipe.id,
                "title": recipe.title,
                "description": recipe.description,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "servings": recipe.servings,
                "ingredients": [
                    {
                        "name": ing.name,
                        "quantity": ing.quantity,
                        "unit": ing.unit,
                        "notes": ing.notes
                    } for ing in recipe_ingredients
                ],
                "instructions": [
                    {
                        "step_number": inst.step_number,
                        "description": inst.description
                    } for inst in full_recipe.instructions_list
                ] if full_recipe.instructions_list else [],
                "nutrition": {
                    "calories": full_recipe.nutrition_info.calories if full_recipe.nutrition_info else None,
                    "protein": full_recipe.nutrition_info.protein if full_recipe.nutrition_info else None,
                    "carbohydrates": full_recipe.nutrition_info.carbohydrates if full_recipe.nutrition_info else None,
                    "fat": full_recipe.nutrition_info.fat if full_recipe.nutrition_info else None,
                    "fiber": full_recipe.nutrition_info.fiber if full_recipe.nutrition_info else None,
                    "sugar": full_recipe.nutrition_info.sugar if full_recipe.nutrition_info else None,
                    "sodium": full_recipe.nutrition_info.sodium if full_recipe.nutrition_info else None,
                } if full_recipe.nutrition_info else None
            }
            recipe_list.append(recipe_data)

        return jsonify({
            "total_recipes": len(recipe_list),
            "recipes": recipe_list
        })

    except Exception as e:
        print(f"Error getting recipes: {e}")
        return jsonify({"error": "Failed to get recipes"}), 500

@app.route("/database-status", methods=["GET"])
@require_api_key
def database_status_route():
    """Get database statistics"""
    try:
        # Try to get recipe count - this will fail if schema is incomplete
        recipe_count = 0
        ingredient_count = 0
        instruction_count = 0
        nutrition_count = 0
        sample_recipes = []

        try:
            recipe_count = Recipe.query.count()
        except Exception as e:
            print(f"Recipe count failed: {e}")
            recipe_count = 0

        try:
            ingredient_count = Ingredient.query.count()
        except Exception as e:
            print(f"Ingredient count failed: {e}")
            ingredient_count = 0

        try:
            instruction_count = Instruction.query.count()
        except Exception as e:
            print(f"Instruction count failed: {e}")
            instruction_count = 0

        try:
            nutrition_count = Nutrition.query.count()
        except Exception as e:
            print(f"Nutrition count failed: {e}")
            nutrition_count = 0

        try:
            # Get some sample recipe titles
            sample_recipes_query = Recipe.query.limit(5).all()
            sample_recipes = [recipe.title for recipe in sample_recipes_query]
        except Exception as e:
            print(f"Sample recipes query failed: {e}")
            sample_recipes = []

        # Determine database health status
        schema_issues = recipe_count == 0 and len(sample_recipes) == 0
        status = "schema_issues" if schema_issues else "healthy"

        status_data = {
            "total_recipes": recipe_count,
            "total_ingredients": ingredient_count,
            "total_instructions": instruction_count,
            "total_nutrition_entries": nutrition_count,
            "total_users": 0,  # Simplified for now
            "database_url": DATABASE_URL.split('/')[-1] if '/' in DATABASE_URL else DATABASE_URL,
            "status": status,
            "sample_recipes": sample_recipes
        }

        if schema_issues:
            status_data["note"] = "Database schema needs updating. Run init_db.py to fix."
        else:
            status_data["note"] = "Database is healthy and fully functional."

        return jsonify(status_data)

    except Exception as e:
        print(f"Error getting database status: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "total_recipes": 0,
            "total_ingredients": 0,
            "total_instructions": 0,
            "total_nutrition_entries": 0,
            "note": "Database connection or schema error. Check server logs."
        }), 500

@app.route("/search-recipes", methods=["POST"])
@require_api_key
def search_recipes_route():
    """Advanced recipe search and filtering with pagination"""
    data = request.get_json()

    # Extract search parameters
    query = data.get('query', '').strip()
    dietary_preferences = data.get('dietary_preferences', [])  # ['vegetarian', 'vegan', 'gluten-free']
    cuisine_type = data.get('cuisine_type')  # 'italian', 'chinese', etc.
    difficulty_level = data.get('difficulty_level')  # 'easy', 'medium', 'hard'
    max_prep_time = data.get('max_prep_time')  # in minutes
    max_cook_time = data.get('max_cook_time')  # in minutes
    max_total_time = data.get('max_total_time')  # in minutes
    min_servings = data.get('min_servings')
    max_servings = data.get('max_servings')
    # Nutritional filters
    max_calories = data.get('max_calories')  # per serving
    min_protein = data.get('min_protein')  # grams per serving
    max_carbs = data.get('max_carbs')  # grams per serving
    max_fat = data.get('max_fat')  # grams per serving
    max_sugar = data.get('max_sugar')  # grams per serving
    max_sodium = data.get('max_sodium')  # mg per serving
    sort_by = data.get('sort_by', 'title')  # 'title', 'prep_time', 'cook_time', 'total_time', 'created_at'
    sort_order = data.get('sort_order', 'asc')  # 'asc', 'desc'
    page = data.get('page', 1)
    per_page = data.get('per_page', 20)

    try:
        # Build query with joins for nutrition filtering
        recipes_query = Recipe.query.outerjoin(Nutrition, Recipe.id == Nutrition.recipe_id)

        # Text search in title and description
        if query:
            recipes_query = recipes_query.filter(
                db.or_(
                    Recipe.title.ilike(f'%{query}%'),
                    Recipe.description.ilike(f'%{query}%')
                )
            )

        # Filter by dietary preferences
        if dietary_preferences:
            for pref in dietary_preferences:
                # Check if recipe has this dietary preference in its JSON field
                recipes_query = recipes_query.filter(
                    Recipe.dietary_preferences.like(f'%{pref}%')
                )

        # Filter by cuisine type
        if cuisine_type:
            recipes_query = recipes_query.filter(Recipe.cuisine_type == cuisine_type)

        # Filter by difficulty level
        if difficulty_level:
            recipes_query = recipes_query.filter(Recipe.difficulty_level == difficulty_level)

        # Filter by preparation time
        if max_prep_time:
            recipes_query = recipes_query.filter(Recipe.prep_time <= max_prep_time)

        # Filter by cooking time
        if max_cook_time:
            recipes_query = recipes_query.filter(Recipe.cook_time <= max_cook_time)

        # Filter by total time
        if max_total_time:
            recipes_query = recipes_query.filter(Recipe.total_time <= max_total_time)

        # Filter by servings
        if min_servings:
            recipes_query = recipes_query.filter(Recipe.servings >= min_servings)
        if max_servings:
            recipes_query = recipes_query.filter(Recipe.servings <= max_servings)

        # Nutritional filters
        if max_calories:
            recipes_query = recipes_query.filter(Nutrition.calories <= max_calories)
        if min_protein:
            recipes_query = recipes_query.filter(Nutrition.protein >= min_protein)
        if max_carbs:
            recipes_query = recipes_query.filter(Nutrition.carbohydrates <= max_carbs)
        if max_fat:
            recipes_query = recipes_query.filter(Nutrition.fat <= max_fat)
        if max_sugar:
            recipes_query = recipes_query.filter(Nutrition.sugar <= max_sugar)
        if max_sodium:
            recipes_query = recipes_query.filter(Nutrition.sodium <= max_sodium)

        # Apply sorting
        sort_column = getattr(Recipe, sort_by, Recipe.title)
        if sort_order == 'desc':
            recipes_query = recipes_query.order_by(sort_column.desc())
        else:
            recipes_query = recipes_query.order_by(sort_column.asc())

        # Apply pagination
        total_recipes = recipes_query.count()
        recipes = recipes_query.offset((page - 1) * per_page).limit(per_page).all()

        # Format results
        recipe_list = []
        for recipe in recipes:
            full_recipe = get_recipe_with_details(recipe.id)
            recipe_ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()

            recipe_data = {
                "id": recipe.id,
                "title": recipe.title,
                "description": recipe.description,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "servings": recipe.servings,
                "cuisine_type": recipe.cuisine_type,
                "difficulty_level": recipe.difficulty_level,
                "dietary_preferences": recipe.dietary_preferences,
                "total_time": recipe.total_time,
                "source": recipe.source,
                "image_url": recipe.image_url,
                "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
                "ingredients_count": len(recipe_ingredients),
                "ingredients": [
                    {
                        "name": ing.name,
                        "quantity": ing.quantity,
                        "unit": ing.unit,
                        "notes": ing.notes
                    } for ing in recipe_ingredients
                ],
                "instructions_count": len(full_recipe.instructions_list) if full_recipe.instructions_list else 0,
                "has_nutrition": full_recipe.nutrition_info is not None,
                "nutrition": {
                    "calories": full_recipe.nutrition_info.calories if full_recipe.nutrition_info else None,
                    "protein": full_recipe.nutrition_info.protein if full_recipe.nutrition_info else None,
                    "carbohydrates": full_recipe.nutrition_info.carbohydrates if full_recipe.nutrition_info else None,
                    "fat": full_recipe.nutrition_info.fat if full_recipe.nutrition_info else None,
                    "fiber": full_recipe.nutrition_info.fiber if full_recipe.nutrition_info else None,
                    "sugar": full_recipe.nutrition_info.sugar if full_recipe.nutrition_info else None,
                    "sodium": full_recipe.nutrition_info.sodium if full_recipe.nutrition_info else None,
                } if full_recipe.nutrition_info else None
            }
            recipe_list.append(recipe_data)

        # Calculate pagination info
        total_pages = (total_recipes + per_page - 1) // per_page

        return jsonify({
            "total_recipes": total_recipes,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page,
            "recipes": recipe_list,
            "filters_applied": {
                "query": query,
                "dietary_preferences": dietary_preferences,
                "cuisine_type": cuisine_type,
                "difficulty_level": difficulty_level,
                "max_prep_time": max_prep_time,
                "max_cook_time": max_cook_time,
                "max_total_time": max_total_time,
                "min_servings": min_servings,
                "max_servings": max_servings,
                "max_calories": max_calories,
                "min_protein": min_protein,
                "max_carbs": max_carbs,
                "max_fat": max_fat,
                "max_sugar": max_sugar,
                "max_sodium": max_sodium,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        })

    except Exception as e:
        print(f"Error searching recipes: {e}")
        return jsonify({"error": "Failed to search recipes"}), 500

@app.route("/recipe-filters", methods=["GET"])
@require_api_key
def get_recipe_filters_route():
    """Get available filter options for recipes"""
    try:
        # Get distinct values for filter dropdowns
        cuisine_types = db.session.query(Recipe.cuisine_type).distinct().filter(
            Recipe.cuisine_type.isnot(None)
        ).all()
        cuisine_types = [ct[0] for ct in cuisine_types if ct[0]]

        difficulty_levels = db.session.query(Recipe.difficulty_level).distinct().filter(
            Recipe.difficulty_level.isnot(None)
        ).all()
        difficulty_levels = [dl[0] for dl in difficulty_levels if dl[0]]

        # Extract dietary preferences from JSON fields
        all_dietary_prefs = set()
        recipes = Recipe.query.filter(Recipe.dietary_preferences.isnot(None)).all()
        for recipe in recipes:
            try:
                prefs = json.loads(recipe.dietary_preferences)
                all_dietary_prefs.update(prefs)
            except:
                pass

        dietary_preferences = sorted(list(all_dietary_prefs))

        # Get time ranges
        time_stats = db.session.query(
            db.func.min(Recipe.prep_time),
            db.func.max(Recipe.prep_time),
            db.func.min(Recipe.cook_time),
            db.func.max(Recipe.cook_time),
            db.func.min(Recipe.total_time),
            db.func.max(Recipe.total_time),
            db.func.min(Recipe.servings),
            db.func.max(Recipe.servings)
        ).first()

        return jsonify({
            "cuisine_types": cuisine_types,
            "difficulty_levels": difficulty_levels,
            "dietary_preferences": dietary_preferences,
            "time_ranges": {
                "prep_time": {
                    "min": time_stats[0],
                    "max": time_stats[1]
                },
                "cook_time": {
                    "min": time_stats[2],
                    "max": time_stats[3]
                },
                "total_time": {
                    "min": time_stats[4],
                    "max": time_stats[5]
                },
                "servings": {
                    "min": time_stats[6],
                    "max": time_stats[7]
                }
            },
            "sort_options": [
                {"value": "title", "label": "Title"},
                {"value": "prep_time", "label": "Preparation Time"},
                {"value": "cook_time", "label": "Cooking Time"},
                {"value": "total_time", "label": "Total Time"},
                {"value": "created_at", "label": "Date Created"},
                {"value": "servings", "label": "Servings"}
            ]
        })

    except Exception as e:
        print(f"Error getting recipe filters: {e}")
        return jsonify({"error": "Failed to get filter options"}), 500

@app.route("/rate-recipe", methods=["POST"])
@require_api_key
def rate_recipe_route():
    """Rate a recipe (for collaborative filtering)"""
    data = request.get_json()

    if not data or 'user_id' not in data or 'recipe_id' not in data or 'rating' not in data:
        return jsonify({"error": "user_id, recipe_id, and rating are required"}), 400

    user_id = data['user_id']
    recipe_id = data['recipe_id']
    rating = data['rating']
    review = data.get('review', '')

    if not (1 <= rating <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    try:
        from database_models import RecipeRating

        # Check if rating already exists
        existing_rating = RecipeRating.query.filter_by(
            user_id=user_id, recipe_id=recipe_id
        ).first()

        if existing_rating:
            existing_rating.rating = rating
            existing_rating.review = review
        else:
            new_rating = RecipeRating(
                user_id=user_id,
                recipe_id=recipe_id,
                rating=rating,
                review=review
            )
            db.session.add(new_rating)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Rating saved successfully"
        })

    except Exception as e:
        print(f"Error saving rating: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to save rating"}), 500

@app.route("/recipe/<int:recipe_id>/ratings", methods=["GET"])
@require_api_key
def get_recipe_ratings_route(recipe_id):
    """Get ratings for a specific recipe"""
    try:
        from database_models import RecipeRating

        ratings = RecipeRating.query.filter_by(recipe_id=recipe_id).all()

        ratings_data = []
        for rating in ratings:
            ratings_data.append({
                "user_id": rating.user_id,
                "rating": rating.rating,
                "review": rating.review,
                "created_at": rating.created_at.isoformat() if rating.created_at else None
            })

        # Calculate average rating
        if ratings:
            avg_rating = sum(r.rating for r in ratings) / len(ratings)
        else:
            avg_rating = 0

        return jsonify({
            "recipe_id": recipe_id,
            "total_ratings": len(ratings),
            "average_rating": round(avg_rating, 2),
            "ratings": ratings_data
        })

    except Exception as e:
        print(f"Error getting ratings: {e}")
        return jsonify({"error": "Failed to get ratings"}), 500

# ===== AUTHENTICATION ENDPOINTS =====

@app.route("/save-recipe", methods=["POST"])
@token_required
def save_recipe(current_user):
    """Save a generated recipe to the database"""
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({"error": "Recipe title is required"}), 400

    try:
        # Parse ingredients if provided as text
        ingredients_text = data.get('ingredients', '')
        ingredients_list = []

        if isinstance(ingredients_text, str):
            # Parse simple ingredient list from text
            lines = [line.strip() for line in ingredients_text.split('\n') if line.strip()]
            for line in lines:
                # Simple parsing: assume format like "2 cups flour" or just "flour"
                parts = line.split(' ', 2)
                if len(parts) >= 2 and parts[0].isdigit():
                    quantity = float(parts[0])
                    unit = parts[1] if len(parts) > 2 else None
                    name = ' '.join(parts[2:]) if len(parts) > 2 else parts[1]
                else:
                    quantity = None
                    unit = None
                    name = line

                ingredients_list.append({
                    'name': name,
                    'quantity': quantity,
                    'unit': unit
                })
        elif isinstance(ingredients_text, list):
            ingredients_list = ingredients_text

        # Create the recipe
        recipe = Recipe(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description', ''),
            prep_time=data.get('prep_time'),
            cook_time=data.get('cook_time'),
            servings=data.get('servings', 4),
            cuisine_type=data.get('cuisine_type', 'General'),
            difficulty_level=data.get('difficulty_level', 'medium'),
            dietary_preferences=data.get('dietary_preferences'),
            total_time=data.get('total_time') or (data.get('prep_time', 0) + data.get('cook_time', 0)),
            source='user_generated'
        )

        db.session.add(recipe)
        db.session.flush()  # Get the recipe ID

        # Add ingredients
        for ing_data in ingredients_list:
            if isinstance(ing_data, dict):
                ingredient = Ingredient(
                    recipe_id=recipe.id,
                    name=ing_data.get('name', ''),
                    quantity=ing_data.get('quantity'),
                    unit=ing_data.get('unit'),
                    notes=ing_data.get('notes')
                )
            else:
                # Handle string ingredients
                ingredient = Ingredient(
                    recipe_id=recipe.id,
                    name=str(ing_data)
                )
            db.session.add(ingredient)

        # Add instructions if provided
        instructions_text = data.get('instructions', '')
        if instructions_text:
            if isinstance(instructions_text, str):
                # Split by newlines or numbered steps
                lines = [line.strip() for line in instructions_text.split('\n') if line.strip()]
                step_num = 1
                for line in lines:
                    # Remove numbering if present (e.g., "1. " or "Step 1: ")
                    line = line.lstrip('0123456789. ')
                    if line.startswith('Step ') and ': ' in line:
                        line = line.split(': ', 1)[1]
                    if line:
                        instruction = Instruction(
                            recipe_id=recipe.id,
                            step_number=step_num,
                            description=line
                        )
                        db.session.add(instruction)
                        step_num += 1
            elif isinstance(instructions_text, list):
                for i, desc in enumerate(instructions_text, 1):
                    instruction = Instruction(
                        recipe_id=recipe.id,
                        step_number=i,
                        description=str(desc)
                    )
                    db.session.add(instruction)

        # Add nutrition info if provided
        nutrition_data = data.get('nutrition')
        if nutrition_data:
            nutrition = Nutrition(
                recipe_id=recipe.id,
                calories=nutrition_data.get('calories'),
                protein=nutrition_data.get('protein'),
                carbohydrates=nutrition_data.get('carbohydrates'),
                fat=nutrition_data.get('fat'),
                fiber=nutrition_data.get('fiber'),
                sugar=nutrition_data.get('sugar'),
                sodium=nutrition_data.get('sodium')
            )
            db.session.add(nutrition)

        db.session.commit()

        # Return the saved recipe with full details
        saved_recipe = get_recipe_with_details(recipe.id)
        recipe_ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()

        recipe_data = {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "prep_time": recipe.prep_time,
            "cook_time": recipe.cook_time,
            "servings": recipe.servings,
            "cuisine_type": recipe.cuisine_type,
            "difficulty_level": recipe.difficulty_level,
            "dietary_preferences": recipe.dietary_preferences,
            "total_time": recipe.total_time,
            "source": recipe.source,
            "image_url": recipe.image_url,
            "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
            "ingredients": [
                {
                    "name": ing.name,
                    "quantity": ing.quantity,
                    "unit": ing.unit,
                    "notes": ing.notes
                } for ing in recipe_ingredients
            ],
            "instructions": [
                {
                    "step_number": inst.step_number,
                    "description": inst.description
                } for inst in saved_recipe.instructions_list
            ] if saved_recipe.instructions_list else [],
            "nutrition": {
                "calories": saved_recipe.nutrition_info.calories if saved_recipe.nutrition_info else None,
                "protein": saved_recipe.nutrition_info.protein if saved_recipe.nutrition_info else None,
                "carbohydrates": saved_recipe.nutrition_info.carbohydrates if saved_recipe.nutrition_info else None,
                "fat": saved_recipe.nutrition_info.fat if saved_recipe.nutrition_info else None,
                "fiber": saved_recipe.nutrition_info.fiber if saved_recipe.nutrition_info else None,
                "sugar": saved_recipe.nutrition_info.sugar if saved_recipe.nutrition_info else None,
                "sodium": saved_recipe.nutrition_info.sodium if saved_recipe.nutrition_info else None,
            } if saved_recipe.nutrition_info else None
        }

        return jsonify({
            "success": True,
            "message": "Recipe saved successfully",
            "recipe": recipe_data
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error saving recipe: {e}")
        return jsonify({"error": "Failed to save recipe"}), 500

@app.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409

    try:
        # Create new user
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password,
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )

        db.session.add(new_user)
        db.session.commit()

        # Create default preferences
        default_prefs = {
            'dietary_restrictions': '[]',
            'favorite_cuisines': '["Italian", "Chinese"]',
            'cooking_skill_level': 'intermediate',
            'preferred_servings': '4'
        }

        for key, value in default_prefs.items():
            set_user_preference(new_user.id, key, value)

        # Generate token
        token = jwt.encode({
            'user_id': new_user.id,
            'username': new_user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, JWT_SECRET_KEY, algorithm="HS256")

        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    # Find user
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Check if user has a password (local auth) or is OAuth-only
    if user.password_hash is None:
        # User was created without a password (OAuth or incomplete setup)
        return jsonify({'error': 'This account was created via OAuth. Please use Google or Facebook login.'}), 401

    if not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Generate token
    token = jwt.encode({
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET_KEY, algorithm="HS256")

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    })

@app.route('/auth/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile"""
    preferences = get_user_preferences(current_user.id)

    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'profile_image': current_user.profile_image,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None
        },
        'preferences': preferences
    })

@app.route('/auth/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile"""
    data = request.get_json()

    try:
        # Update user info
        if 'first_name' in data:
            current_user.first_name = data['first_name']
        if 'last_name' in data:
            current_user.last_name = data['last_name']
        if 'email' in data:
            # Check if email is already taken by another user
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != current_user.id:
                return jsonify({'error': 'Email already in use'}), 409
            current_user.email = data['email']

        # Update preferences
        if 'preferences' in data:
            for key, value in data['preferences'].items():
                set_user_preference(current_user.id, key, value)

        db.session.commit()

        preferences = get_user_preferences(current_user.id)

        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name
            },
            'preferences': preferences
        })

    except Exception as e:
        db.session.rollback()
        print(f"Profile update error: {e}")
        return jsonify({'error': 'Profile update failed'}), 500

@app.route('/auth/favorites', methods=['GET'])
@token_required
def get_favorites(current_user):
    """Get user's favorite recipes"""
    try:
        favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        favorite_recipes = []

        for fav in favorites:
            recipe = Recipe.query.get(fav.recipe_id)
            if recipe:
                full_recipe = get_recipe_with_details(recipe.id)
                recipe_ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()

                recipe_data = {
                    "id": recipe.id,
                    "title": recipe.title,
                    "description": recipe.description,
                    "prep_time": recipe.prep_time,
                    "cook_time": recipe.cook_time,
                    "servings": recipe.servings,
                    "cuisine_type": recipe.cuisine_type,
                    "difficulty_level": recipe.difficulty_level,
                    "dietary_preferences": recipe.dietary_preferences,
                    "total_time": recipe.total_time,
                    "source": recipe.source,
                    "image_url": recipe.image_url,
                    "favorited_at": fav.created_at.isoformat() if fav.created_at else None,
                    "ingredients_count": len(recipe_ingredients),
                    "instructions_count": len(full_recipe.instructions_list) if full_recipe.instructions_list else 0,
                    "has_nutrition": full_recipe.nutrition_info is not None
                }
                favorite_recipes.append(recipe_data)

        return jsonify({
            'favorites': favorite_recipes,
            'total': len(favorite_recipes)
        })
    except Exception as e:
        print(f"Get favorites error: {e}")
        return jsonify({'error': 'Failed to get favorites'}), 500

@app.route('/auth/favorites/<int:recipe_id>', methods=['POST'])
@token_required
def add_favorite(current_user, recipe_id):
    """Add recipe to user's favorites"""
    try:
        # Check if recipe exists
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        # Check if already favorited
        existing_fav = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
        if existing_fav:
            return jsonify({'message': 'Recipe already in favorites'}), 200

        # Add to favorites
        favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(favorite)
        db.session.commit()

        return jsonify({
            'message': 'Recipe added to favorites',
            'recipe_id': recipe_id
        })
    except Exception as e:
        db.session.rollback()
        print(f"Add favorite error: {e}")
        return jsonify({'error': 'Failed to add favorite'}), 500

@app.route('/auth/favorites/<int:recipe_id>', methods=['DELETE'])
@token_required
def remove_favorite(current_user, recipe_id):
    """Remove recipe from user's favorites"""
    try:
        favorite = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
        if not favorite:
            return jsonify({'error': 'Recipe not in favorites'}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({
            'message': 'Recipe removed from favorites',
            'recipe_id': recipe_id
        })
    except Exception as e:
        db.session.rollback()
        print(f"Remove favorite error: {e}")
        return jsonify({'error': 'Failed to remove favorite'}), 500

@app.route('/auth/cooking-history', methods=['GET'])
@token_required
def get_cooking_history(current_user):
    """Get user's cooking history"""
    try:
        history = CookingHistory.query.filter_by(user_id=current_user.id).order_by(CookingHistory.cooked_at.desc()).all()
        cooking_history = []

        for item in history:
            recipe = Recipe.query.get(item.recipe_id)
            if recipe:
                recipe_data = {
                    "id": item.id,
                    "recipe_id": recipe.id,
                    "recipe_title": recipe.title,
                    "recipe_image": recipe.image_url,
                    "cooked_at": item.cooked_at.isoformat() if item.cooked_at else None,
                    "rating": item.rating,
                    "notes": item.notes,
                    "cuisine_type": recipe.cuisine_type,
                    "difficulty_level": recipe.difficulty_level
                }
                cooking_history.append(recipe_data)

        return jsonify({
            'history': cooking_history,
            'total': len(cooking_history)
        })
    except Exception as e:
        print(f"Get cooking history error: {e}")
        return jsonify({'error': 'Failed to get cooking history'}), 500

@app.route('/auth/cooking-history', methods=['POST'])
@token_required
def add_cooking_history(current_user):
    """Add recipe to cooking history"""
    data = request.get_json()

    if not data or 'recipe_id' not in data:
        return jsonify({'error': 'recipe_id is required'}), 400

    recipe_id = data['recipe_id']
    rating = data.get('rating')
    notes = data.get('notes')

    try:
        # Check if recipe exists
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        # Add to cooking history
        history_item = CookingHistory(
            user_id=current_user.id,
            recipe_id=recipe_id,
            rating=rating,
            notes=notes
        )
        db.session.add(history_item)
        db.session.commit()

        return jsonify({
            'message': 'Recipe added to cooking history',
            'history_id': history_item.id,
            'recipe_id': recipe_id
        })
    except Exception as e:
        db.session.rollback()
        print(f"Add cooking history error: {e}")
        return jsonify({'error': 'Failed to add to cooking history'}), 500

# ===== OAUTH ENDPOINTS =====

@app.route('/auth/google/login')
def google_login():
    """Initiate Google OAuth login"""
    if not GOOGLE_CLIENT_ID:
        return jsonify({'error': 'Google OAuth not configured'}), 500

    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def google_auth():
    """Handle Google OAuth callback"""
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()

        # Check if user already exists
        user = User.query.filter_by(oauth_id=user_info['id'], oauth_provider='google').first()

        if not user:
            # Check if email already exists
            existing_user = User.query.filter_by(email=user_info['email']).first()
            if existing_user:
                # Link OAuth to existing account
                existing_user.oauth_provider = 'google'
                existing_user.oauth_id = user_info['id']
                existing_user.profile_image = user_info.get('picture')
                user = existing_user
            else:
                # Create new user
                username = user_info['email'].split('@')[0] + '_google'
                # Ensure unique username
                counter = 1
                original_username = username
                while User.query.filter_by(username=username).first():
                    username = f"{original_username}_{counter}"
                    counter += 1

                user = User(
                    username=username,
                    email=user_info['email'],
                    first_name=user_info.get('given_name'),
                    last_name=user_info.get('family_name'),
                    profile_image=user_info.get('picture'),
                    oauth_provider='google',
                    oauth_id=user_info['id']
                )
                db.session.add(user)

                # Create default preferences
                default_prefs = {
                    'dietary_restrictions': '[]',
                    'favorite_cuisines': '["Italian", "Chinese"]',
                    'cooking_skill_level': 'intermediate',
                    'preferred_servings': '4'
                }
                for key, value in default_prefs.items():
                    set_user_preference(user.id, key, value)

            db.session.commit()

        # Generate JWT token
        jwt_token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, JWT_SECRET_KEY, algorithm="HS256")

        # Redirect to frontend with token
        redirect_url = f"{FRONTEND_URL}/oauth/callback?token={jwt_token}&provider=google"
        return redirect(redirect_url)

    except Exception as e:
        print(f"Google OAuth error: {e}")
        return redirect(f"{FRONTEND_URL}/login?error=oauth_failed")

@app.route('/auth/facebook/login')
def facebook_login():
    """Initiate Facebook OAuth login"""
    if not FACEBOOK_APP_ID:
        return jsonify({'error': 'Facebook OAuth not configured'}), 500

    redirect_uri = url_for('facebook_auth', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@app.route('/auth/facebook/callback')
def facebook_auth():
    """Handle Facebook OAuth callback"""
    try:
        token = oauth.facebook.authorize_access_token()
        user_info = oauth.facebook.get('me?fields=id,email,first_name,last_name,picture').json()

        # Check if user already exists
        user = User.query.filter_by(oauth_id=user_info['id'], oauth_provider='facebook').first()

        if not user:
            # Check if email already exists
            existing_user = User.query.filter_by(email=user_info.get('email')).first()
            if existing_user:
                # Link OAuth to existing account
                existing_user.oauth_provider = 'facebook'
                existing_user.oauth_id = user_info['id']
                if user_info.get('picture') and user_info['picture'].get('data'):
                    existing_user.profile_image = user_info['picture']['data']['url']
                user = existing_user
            else:
                # Create new user
                username = user_info.get('email', f"fb_user_{user_info['id']}").split('@')[0] + '_facebook'
                # Ensure unique username
                counter = 1
                original_username = username
                while User.query.filter_by(username=username).first():
                    username = f"{original_username}_{counter}"
                    counter += 1

                user = User(
                    username=username,
                    email=user_info.get('email'),
                    first_name=user_info.get('first_name'),
                    last_name=user_info.get('last_name'),
                    oauth_provider='facebook',
                    oauth_id=user_info['id']
                )

                if user_info.get('picture') and user_info['picture'].get('data'):
                    user.profile_image = user_info['picture']['data']['url']

                db.session.add(user)

                # Create default preferences
                default_prefs = {
                    'dietary_restrictions': '[]',
                    'favorite_cuisines': '["Italian", "Chinese"]',
                    'cooking_skill_level': 'intermediate',
                    'preferred_servings': '4'
                }
                for key, value in default_prefs.items():
                    set_user_preference(user.id, key, value)

            db.session.commit()

        # Generate JWT token
        jwt_token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, JWT_SECRET_KEY, algorithm="HS256")

        # Redirect to frontend with token
        redirect_url = f"{FRONTEND_URL}/oauth/callback?token={jwt_token}&provider=facebook"
        return redirect(redirect_url)

    except Exception as e:
        print(f"Facebook OAuth error: {e}")
        return redirect(f"{FRONTEND_URL}/login?error=oauth_failed")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host="0.0.0.0", port=port)

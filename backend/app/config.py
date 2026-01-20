import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# For future use (Milestone 2,3)
MODEL_NAME = "resnet50"

# API Key configuration
API_KEY = os.getenv("API_KEY", "intelligent-recipe-generator-api-key-2023")  # Secure API key for authentication, defaults to env var
REQUIRED_API_KEY = os.getenv("REQUIRED_API_KEY", "True").lower() == "true"  # Enable API key requirement for security, defaults to True

# External API Keys
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY")
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Recipe Data Collection API Keys
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")
THEMEALDB_API_KEY = os.getenv("THEMEALDB_API_KEY")  # Usually not required

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///instance/intelligent_recipe.db")

# JWT Configuration for Authentication
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-2023")

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")

# Frontend URL for OAuth redirects
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

#!/usr/bin/env python3
"""
AI Recipe Image Generator using Google Gemini
Generates custom images for recipes using AI
"""
import google.generativeai as genai
from config import GOOGLE_GEMINI_API_KEY
# Note: This file still uses deprecated google.generativeai for image generation
# Consider updating to google-genai package when image generation becomes available
import base64
import io
from PIL import Image
import os
import uuid

def generate_recipe_image(recipe_name, ingredients=[], cuisine="General", style="photorealistic"):
    """
    Generate an AI image for a recipe using Google Gemini

    Args:
        recipe_name (str): Name of the recipe
        ingredients (list): List of ingredient names
        cuisine (str): Cuisine type for styling
        style (str): Image style (photorealistic, artistic, cartoon, etc.)

    Returns:
        dict: Response with image data or error
    """
    if not GOOGLE_GEMINI_API_KEY or GOOGLE_GEMINI_API_KEY == "your_google_gemini_api_key_here":
        return {
            "error": "Google Gemini API key not configured",
            "message": "Please configure your Gemini API key in the .env file"
        }

    try:
        # Configure Gemini API
        genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

        # Select appropriate model for image generation
        # From our testing, we know gemini-2.0-flash-exp-image-generation exists
        model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')

        # Prepare ingredients list for prompt
        if ingredients and len(ingredients) > 0:
            ingredients_str = ", ".join(ingredients[:5])  # Limit to first 5 ingredients
            if len(ingredients) > 5:
                ingredients_str += f" and {len(ingredients) - 5} more ingredients"
        else:
            ingredients_str = "fresh ingredients"

        # Create detailed prompt for image generation
        prompt = f"""Create a beautiful, appetizing image of the dish: {recipe_name}

Key elements to include:
- Main dish: {recipe_name}
- Ingredients visible: {ingredients_str}
- Style: {style}
- Cuisine: {cuisine}
- Food photography quality
- Professional plating
- Appetizing presentation
- Warm, inviting colors
- High resolution, detailed

The image should look like a professional food photograph that would appear in a cookbook or restaurant menu. Make it realistic and mouth-watering."""

        print(f"🤖 Generating AI image for: {recipe_name}")
        print(f"📝 Using ingredients: {ingredients_str}")
        print(f"🏺 Cuisine: {cuisine}, Style: {style}")

        # Generate the image
        response = model.generate_content(prompt)

        # Process the response
        if response and hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]

            # Check if there's image content
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data'):
                        # Base64 encoded image data
                        image_data = part.inline_data.data
                        mime_type = part.inline_data.mime_type

                        # Decode base64 to bytes
                        image_bytes = base64.b64decode(image_data)

                        # Create PIL Image for verification
                        image = Image.open(io.BytesIO(image_bytes))

                        # Save image to uploads directory
                        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'ai_images')
                        os.makedirs(upload_dir, exist_ok=True)

                        # Generate unique filename
                        file_extension = 'png'  # Gemini typically generates PNG
                        unique_filename = f"ai_recipe_{uuid.uuid4().hex}.{file_extension}"
                        file_path = os.path.join(upload_dir, unique_filename)

                        # Save the image
                        image.save(file_path, format=file_extension.upper())

                        # Return success response
                        image_url = f"/uploads/ai_images/{unique_filename}"

                        return {
                            "success": True,
                            "message": f"AI image generated successfully for {recipe_name}",
                            "image_url": image_url,
                            "recipe_name": recipe_name,
                            "ingredients_used": ingredients,
                            "cuisine": cuisine,
                            "style": style,
                            "ai_provider": "gemini",
                            "image_size": f"{image.width}x{image.height}",
                            "file_path": file_path
                        }

        # If we get here, no image was generated
        return {
            "error": "No image generated",
            "message": "Gemini API did not return an image. This may be due to content filters or API limitations."
        }

    except Exception as e:
        print(f"❌ Gemini Image Generation Error: {e}")
        return {
            "error": f"Image generation failed: {str(e)}",
            "message": "Failed to generate AI image. This may be due to API rate limits, content filters, or connectivity issues."
        }

def generate_recipe_image_dalle(recipe_name, ingredients=[], cuisine="General", style="photorealistic"):
    """
    Alternative implementation using OpenAI DALL-E (if available)
    This would be used if Gemini image generation fails
    """
    try:
        from openai import OpenAI
        from config import OPENAI_API_KEY

        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            return None  # Not configured

        client = OpenAI(api_key=OPENAI_API_KEY)

        # Prepare ingredients for prompt
        ingredients_str = ", ".join(ingredients[:5]) if ingredients else "fresh ingredients"

        prompt = f"""Professional food photograph of {recipe_name}, featuring {ingredients_str}.
        {cuisine} cuisine, {style} style, appetizing presentation, high resolution, cookbook quality."""

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        return {
            "success": True,
            "message": f"DALL-E image generated for {recipe_name}",
            "image_url": image_url,
            "recipe_name": recipe_name,
            "ingredients_used": ingredients,
            "cuisine": cuisine,
            "style": style,
            "ai_provider": "dalle"
        }

    except Exception as e:
        print(f"DALL-E image generation failed: {e}")
        return None

def generate_fallback_recipe_image(recipe_name, ingredients=[], cuisine="General"):
    """
    Generate a fallback image URL using stock photo services
    Used when AI image generation is not available
    """
    # Use Unsplash or similar service for stock food images
    import random

    # Keywords based on recipe name and ingredients
    keywords = [recipe_name.lower()]

    # Add ingredient keywords
    if ingredients:
        keywords.extend([ing.lower() for ing in ingredients[:3]])

    # Add cuisine-specific keywords
    cuisine_keywords = {
        'Italian': ['pasta', 'pizza', 'italian food'],
        'Chinese': ['chinese food', 'stir fry', 'asian cuisine'],
        'Indian': ['curry', 'indian food', 'spicy food'],
        'Mexican': ['tacos', 'mexican food', 'burrito'],
        'Thai': ['thai food', 'asian noodles'],
        'Japanese': ['sushi', 'ramen', 'japanese food'],
        'French': ['french cuisine', 'baguette'],
        'American': ['burger', 'comfort food']
    }

    if cuisine in cuisine_keywords:
        keywords.extend(cuisine_keywords[cuisine])

    # Select random keywords and create search term
    selected_keywords = random.sample(keywords, min(3, len(keywords)))
    search_term = '+'.join(selected_keywords)

    # Generate Unsplash URL
    image_id = str(uuid.uuid4())[:8]
    fallback_url = f"https://source.unsplash.com/featured/?{search_term},{image_id}/800x600"

    return {
        "success": True,
        "message": f"Fallback stock image for {recipe_name}",
        "image_url": fallback_url,
        "recipe_name": recipe_name,
        "ingredients_used": ingredients,
        "cuisine": cuisine,
        "ai_provider": "stock_photo",
        "is_fallback": True
    }

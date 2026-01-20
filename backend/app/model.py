import random
import hashlib
from PIL import Image
import io
import base64
import requests
from config import GOOGLE_VISION_API_KEY, OPENAI_API_KEY
import re

# Try to import torchvision for image classification
try:
    import torch
    import torchvision.transforms as transforms
    from torchvision.models import resnet50
    HAVE_TORCHVISION = True
    # Load ImageNet class names
    try:
        import urllib.request
        import json
        url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
        with urllib.request.urlopen(url) as f:
            classes = [line.decode('utf-8').strip() for line in f.readlines()]
        IMAGENET_CLASSES = classes
    except Exception:
        IMAGENET_CLASSES = []
except Exception:
    HAVE_TORCHVISION = False
    IMAGENET_CLASSES = []

INGREDIENTS = [
    "tomato", "onion", "garlic", "carrot", "potato", "chicken", "beef", "rice",
    "pasta", "cheese", "lettuce", "broccoli", "spinach", "mushroom", "bell pepper",
    "egg", "milk", "flour", "sugar", "salt", "chips", "lays", "bread", "butter",
    "oil", "pepper", "cabbage", "cucumber", "apple", "banana", "orange", "lemon",
    "ginger", "corn", "peas", "beans", "fish", "shrimp", "pork", "lamb", "turkey",
    "yogurt", "cream", "soy sauce", "vinegar", "honey", "chocolate", "nuts", "seeds",
    "avocado", "strawberry", "blueberry", "mango", "pineapple", "watermelon",
    "grapes", "celery", "cauliflower", "eggplant", "zucchini", "squash", "pumpkin"
]

# Additional ingredient mappings and variations
INGREDIENT_VARIATIONS = {
    "lays": "chips",
    "lay's": "chips",
    "potato chips": "chips",
    "french fries": "potato",
    "fries": "potato",
    "tomatos": "tomato",
    "potatos": "potato",
    "carrots": "carrot",
    "onions": "onion",
    "eggs": "egg",
    "chickens": "chicken",
    "beefs": "beef",
    "fishs": "fish",
    "shrimps": "shrimp",
    "tomatoes": "tomato",
    "potatoes": "potato",
    "carrots": "carrot",
    "onions": "onion",
    "lettuces": "lettuce",
    "broccolis": "broccoli",
    "spinaches": "spinach",
    "mushrooms": "mushroom",
    "peppers": "bell pepper",
    "peppers": "bell pepper",
    "apples": "apple",
    "bananas": "banana",
    "oranges": "orange",
    "lemons": "lemon",
    "strawberries": "strawberry",
    "blueberries": "blueberry",
    "mangos": "mango",
    "pineapples": "pineapple",
    "watermelons": "watermelon",
    "grapes": "grapes",
    "nuts": "nuts",
    "seeds": "seeds",
    "fresh": "lettuce",  # Common prefix
    "organic": "lettuce",  # Common prefix
    "green": "lettuce",
    "red": "tomato"
}

def get_google_vision_prediction(pil_img, ocr_text=""):
    """
    Use Google Vision API for image analysis if API key is available.
    """
    if not GOOGLE_VISION_API_KEY:
        return None

    try:
        # Convert PIL image to base64
        buffer = io.BytesIO()
        pil_img.save(buffer, format='JPEG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Google Vision API request
        url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"
        payload = {
            "requests": [{
                "image": {"content": img_base64},
                "features": [
                    {"type": "LABEL_DETECTION", "maxResults": 10},
                    {"type": "TEXT_DETECTION"}
                ]
            }]
        }

        response = requests.post(url, json=payload)
        result = response.json()

        if 'responses' in result and result['responses']:
            response_data = result['responses'][0]

            # Extract labels
            labels = []
            if 'labelAnnotations' in response_data:
                labels = [label['description'].lower() for label in response_data['labelAnnotations']]

            # Check for ingredients in labels
            for ingredient in INGREDIENTS:
                if ingredient in labels:
                    return {
                        "name": ingredient.capitalize(),
                        "confidence": 0.9
                    }

            # If no direct match, try to find food-related labels
            food_labels = [label for label in labels if any(food in label for food in ['food', 'vegetable', 'fruit', 'meat', 'dairy'])]
            if food_labels:
                return {
                    "name": food_labels[0].capitalize(),
                    "confidence": 0.8
                }

    except Exception as e:
        print(f"Google Vision API error: {e}")

    return None

def get_openai_prediction(pil_img, ocr_text=""):
    """
    Use OpenAI API for image analysis if API key is available.
    Returns a list of ingredient dicts.
    """
    if not OPENAI_API_KEY:
        return None

    try:
        # Convert PIL image to base64
        buffer = io.BytesIO()
        pil_img.save(buffer, format='JPEG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # OpenAI API request
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = (
            f"Analyze this food image and identify all visible ingredients. "
            f"OCR text: '{ocr_text}'. "
            f"Respond with a JSON array of ingredients with their names and confidence scores (0-1): "
            f"[{{'ingredient': 'name', 'confidence': 0.95}}]"
        )

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                        }
                    ]
                }
            ],
            "max_tokens": 200  # Increased for multiple ingredients
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if 'choices' in result and result['choices']:
            content = result['choices'][0]['message']['content']
            # Try to parse JSON from response
            try:
                import json
                parsed = json.loads(content)
                ingredients = []

                # Handle array of ingredients
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and 'ingredient' in item and 'confidence' in item:
                            ingredients.append({
                                "name": item['ingredient'].capitalize(),
                                "confidence": item['confidence']
                            })
                # Handle single ingredient (backward compatibility)
                elif isinstance(parsed, dict) and 'ingredient' in parsed and 'confidence' in parsed:
                    ingredients.append({
                        "name": parsed['ingredient'].capitalize(),
                        "confidence": parsed['confidence']
                    })

                if ingredients:
                    return ingredients

            except Exception as e:
                print(f"JSON parsing error: {e}")

    except Exception as e:
        print(f"OpenAI API error: {e}")

    return None

def spell_check_text(text):
    """
    Apply spell checking to OCR text to correct common mistakes.
    Disabled because it was making incorrect corrections (e.g., 'rice' -> 'Vice').
    """
    # Spell checking is disabled as it was causing more harm than good
    # by making incorrect corrections to food-related terms
    return text

def classify_image(pil_img):
    """
    Use ResNet50 to classify the image and return potential ingredients.
    """
    if not HAVE_TORCHVISION or not IMAGENET_CLASSES:
        return None

    try:
        # Load model lazily
        model = resnet50(pretrained=True)
        model.eval()

        # Preprocess image
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        input_tensor = preprocess(pil_img)
        input_batch = input_tensor.unsqueeze(0)  # Create a mini-batch

        with torch.no_grad():
            output = model(input_batch)

        # Get top 5 predictions
        _, indices = torch.topk(output, 5)
        predictions = [IMAGENET_CLASSES[idx] for idx in indices[0]]

        print(f"Image classification predictions: {predictions}")

        # Map to ingredients
        for pred in predictions:
            pred_lower = pred.lower()
            for ingredient in INGREDIENTS:
                if ingredient in pred_lower:
                    return {"name": ingredient.capitalize(), "confidence": 0.7}

        # Check for food-related classes with better mapping
        food_class_mapping = {
            # Fruits
            "orange": "orange", "lemon": "lemon", "apple": "apple", "banana": "banana",
            "grape": "grapes", "strawberry": "strawberry", "pineapple": "pineapple",
            "watermelon": "watermelon", "mango": "mango", "peach": "peach", "pear": "pear",

            # Vegetables
            "broccoli": "broccoli", "carrot": "carrot", "lettuce": "lettuce", "tomato": "tomato",
            "onion": "onion", "garlic": "garlic", "potato": "potato", "cucumber": "cucumber",
            "bell pepper": "bell pepper", "pepper": "bell pepper", "spinach": "spinach",
            "cabbage": "cabbage", "cauliflower": "cauliflower", "eggplant": "eggplant",

            # Proteins
            "chicken": "chicken", "beef": "beef", "fish": "fish", "shrimp": "shrimp",
            "pork": "pork", "turkey": "turkey", "egg": "egg", "bacon": "pork",

            # Dairy and grains
            "bread": "bread", "cheese": "cheese", "milk": "milk", "butter": "butter",
            "rice": "rice", "pasta": "pasta", "noodle": "pasta",

            # Other foods
            "chocolate": "chocolate", "nuts": "nuts", "yogurt": "yogurt", "honey": "honey",
            "sugar": "sugar", "flour": "flour", "salt": "salt", "oil": "oil",

            # Common food containers/packages that indicate food
            "packet": "unknown",  # Could be any packaged food
            "box": "unknown",
            "can": "unknown",
            "bottle": "unknown",

            # Better food recognition
            "hot pot": "unknown",  # Kitchen item, not food
            "caldron": "unknown",  # Kitchen item, not food
            "consomme": "unknown",  # Could be soup
            "soup bowl": "unknown",
            "plate": "unknown",
            "French loaf": "bread",
            "eggnog": "egg",  # Contains egg
            "dough": "flour"  # Made from flour
        }

        for pred in predictions:
            pred_lower = pred.lower()
            if pred_lower in food_class_mapping:
                ingredient = food_class_mapping[pred_lower]
                if ingredient != "unknown":
                    return {"name": ingredient.capitalize(), "confidence": 0.6}

        # Additional fuzzy matching for food-related predictions
        for pred in predictions:
            pred_lower = pred.lower()
            # Check if prediction contains food-related keywords
            food_keywords = ["fruit", "vegetable", "food", "meal", "dish", "produce"]
            for keyword in food_keywords:
                if keyword in pred_lower:
                    # Try to map to a reasonable default ingredient
                    return {"name": "Lettuce", "confidence": 0.4}  # Default to common vegetable

        return None

    except Exception as e:
        print(f"Image classification error: {e}")
        return None

def extract_ingredients_from_text(ocr_text):
    """
    Extract all possible ingredients from OCR text with enhanced pattern matching and context awareness.
    Returns a list of tuples (ingredient, confidence).
    """
    if not ocr_text:
        return []

    # Apply spell checking to improve accuracy
    corrected_text = spell_check_text(ocr_text)

    ocr_lower = corrected_text.lower()
    found_ingredients = []

    print(f"Analyzing OCR text for ingredients: '{corrected_text[:200]}...'")

    # Enhanced ingredient detection with multiple patterns

    # 1. Check for ingredient variations first (highest priority)
    for variation, ingredient in INGREDIENT_VARIATIONS.items():
        if variation in ocr_lower:
            if ingredient not in [ing for ing, conf in found_ingredients]:
                found_ingredients.append((ingredient, 0.95))
                print(f"Found variation '{variation}' -> '{ingredient}'")

    # 2. Check for direct ingredient matches with word boundaries
    for ingredient in INGREDIENTS:
        # Use word boundaries for more accurate matching
        pattern = r'\b' + re.escape(ingredient) + r'\b'
        if re.search(pattern, ocr_lower):
            if ingredient not in [ing for ing, conf in found_ingredients]:
                found_ingredients.append((ingredient, 0.9))
                print(f"Found direct ingredient match: '{ingredient}'")

    # 3. Enhanced partial matching with better logic
    words = re.findall(r'\b\w+\b', ocr_lower)
    for word in words:
        # Skip common stop words and very short words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'an', 'a', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'fresh', 'organic', 'natural', 'ingredients', 'contains', 'made', 'from', 'with', 'serving', 'size', 'calories', 'fat', 'protein', 'carbs'}
        if word in stop_words or len(word) < 3:
            continue

        for ingredient in INGREDIENTS:
            if len(word) >= 3 and len(ingredient) >= 3:
                # Exact match (already covered above, but keeping for completeness)
                if word == ingredient:
                    if ingredient not in [ing for ing, conf in found_ingredients]:
                        found_ingredients.append((ingredient, 0.9))
                        print(f"Found exact match: '{word}' -> ingredient '{ingredient}'")

                # Partial substring matching with better rules
                elif (word in ingredient or ingredient in word) and abs(len(word) - len(ingredient)) <= 2:
                    if ingredient not in [ing for ing, conf in found_ingredients]:
                        found_ingredients.append((ingredient, 0.8))
                        print(f"Found partial match: word '{word}' -> ingredient '{ingredient}'")

                # Plural forms (more comprehensive)
                elif word.endswith('s') and word[:-1] == ingredient:
                    if ingredient not in [ing for ing, conf in found_ingredients]:
                        found_ingredients.append((ingredient, 0.85))
                        print(f"Found plural match: '{word}' -> ingredient '{ingredient}'")

                elif word.endswith('es') and word[:-2] == ingredient:
                    if ingredient not in [ing for ing, conf in found_ingredients]:
                        found_ingredients.append((ingredient, 0.85))
                        print(f"Found plural match: '{word}' -> ingredient '{ingredient}'")

                elif word.endswith('ies') and word[:-3] + 'y' == ingredient:
                    if ingredient not in [ing for ing, conf in found_ingredients]:
                        found_ingredients.append((ingredient, 0.85))
                        print(f"Found plural match: '{word}' -> ingredient '{ingredient}'")

                # Fuzzy matching with improved threshold
                else:
                    try:
                        import difflib
                        similarity = difflib.SequenceMatcher(None, word, ingredient).ratio()
                        if similarity > 0.85 and len(word) >= 4:  # Higher similarity threshold
                            if ingredient not in [ing for ing, conf in found_ingredients]:
                                found_ingredients.append((ingredient, 0.75))
                                print(f"Found fuzzy match: '{word}' -> '{ingredient}' (similarity: {similarity:.2f})")
                    except ImportError:
                        pass  # difflib is built-in, but just in case

    # 4. Pattern-based ingredient detection (for common cooking contexts)
    cooking_patterns = [
        # Quantity + ingredient patterns
        r'\b(\d+(?:\.\d+)?)\s*(?:cups?|cups?|tbsp|tsp|oz|g|kg|ml|l|lb|pounds?|pound)\s+(\w+)',
        # Ingredient with common prefixes
        r'\b(?:fresh|organic|dried|ground|chopped|sliced|minced)\s+(\w+)',
        # Common ingredient phrases
        r'\b(\w+)\s+(?:powder|flour|oil|sauce|paste|extract)',
        # Meat/protein indicators
        r'\b(\w+)\s+(?:breast|thigh|wing|fillet|steak|chop)',
    ]

    for pattern in cooking_patterns:
        matches = re.findall(pattern, ocr_lower)
        for match in matches:
            if isinstance(match, tuple):
                # For quantity patterns, take the ingredient part
                candidate = match[1] if len(match) > 1 else match[0]
            else:
                candidate = match

            # Check if the candidate is in our ingredient list
            for ingredient in INGREDIENTS:
                if candidate == ingredient or (len(candidate) >= 4 and difflib.SequenceMatcher(None, candidate, ingredient).ratio() > 0.8):
                    if ingredient not in [ing for ing, conf in found_ingredients]:
                        found_ingredients.append((ingredient, 0.8))
                        print(f"Found pattern match: '{candidate}' -> ingredient '{ingredient}'")
                        break

    # 5. Common food-related keyword detection
    food_keywords = {
        'noodle': 'pasta',
        'noodles': 'pasta',
        'pasta': 'pasta',
        'rice': 'rice',
        'bread': 'bread',
        'chicken': 'chicken',
        'beef': 'beef',
        'pork': 'pork',
        'fish': 'fish',
        'seafood': 'fish',
        'shrimp': 'shrimp',
        'vegetable': 'lettuce',
        'vegetables': 'lettuce',
        'salad': 'lettuce',
        'fruit': 'apple',
        'fruits': 'apple',
        'snack': 'chips',
        'chips': 'chips',
        'instant': 'pasta',
        'cheese': 'cheese',
        'milk': 'milk',
        'egg': 'egg',
        'eggs': 'egg',
        'onion': 'onion',
        'garlic': 'garlic',
        'tomato': 'tomato',
        'potato': 'potato',
        'carrot': 'carrot',
        'lettuce': 'lettuce',
        'broccoli': 'broccoli',
        'spinach': 'spinach',
        'mushroom': 'mushroom',
        'pepper': 'bell pepper',
        'meat': 'chicken',
        'protein': 'chicken'
    }

    for keyword, ingredient in food_keywords.items():
        if keyword in ocr_lower:
            if ingredient not in [ing for ing, conf in found_ingredients]:
                found_ingredients.append((ingredient, 0.7))
                print(f"Found food keyword '{keyword}' -> ingredient '{ingredient}'")

    # Remove duplicates and sort by confidence
    unique_ingredients = []
    seen = set()
    for ing, conf in found_ingredients:
        if ing not in seen:
            unique_ingredients.append((ing, conf))
            seen.add(ing)

    return unique_ingredients

def get_predictions(pil_img, ocr_text=""):
    """
    Generate prediction using external APIs if available, otherwise fall back to local logic.
    Returns a dict with ingredients list, ocr_text.
    """
    print("\n=== Starting ingredient prediction ===")

    # Try Google Vision API first
    google_result = get_google_vision_prediction(pil_img, ocr_text)
    if google_result:
        print("Using Google Vision API result")
        return {
            "ingredients": [google_result],
            "ocr_text": ocr_text
        }

    # Try OpenAI API
    openai_results = get_openai_prediction(pil_img, ocr_text)
    if openai_results:
        print("Using OpenAI API result")
        return {
            "ingredients": openai_results,
            "ocr_text": ocr_text
        }

    # Fall back to local logic with enhanced ingredient extraction
    print("Using local ingredient extraction")

    found_ingredients = extract_ingredients_from_text(ocr_text)

    if found_ingredients:
        # Sort by confidence and return all matches above a threshold
        found_ingredients.sort(key=lambda x: x[1], reverse=True)
        # Include ingredients with confidence > 0.5 to catch more matches
        filtered_ingredients = [ing for ing in found_ingredients if ing[1] > 0.5]

        print(f"\nFound ingredients: {filtered_ingredients}\n")

        return {
            "ingredients": [{"name": ing[0].capitalize(), "confidence": ing[1]} for ing in filtered_ingredients],
            "ocr_text": ocr_text
        }

    # If still no match, try to infer from common food-related keywords
    ocr_lower = ocr_text.lower() if ocr_text else ""

    food_keywords = {
        "noodle": "pasta",
        "noodles": "pasta",
        "pasta": "pasta",
        "rice": "rice",
        "bread": "bread",
        "chicken": "chicken",
        "beef": "beef",
        "pork": "pork",
        "fish": "fish",
        "seafood": "fish",
        "shrimp": "shrimp",
        "vegetable": "lettuce",
        "vegetables": "lettuce",
        "salad": "lettuce",
        "fruit": "apple",
        "fruits": "apple",
        "snack": "chips",
        "chips": "chips",
        "instant": "pasta",
        "cheese": "cheese",
        "milk": "milk",
        "egg": "egg",
        "eggs": "egg",
        "onion": "onion",
        "garlic": "garlic",
        "tomato": "tomato",
        "potato": "potato",
        "carrot": "carrot",
        "lettuce": "lettuce",
        "broccoli": "broccoli",
        "spinach": "spinach",
        "mushroom": "mushroom",
        "pepper": "bell pepper",
        "meat": "chicken",
        "protein": "chicken"
    }

    inferred_ingredients = []
    for keyword, ingredient in food_keywords.items():
        if keyword in ocr_lower:
            inferred_ingredients.append({"name": ingredient.capitalize(), "confidence": 0.8})
            print(f"Found food keyword '{keyword}' -> ingredient '{ingredient}'")

    if inferred_ingredients:
        return {
            "ingredients": inferred_ingredients,
            "ocr_text": ocr_text
        }

    # For single vegetable photos, we DO want to detect ingredients using image classification
    # This allows users to upload photos of individual vegetables/fruits and get ingredient detection
    print("Trying image classification for vegetable/fruit identification...")
    classification_result = classify_image(pil_img)
    if classification_result:
        print(f"Image classification found: {classification_result}")
        return {
            "ingredients": [classification_result],
            "ocr_text": ocr_text
        }

    # If image classification fails and there's no OCR text with ingredients, return empty
    print("No ingredients detected from image or text")
    return {
        "ingredients": [],
        "ocr_text": ocr_text
    }

#!/usr/bin/env python3
"""
Sample Recipe Data Generator
Creates sample recipe data for testing and demonstration purposes.
Populates the database with realistic recipe data.
"""

from database_models import init_db, db, create_user, create_recipe, add_ingredient, add_instruction, add_nutrition, User, Recipe
from flask import Flask
from config import DATABASE_URL

# Create Flask app for database operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

SAMPLE_RECIPES = [
    {
        "title": "Classic Spaghetti Carbonara",
        "description": "Traditional Italian pasta dish with eggs, cheese, pancetta, and black pepper",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 4,
        "ingredients": [
            {"name": "spaghetti", "quantity": 400, "unit": "grams", "notes": "dry"},
            {"name": "pancetta", "quantity": 150, "unit": "grams", "notes": "diced"},
            {"name": "eggs", "quantity": 3, "unit": "large", "notes": "whole"},
            {"name": "parmesan cheese", "quantity": 100, "unit": "grams", "notes": "grated"},
            {"name": "black pepper", "quantity": 1, "unit": "teaspoon", "notes": "freshly ground"},
            {"name": "salt", "quantity": 1, "unit": "teaspoon", "notes": "to taste"}
        ],
        "instructions": [
            {"step_number": 1, "description": "Bring a large pot of salted water to boil. Cook spaghetti according to package directions until al dente."},
            {"step_number": 2, "description": "While pasta cooks, heat a large skillet over medium heat. Add diced pancetta and cook until crispy, about 5 minutes."},
            {"step_number": 3, "description": "In a bowl, whisk together eggs, grated parmesan cheese, and black pepper."},
            {"step_number": 4, "description": "Reserve 1 cup of pasta cooking water, then drain the spaghetti."},
            {"step_number": 5, "description": "Add hot spaghetti to the skillet with pancetta. Remove from heat."},
            {"step_number": 6, "description": "Quickly pour in the egg mixture, stirring constantly. Add reserved pasta water gradually to create a creamy sauce."},
            {"step_number": 7, "description": "Serve immediately with extra parmesan cheese and black pepper."}
        ],
        "nutrition": {
            "calories": 650,
            "protein": 28,
            "carbohydrates": 65,
            "fat": 28,
            "fiber": 3,
            "sugar": 2,
            "sodium": 890
        }
    },
    {
        "title": "Chicken Tikka Masala",
        "description": "Creamy and flavorful Indian curry with tender chicken pieces",
        "prep_time": 20,
        "cook_time": 30,
        "servings": 4,
        "ingredients": [
            {"name": "chicken breast", "quantity": 500, "unit": "grams", "notes": "cut into cubes"},
            {"name": "yogurt", "quantity": 200, "unit": "grams", "notes": "plain"},
            {"name": "garam masala", "quantity": 2, "unit": "teaspoons", "notes": ""},
            {"name": "cumin", "quantity": 1, "unit": "teaspoon", "notes": "ground"},
            {"name": "paprika", "quantity": 1, "unit": "teaspoon", "notes": ""},
            {"name": "turmeric", "quantity": 1, "unit": "teaspoon", "notes": ""},
            {"name": "ginger", "quantity": 2, "unit": "tablespoons", "notes": "grated"},
            {"name": "garlic", "quantity": 4, "unit": "cloves", "notes": "minced"},
            {"name": "tomato sauce", "quantity": 400, "unit": "grams", "notes": "canned"},
            {"name": "heavy cream", "quantity": 200, "unit": "ml", "notes": ""},
            {"name": "butter", "quantity": 2, "unit": "tablespoons", "notes": ""},
            {"name": "onion", "quantity": 1, "unit": "large", "notes": "chopped"},
            {"name": "cilantro", "quantity": 1, "unit": "bunch", "notes": "fresh, chopped"}
        ],
        "instructions": [
            {"step_number": 1, "description": "Mix yogurt with half the garam masala, cumin, paprika, turmeric, ginger, and garlic to make marinade."},
            {"step_number": 2, "description": "Add chicken cubes to marinade and let sit for 30 minutes (or overnight for better flavor)."},
            {"step_number": 3, "description": "Heat butter in a large pan. Add marinated chicken and cook until browned, about 8-10 minutes."},
            {"step_number": 4, "description": "Remove chicken from pan and set aside. In the same pan, add chopped onion and cook until soft."},
            {"step_number": 5, "description": "Add remaining garlic and ginger. Cook for 1 minute until fragrant."},
            {"step_number": 6, "description": "Add tomato sauce, remaining spices, and simmer for 10 minutes."},
            {"step_number": 7, "description": "Stir in heavy cream and return chicken to the pan. Simmer for another 10 minutes."},
            {"step_number": 8, "description": "Garnish with fresh cilantro and serve with rice or naan bread."}
        ],
        "nutrition": {
            "calories": 480,
            "protein": 35,
            "carbohydrates": 15,
            "fat": 32,
            "fiber": 3,
            "sugar": 8,
            "sodium": 720
        }
    },
    {
        "title": "Vegetable Stir Fry",
        "description": "Colorful and healthy vegetable stir fry with tofu",
        "prep_time": 15,
        "cook_time": 10,
        "servings": 4,
        "ingredients": [
            {"name": "tofu", "quantity": 300, "unit": "grams", "notes": "firm, cubed"},
            {"name": "broccoli", "quantity": 200, "unit": "grams", "notes": "florets"},
            {"name": "bell pepper", "quantity": 2, "unit": "medium", "notes": "sliced, mixed colors"},
            {"name": "carrot", "quantity": 2, "unit": "medium", "notes": "julienned"},
            {"name": "zucchini", "quantity": 1, "unit": "large", "notes": "sliced"},
            {"name": "soy sauce", "quantity": 3, "unit": "tablespoons", "notes": "low sodium"},
            {"name": "sesame oil", "quantity": 1, "unit": "tablespoon", "notes": ""},
            {"name": "garlic", "quantity": 3, "unit": "cloves", "notes": "minced"},
            {"name": "ginger", "quantity": 1, "unit": "tablespoon", "notes": "grated"},
            {"name": "cornstarch", "quantity": 1, "unit": "teaspoon", "notes": "mixed with 2 tbsp water"},
            {"name": "rice", "quantity": 200, "unit": "grams", "notes": "cooked, for serving"}
        ],
        "instructions": [
            {"step_number": 1, "description": "Press tofu to remove excess water, then cube it."},
            {"step_number": 2, "description": "Heat sesame oil in a wok or large skillet over high heat."},
            {"step_number": 3, "description": "Add tofu cubes and stir fry until golden, about 5 minutes. Remove and set aside."},
            {"step_number": 4, "description": "In the same wok, add garlic and ginger. Stir fry for 30 seconds."},
            {"step_number": 5, "description": "Add all vegetables and stir fry for 4-5 minutes until crisp-tender."},
            {"step_number": 6, "description": "Return tofu to the wok. Add soy sauce and cornstarch mixture."},
            {"step_number": 7, "description": "Stir fry for another 2 minutes until sauce thickens."},
            {"step_number": 8, "description": "Serve hot over steamed rice."}
        ],
        "nutrition": {
            "calories": 320,
            "protein": 18,
            "carbohydrates": 45,
            "fat": 12,
            "fiber": 6,
            "sugar": 8,
            "sodium": 580
        }
    },
    {
        "title": "Beef Tacos",
        "description": "Authentic Mexican beef tacos with fresh toppings",
        "prep_time": 15,
        "cook_time": 20,
        "servings": 4,
        "ingredients": [
            {"name": "ground beef", "quantity": 500, "unit": "grams", "notes": "80% lean"},
            {"name": "onion", "quantity": 1, "unit": "medium", "notes": "diced"},
            {"name": "garlic", "quantity": 3, "unit": "cloves", "notes": "minced"},
            {"name": "cumin", "quantity": 1, "unit": "tablespoon", "notes": "ground"},
            {"name": "chili powder", "quantity": 1, "unit": "tablespoon", "notes": ""},
            {"name": "oregano", "quantity": 1, "unit": "teaspoon", "notes": "dried"},
            {"name": "salt", "quantity": 1, "unit": "teaspoon", "notes": ""},
            {"name": "black pepper", "quantity": 0.5, "unit": "teaspoon", "notes": "ground"},
            {"name": "corn tortillas", "quantity": 8, "unit": "pieces", "notes": "small"},
            {"name": "lettuce", "quantity": 2, "unit": "cups", "notes": "shredded"},
            {"name": "tomato", "quantity": 2, "unit": "medium", "notes": "diced"},
            {"name": "cheddar cheese", "quantity": 150, "unit": "grams", "notes": "shredded"},
            {"name": "sour cream", "quantity": 200, "unit": "grams", "notes": "optional"},
            {"name": "lime", "quantity": 1, "unit": "whole", "notes": "cut into wedges"}
        ],
        "instructions": [
            {"step_number": 1, "description": "Heat a large skillet over medium-high heat. Add ground beef and cook until browned, breaking it up with a spoon."},
            {"step_number": 2, "description": "Add diced onion and minced garlic. Cook for 3-4 minutes until softened."},
            {"step_number": 3, "description": "Stir in cumin, chili powder, oregano, salt, and black pepper. Cook for 1 minute."},
            {"step_number": 4, "description": "Add 1/4 cup water and simmer for 5 minutes until thickened."},
            {"step_number": 5, "description": "Warm tortillas in a dry skillet or microwave."},
            {"step_number": 6, "description": "Fill each tortilla with beef mixture, lettuce, tomato, and cheese."},
            {"step_number": 7, "description": "Top with sour cream if desired and serve with lime wedges."}
        ],
        "nutrition": {
            "calories": 420,
            "protein": 28,
            "carbohydrates": 25,
            "fat": 24,
            "fiber": 4,
            "sugar": 4,
            "sodium": 680
        }
    },
    {
        "title": "Mediterranean Quinoa Salad",
        "description": "Healthy and refreshing quinoa salad with Mediterranean flavors",
        "prep_time": 15,
        "cook_time": 15,
        "servings": 4,
        "ingredients": [
            {"name": "quinoa", "quantity": 200, "unit": "grams", "notes": "uncooked"},
            {"name": "cucumber", "quantity": 1, "unit": "large", "notes": "diced"},
            {"name": "tomatoes", "quantity": 2, "unit": "medium", "notes": "diced"},
            {"name": "red onion", "quantity": 0.5, "unit": "medium", "notes": "finely chopped"},
            {"name": "kalamata olives", "quantity": 100, "unit": "grams", "notes": "pitted"},
            {"name": "feta cheese", "quantity": 150, "unit": "grams", "notes": "crumbled"},
            {"name": "olive oil", "quantity": 3, "unit": "tablespoons", "notes": "extra virgin"},
            {"name": "lemon juice", "quantity": 2, "unit": "tablespoons", "notes": "fresh"},
            {"name": "oregano", "quantity": 1, "unit": "teaspoon", "notes": "dried"},
            {"name": "salt", "quantity": 0.5, "unit": "teaspoon", "notes": ""},
            {"name": "black pepper", "quantity": 0.25, "unit": "teaspoon", "notes": "ground"},
            {"name": "fresh parsley", "quantity": 0.25, "unit": "cup", "notes": "chopped"}
        ],
        "instructions": [
            {"step_number": 1, "description": "Rinse quinoa under cold water. Cook in 400ml water according to package directions, about 15 minutes."},
            {"step_number": 2, "description": "Fluff cooked quinoa with a fork and let cool to room temperature."},
            {"step_number": 3, "description": "In a large bowl, combine cucumber, tomatoes, red onion, olives, and feta cheese."},
            {"step_number": 4, "description": "Add cooled quinoa to the vegetable mixture."},
            {"step_number": 5, "description": "In a small bowl, whisk together olive oil, lemon juice, oregano, salt, and pepper."},
            {"step_number": 6, "description": "Pour dressing over the salad and toss gently to combine."},
            {"step_number": 7, "description": "Sprinkle with fresh parsley and serve chilled or at room temperature."}
        ],
        "nutrition": {
            "calories": 380,
            "protein": 12,
            "carbohydrates": 35,
            "fat": 22,
            "fiber": 5,
            "sugar": 6,
            "sodium": 720
        }
    }
]

def generate_more_recipes(num_recipes=500):
    """Generate additional sample recipes by varying existing ones"""
    import random

    base_recipes = SAMPLE_RECIPES.copy()
    generated_recipes = []

    # Recipe templates with variations
    recipe_templates = [
        {
            "base": "Pasta",
            "variations": ["Primavera", "Alfredo", "Pesto", "Aglio e Olio", "Arrabbiata"],
            "ingredients": ["pasta", "olive oil", "garlic", "herbs", "vegetables", "cheese"]
        },
        {
            "base": "Chicken",
            "variations": ["Curry", "Stir Fry", "Grilled", "Roasted", "Soup"],
            "ingredients": ["chicken", "spices", "vegetables", "sauce", "rice"]
        },
        {
            "base": "Salad",
            "variations": ["Greek", "Caesar", "Caprese", "Cobb", "Nicoise"],
            "ingredients": ["lettuce", "vegetables", "dressing", "protein", "cheese"]
        },
        {
            "base": "Soup",
            "variations": ["Tomato", "Chicken Noodle", "Vegetable", "Lentil", "Creamy Mushroom"],
            "ingredients": ["broth", "vegetables", "protein", "cream", "herbs"]
        },
        {
            "base": "Burger",
            "variations": ["Classic", "Cheese", "Bacon", "Veggie", "Turkey"],
            "ingredients": ["ground meat", "bun", "lettuce", "tomato", "cheese", "condiments"]
        }
    ]

    for i in range(num_recipes):
        template = random.choice(recipe_templates)
        variation = random.choice(template["variations"])

        title = f"{variation} {template['base']}"

        # Avoid duplicates
        if any(r["title"] == title for r in generated_recipes + base_recipes):
            continue

        # Generate ingredients
        num_ingredients = random.randint(6, 12)
        ingredients = []
        for ing_name in random.sample(template["ingredients"], min(len(template["ingredients"]), num_ingredients)):
            ingredients.append({
                "name": ing_name,
                "quantity": random.randint(1, 500),
                "unit": random.choice(["grams", "cups", "tablespoons", "teaspoons", "pieces", "ml"]),
                "notes": random.choice(["", "fresh", "chopped", "diced", "grated", "minced"])
            })

        # Generate instructions
        instructions = []
        for step_num in range(1, random.randint(4, 8)):
            instructions.append({
                "step_number": step_num,
                "description": f"Step {step_num}: Perform cooking action for {template['base'].lower()} preparation."
            })

        # Generate nutrition (approximate)
        nutrition = {
            "calories": random.randint(200, 800),
            "protein": random.randint(10, 50),
            "carbohydrates": random.randint(20, 80),
            "fat": random.randint(5, 40),
            "fiber": random.randint(1, 10),
            "sugar": random.randint(1, 20),
            "sodium": random.randint(200, 1000)
        }

        recipe = {
            "title": title,
            "description": f"A delicious {variation.lower()} {template['base'].lower()} recipe",
            "prep_time": random.randint(5, 30),
            "cook_time": random.randint(10, 60),
            "servings": random.randint(2, 6),
            "ingredients": ingredients,
            "instructions": instructions,
            "nutrition": nutrition
        }

        generated_recipes.append(recipe)

        if len(generated_recipes) >= num_recipes:
            break

    return generated_recipes

def populate_sample_data():
    """Populate database with sample recipe data"""
    print("Starting sample data population...")

    with app.app_context():
        # Create or get a sample user
        user = db.session.query(User).filter_by(username='sample_user').first()
        if not user:
            user = create_user('sample_user', 'sample@example.com')

        # Add base recipes
        all_recipes = SAMPLE_RECIPES.copy()

        # Generate additional recipes to reach target
        additional_recipes = generate_more_recipes(495)  # 5 base + 495 generated = 500 total
        all_recipes.extend(additional_recipes)

        print(f"Total recipes to add: {len(all_recipes)}")

        successful = 0
        failed = 0

        for recipe_data in all_recipes:
            try:
                # Check if recipe already exists
                existing = db.session.query(Recipe).filter_by(
                    title=recipe_data['title']
                ).first()

                if existing:
                    continue

                # Create recipe
                recipe = create_recipe(
                    user_id=user.id,
                    title=recipe_data['title'],
                    description=recipe_data['description'],
                    prep_time=recipe_data['prep_time'],
                    cook_time=recipe_data['cook_time'],
                    servings=recipe_data['servings']
                )

                # Add ingredients
                for ingredient_data in recipe_data['ingredients']:
                    add_ingredient(
                        recipe_id=recipe.id,
                        name=ingredient_data['name'],
                        quantity=ingredient_data['quantity'],
                        unit=ingredient_data['unit'],
                        notes=ingredient_data['notes']
                    )

                # Add instructions
                for instruction_data in recipe_data['instructions']:
                    add_instruction(
                        recipe_id=recipe.id,
                        step_number=instruction_data['step_number'],
                        description=instruction_data['description']
                    )

                # Add nutrition
                if recipe_data['nutrition']:
                    add_nutrition(
                        recipe_id=recipe.id,
                        calories=recipe_data['nutrition'].get('calories'),
                        protein=recipe_data['nutrition'].get('protein'),
                        carbohydrates=recipe_data['nutrition'].get('carbohydrates'),
                        fat=recipe_data['nutrition'].get('fat'),
                        fiber=recipe_data['nutrition'].get('fiber'),
                        sugar=recipe_data['nutrition'].get('sugar'),
                        sodium=recipe_data['nutrition'].get('sodium')
                    )

                successful += 1
                if successful % 100 == 0:
                    print(f"Processed {successful} recipes...")

            except Exception as e:
                print(f"Error saving recipe '{recipe_data.get('title', 'Unknown')}': {e}")
                failed += 1
                continue

        db.session.commit()
        print("Sample data population complete!")
        print(f"Successfully added: {successful} recipes")
        print(f"Failed to add: {failed} recipes")
        print(f"Total recipes in database: {db.session.query(Recipe).count()}")

def main():
    """Main function"""
    print("Sample Recipe Data Generator")
    print("=" * 30)

    populate_sample_data()

if __name__ == "__main__":
    main()

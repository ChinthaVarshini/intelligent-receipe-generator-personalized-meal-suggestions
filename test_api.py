#!/usr/bin/env python3

import requests
import json

# Test the get-all-recipes API
url = "http://127.0.0.1:3000/get-all-recipes"
headers = {"X-API-Key": "intelligent-recipe-generator-api-key-2023"}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Total recipes: {data.get('total_recipes', 0)}")

        recipes = data.get('recipes', [])
        print("\nFirst 5 recipe names:")
        for i, recipe in enumerate(recipes[:5]):
            title = recipe.get('title', 'No title')
            print(f"{i+1}. {title}")

        if len(recipes) > 5:
            print(f"\n... and {len(recipes) - 5} more recipes")

        # Show structure of first recipe
        if recipes:
            print("\nFirst recipe structure:")
            print(json.dumps(recipes[0], indent=2)[:500] + "...")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Error: {e}")

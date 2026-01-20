import requests

API_BASE_URL = 'http://localhost:3000'
API_KEY = 'intelligent-recipe-generator-api-key-2023'

def test_search_recipes():
    """Test the search recipes endpoint with nutritional filters"""

    # Test nutritional filtering
    search_params = {
        "max_calories": 400,
        "min_protein": 10
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/search-recipes",
            json=search_params,
            headers={'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Search successful! Found {data['total_recipes']} recipes")
            for recipe in data['recipes'][:2]:  # Show first 2
                nutrition = recipe.get('nutrition', {})
                print(f"- {recipe['title']}: {nutrition.get('calories', 'N/A')} cal, {nutrition.get('protein', 'N/A')}g protein")
        else:
            print(f"Search failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error testing search: {e}")

def test_dietary_filters():
    """Test dietary preference filtering"""

    search_params = {
        "dietary_preferences": ["vegetarian"]
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/search-recipes",
            json=search_params,
            headers={'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Dietary search successful! Found {data['total_recipes']} vegetarian recipes")
        else:
            print(f"Dietary search failed: {response.status_code}")

    except Exception as e:
        print(f"Error testing dietary search: {e}")

if __name__ == "__main__":
    print("Testing nutritional information display and dietary filtering...")
    test_search_recipes()
    test_dietary_filters()

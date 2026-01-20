import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchRecipes, searchRecipes, setCurrentRecipe, clearGeneratedRecipe, clearSuggestions } from '../features/recipeSlice';
import { Link } from 'react-router-dom';
import './Recipes.css';

const Recipes = () => {
  const dispatch = useDispatch();
  const {
    recipes,
    generatedRecipe,
    suggestions,
    loading,
    error,
    totalRecipes
  } = useSelector(state => state.recipes);

  const { isAuthenticated } = useSelector(state => state.user);

  const [filters, setFilters] = useState({
    dietary_preferences: [],
    cuisine_type: '',
    difficulty_level: '',
    max_prep_time: '',
    max_cook_time: '',
    query: '',
    // Nutritional filters
    max_calories: '',
    min_protein: '',
    max_carbs: '',
    max_fat: '',
    max_sugar: '',
    max_sodium: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [favorites, setFavorites] = useState(new Set());
  const [favoriteLoading, setFavoriteLoading] = useState(new Set());

  useEffect(() => {
    console.log('Recipes component mounted');
    console.log('Current state:', { generatedRecipe: !!generatedRecipe, suggestions: !!suggestions, recipesLength: recipes.length, loading, error });

    // Fetch existing recipes if no generated content
    if (!generatedRecipe && !suggestions && recipes.length === 0) {
      console.log('Calling fetchRecipes()');
      dispatch(fetchRecipes()).then((result) => {
        console.log('fetchRecipes result:', result);
        if (result.type === 'recipes/fetchRecipes/fulfilled') {
          console.log('Recipes fetched successfully:', result.payload);
        } else if (result.type === 'recipes/fetchRecipes/rejected') {
          console.log('Recipes fetch failed:', result.error);
        }
      }).catch((error) => {
        console.log('fetchRecipes error:', error);
      });
    }
  }, [dispatch, generatedRecipe, suggestions, recipes.length]);

  // Load favorite status when recipes change or user logs in
  useEffect(() => {
    const loadFavoriteStatus = async () => {
      if (isAuthenticated && recipes.length > 0) {
        try {
          const token = localStorage.getItem('token');
          const response = await fetch('/auth/favorites', {
            headers: {
              'Authorization': `Bearer ${token}`,
              'X-API-Key': 'intelligent-recipe-generator-api-key-2023'
            }
          });

          if (response.ok) {
            const data = await response.json();
            const favoriteIds = new Set(data.favorites.map(fav => fav.id));
            setFavorites(favoriteIds);
          }
        } catch (err) {
          console.error('Error loading favorite status:', err);
        }
      } else {
        // Clear favorites if user logs out
        setFavorites(new Set());
      }
    };

    loadFavoriteStatus();
  }, [isAuthenticated, recipes]);

  const handleViewRecipe = (recipe) => {
    dispatch(setCurrentRecipe(recipe));
  };

  const handleClearGenerated = () => {
    dispatch(clearGeneratedRecipe());
    dispatch(clearSuggestions());
  };

  const handleApplyFilters = () => {
    // Convert empty strings to undefined for API
    const cleanFilters = {};
    Object.keys(filters).forEach(key => {
      if (filters[key] !== '' && !(Array.isArray(filters[key]) && filters[key].length === 0)) {
        cleanFilters[key] = filters[key];
      }
    });

    // Convert numeric strings to numbers
    const numericFields = ['max_calories', 'min_protein', 'max_carbs', 'max_fat', 'max_sugar', 'max_sodium', 'max_prep_time', 'max_cook_time'];
    numericFields.forEach(field => {
      if (cleanFilters[field]) {
        cleanFilters[field] = parseInt(cleanFilters[field], 10);
      }
    });

    dispatch(searchRecipes(cleanFilters));
  };

  const handleClearFilters = () => {
    setFilters({
      dietary_preferences: [],
      cuisine_type: '',
      difficulty_level: '',
      max_prep_time: '',
      max_cook_time: '',
      query: '',
      max_calories: '',
      min_protein: '',
      max_carbs: '',
      max_fat: '',
      max_sugar: '',
      max_sodium: ''
    });
    dispatch(fetchRecipes());
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleDietaryPreferenceToggle = (preference) => {
    setFilters(prev => ({
      ...prev,
      dietary_preferences: prev.dietary_preferences.includes(preference)
        ? prev.dietary_preferences.filter(p => p !== preference)
        : [...prev.dietary_preferences, preference]
    }));
  };

  const handleSaveGeneratedRecipe = async () => {
    if (!isAuthenticated) {
      alert('Please login to save recipes');
      return;
    }

    if (!generatedRecipe || !generatedRecipe.recipe) {
      alert('No recipe to save');
      return;
    }

    try {
      const token = localStorage.getItem('token');

      // Parse the generated recipe text to extract components
      const recipeText = generatedRecipe.recipe;
      const lines = recipeText.split('\n').map(line => line.trim()).filter(line => line);

      // Simple parsing - extract title from first line
      const title = lines[0] || 'Generated Recipe';

      // Extract ingredients and instructions from the text
      let ingredients = [];
      let instructions = [];
      let description = '';

      // Basic parsing logic - look for common patterns
      let inIngredients = false;
      let inInstructions = false;

      for (const line of lines.slice(1)) {
        const lowerLine = line.toLowerCase();
        if (lowerLine.includes('ingredients') || lowerLine.includes('ingredients:')) {
          inIngredients = true;
          inInstructions = false;
          continue;
        } else if (lowerLine.includes('instructions') || lowerLine.includes('directions') || lowerLine.includes('steps')) {
          inIngredients = false;
          inInstructions = true;
          continue;
        } else if (lowerLine.includes('description') || lowerLine.includes('about')) {
          inIngredients = false;
          inInstructions = false;
          continue;
        }

        if (inIngredients && line) {
          ingredients.push(line);
        } else if (inInstructions && line) {
          instructions.push(line);
        } else if (!inIngredients && !inInstructions && line && !description) {
          description = line;
        }
      }

      // If parsing didn't work well, use the whole text as instructions
      if (instructions.length === 0) {
        instructions = [recipeText];
      }
      if (ingredients.length === 0) {
        ingredients = generatedRecipe.ingredients || [];
      }

      const recipeData = {
        title: title,
        description: description,
        ingredients: ingredients,
        instructions: instructions,
        cuisine_type: 'General',
        difficulty_level: 'medium'
      };

      const response = await fetch('/save-recipe', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-API-Key': 'intelligent-recipe-generator-api-key-2023',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(recipeData)
      });

      if (response.ok) {
        const data = await response.json();

        // Automatically add the saved recipe to favorites
        if (data.recipe && data.recipe.id) {
          try {
            const token = localStorage.getItem('token');
            const favoriteResponse = await fetch(`/auth/favorites/${data.recipe.id}`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
                'X-API-Key': 'intelligent-recipe-generator-api-key-2023'
              }
            });

            if (favoriteResponse.ok) {
              alert('Recipe saved successfully and added to your favorites! ❤️');
            } else {
              alert('Recipe saved successfully! You can add it to favorites from the recipes list.');
            }
          } catch (favError) {
            console.error('Error adding to favorites:', favError);
            alert('Recipe saved successfully! You can add it to favorites from the recipes list.');
          }
        } else {
          alert('Recipe saved successfully! You can now add it to favorites.');
        }

        // Clear the generated recipe and refresh recipes list
        dispatch(clearGeneratedRecipe());
        dispatch(fetchRecipes());
      } else {
        const error = await response.json();
        alert(`Failed to save recipe: ${error.error}`);
      }
    } catch (err) {
      console.error('Save recipe error:', err);
      alert('Network error. Please try again.');
    }
  };

  const handleToggleFavorite = async (recipeId, event) => {
    event.preventDefault(); // Prevent navigation if clicked in card
    event.stopPropagation(); // Prevent event bubbling

    if (!isAuthenticated) {
      alert('Please login to save favorites');
      return;
    }

    setFavoriteLoading(prev => new Set(prev).add(recipeId));

    try {
      const token = localStorage.getItem('token');
      const isFavorited = favorites.has(recipeId);
      const response = await fetch(`/auth/favorites/${recipeId}`, {
        method: isFavorited ? 'DELETE' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-API-Key': 'intelligent-recipe-generator-api-key-2023'
        }
      });

      if (response.ok) {
        setFavorites(prev => {
          const newFavorites = new Set(prev);
          if (isFavorited) {
            newFavorites.delete(recipeId);
          } else {
            newFavorites.add(recipeId);
          }
          return newFavorites;
        });
      } else {
        alert('Failed to update favorites');
      }
    } catch (err) {
      console.error('Favorite toggle error:', err);
      alert('Network error. Please try again.');
    } finally {
      setFavoriteLoading(prev => {
        const newLoading = new Set(prev);
        newLoading.delete(recipeId);
        return newLoading;
      });
    }
  };

  const getRecipeImage = (recipe) => {
    // Get image based on recipe content or cuisine
    const title = (recipe.title || recipe.name || '').toLowerCase();
    const cuisine = (recipe.cuisine_type || '').toLowerCase();

    if (title.includes('pasta') || title.includes('italian')) {
      return '🍝';
    } else if (title.includes('chicken') || title.includes('stir') || cuisine.includes('chinese')) {
      return '🐔';
    } else if (title.includes('salad') || title.includes('fresh')) {
      return '🥗';
    } else if (cuisine.includes('indian')) {
      return '🍛';
    } else if (cuisine.includes('mexican')) {
      return '🌮';
    } else if (cuisine.includes('japanese')) {
      return '🍱';
    } else if (cuisine.includes('thai')) {
      return '🍜';
    } else {
      return '🍽️';
    }
  };

  const renderRecipeCard = (recipe, index) => {
    const matchPercent = recipe.match_percentage || recipe.match || recipe.matchScore || 0;
    const isMatching = matchPercent && Number(matchPercent) > 0;

    return (
      <div key={index} className={`recipe-card ${isMatching ? 'matching' : ''}`}>
        {isMatching && (
          <div className="match-badge">Match: {Math.round(matchPercent)}%</div>
        )}
      <div className="recipe-image">
        {recipe.image_url ? (
          <img
            src={recipe.image_url}
            alt={recipe.title}
            className="recipe-card-image"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'block';
            }}
          />
        ) : null}
        <span
          className="recipe-emoji"
          style={{ display: recipe.image_url ? 'none' : 'block' }}
        >
          {getRecipeImage(recipe)}
        </span>
      </div>
      <div className="recipe-header">
        <div className="title-section">
          <h3 className="recipe-title">{recipe.title || recipe.name}</h3>
          {isAuthenticated && recipe.id && (
            <button
              onClick={(e) => handleToggleFavorite(recipe.id, e)}
              className={`favorite-btn ${favorites.has(recipe.id) ? 'favorited' : ''}`}
              disabled={favoriteLoading.has(recipe.id)}
              title={favorites.has(recipe.id) ? 'Remove from favorites' : 'Add to favorites'}
            >
              {favoriteLoading.has(recipe.id) ? '⏳' : (favorites.has(recipe.id) ? '❤️' : '🤍')}
            </button>
          )}
        </div>
        {recipe.cuisine_type && (
          <span className="recipe-cuisine">{recipe.cuisine_type}</span>
        )}
      </div>

      <div className="recipe-meta">
        {recipe.prep_time && (
          <span className="meta-item">
            🕒 Prep: {recipe.prep_time}min
          </span>
        )}
        {recipe.cook_time && (
          <span className="meta-item">
            🔥 Cook: {recipe.cook_time}min
          </span>
        )}
        {recipe.servings && (
          <span className="meta-item">
            👥 Serves: {recipe.servings}
          </span>
        )}
        {recipe.difficulty_level && (
          <span className={`meta-item difficulty ${recipe.difficulty_level.toLowerCase()}`}>
            {recipe.difficulty_level}
          </span>
        )}
      </div>

      {recipe.description && (
        <p className="recipe-description">{recipe.description}</p>
      )}

      {recipe.ingredients && recipe.ingredients.length > 0 && (
        <div className="recipe-ingredients">
          <h4>Ingredients ({recipe.ingredients.length})</h4>
          <ul>
            {recipe.ingredients.slice(0, 5).map((ing, idx) => (
              <li key={idx}>
                {typeof ing === 'string' ? ing : `${ing.quantity || ''} ${ing.unit || ''} ${ing.name}`.trim()}
              </li>
            ))}
            {recipe.ingredients.length > 5 && (
              <li className="more-ingredients">+{recipe.ingredients.length - 5} more...</li>
            )}
          </ul>
        </div>
      )}

      {recipe.nutrition && (
        <div className="recipe-nutrition-summary">
          <h4>🥗 Nutrition (per serving)</h4>
          <div className="nutrition-summary">
            {recipe.nutrition.calories && (
              <span className="nutrition-item">
                {recipe.nutrition.calories} cal
              </span>
            )}
            {recipe.nutrition.protein && (
              <span className="nutrition-item">
                {recipe.nutrition.protein}g protein
              </span>
            )}
            {recipe.nutrition.carbohydrates && (
              <span className="nutrition-item">
                {recipe.nutrition.carbohydrates}g carbs
              </span>
            )}
            {recipe.nutrition.fat && (
              <span className="nutrition-item">
                {recipe.nutrition.fat}g fat
              </span>
            )}
          </div>
        </div>
      )}

      <div className="recipe-actions">
        <Link
          to={`/recipe/${recipe.id || index}`}
          className="btn btn-primary"
          onClick={() => handleViewRecipe(recipe)}
        >
          View Recipe
        </Link>
      </div>
    </div>
  );

  return (
    <div className="recipes-page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">Recipes</h1>
          {(generatedRecipe || suggestions) && (
            <button
              onClick={handleClearGenerated}
              className="btn btn-secondary"
            >
              Browse All Recipes
            </button>
          )}
        </div>

        {loading && (
          <div className="loading-section">
            <div className="spinner"></div>
            <p>Loading recipes...</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Generated Recipe */}
        {generatedRecipe && (
          <div className="generated-recipe-section">
            <h2>🎉 Generated Recipe</h2>
            <div className="generated-recipe">
              <div className="recipe-content">
                <pre>{generatedRecipe.recipe}</pre>
              </div>
              {isAuthenticated && (
                <div className="generated-recipe-actions">
                  <button
                    onClick={handleSaveGeneratedRecipe}
                    className="btn btn-primary"
                  >
                    💾 Save Recipe & Add to Favorites
                  </button>
                  <Link to="/profile" className="btn btn-secondary">
                    View My Favorites
                  </Link>
                </div>
              )}
              {!isAuthenticated && (
                <div className="auth-notice">
                  <span>🔐</span>
                  <Link to="/login">Login</Link> to save recipes to your favorites!
                </div>
              )}
            </div>
          </div>
        )}

        {/* Recipe Suggestions */}
        {suggestions && (
          <div className="suggestions-section">
            <h2>💡 Recipe Suggestions</h2>
            <div className="suggestions-content">
              <pre>{suggestions}</pre>
            </div>
          </div>
        )}

        {/* Filters Section */}
        {!generatedRecipe && !suggestions && (
          <div className="filters-section">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn btn-secondary filter-toggle"
            >
              {showFilters ? 'Hide Filters' : 'Show Filters'} 🔍
            </button>

            {showFilters && (
              <div className="filters-content">
                <div className="filter-row">
                  <div className="filter-group">
                    <label>Search:</label>
                    <input
                      type="text"
                      placeholder="Recipe name or description..."
                      value={filters.query}
                      onChange={(e) => handleFilterChange('query', e.target.value)}
                    />
                  </div>

                  <div className="filter-group">
                    <label>Cuisine:</label>
                    <select
                      value={filters.cuisine_type}
                      onChange={(e) => handleFilterChange('cuisine_type', e.target.value)}
                    >
                      <option value="">All Cuisines</option>
                      <option value="italian">Italian</option>
                      <option value="chinese">Chinese</option>
                      <option value="indian">Indian</option>
                      <option value="mexican">Mexican</option>
                      <option value="japanese">Japanese</option>
                      <option value="thai">Thai</option>
                      <option value="american">American</option>
                      <option value="french">French</option>
                    </select>
                  </div>

                  <div className="filter-group">
                    <label>Difficulty:</label>
                    <select
                      value={filters.difficulty_level}
                      onChange={(e) => handleFilterChange('difficulty_level', e.target.value)}
                    >
                      <option value="">Any Difficulty</option>
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="hard">Hard</option>
                    </select>
                  </div>
                </div>

                <div className="filter-row">
                  <div className="filter-group">
                    <label>Max Prep Time (min):</label>
                    <input
                      type="number"
                      placeholder="e.g. 30"
                      value={filters.max_prep_time}
                      onChange={(e) => handleFilterChange('max_prep_time', e.target.value)}
                    />
                  </div>

                  <div className="filter-group">
                    <label>Max Cook Time (min):</label>
                    <input
                      type="number"
                      placeholder="e.g. 60"
                      value={filters.max_cook_time}
                      onChange={(e) => handleFilterChange('max_cook_time', e.target.value)}
                    />
                  </div>
                </div>

                <div className="filter-row">
                  <div className="filter-group dietary-preferences">
                    <label>Dietary Preferences:</label>
                    <div className="checkbox-group">
                      {['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'low-carb'].map(pref => (
                        <label key={pref} className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={filters.dietary_preferences.includes(pref)}
                            onChange={() => handleDietaryPreferenceToggle(pref)}
                          />
                          {pref.charAt(0).toUpperCase() + pref.slice(1)}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="filter-row">
                  <h4>🥗 Nutritional Requirements (per serving)</h4>
                </div>

                <div className="filter-row nutritional-filters">
                  <div className="filter-group">
                    <label>Max Calories:</label>
                    <input
                      type="number"
                      placeholder="e.g. 500"
                      value={filters.max_calories}
                      onChange={(e) => handleFilterChange('max_calories', e.target.value)}
                    />
                  </div>

                  <div className="filter-group">
                    <label>Min Protein (g):</label>
                    <input
                      type="number"
                      placeholder="e.g. 20"
                      value={filters.min_protein}
                      onChange={(e) => handleFilterChange('min_protein', e.target.value)}
                    />
                  </div>

                  <div className="filter-group">
                    <label>Max Carbs (g):</label>
                    <input
                      type="number"
                      placeholder="e.g. 50"
                      value={filters.max_carbs}
                      onChange={(e) => handleFilterChange('max_carbs', e.target.value)}
                    />
                  </div>

                  <div className="filter-group">
                    <label>Max Fat (g):</label>
                    <input
                      type="number"
                      placeholder="e.g. 30"
                      value={filters.max_fat}
                      onChange={(e) => handleFilterChange('max_fat', e.target.value)}
                    />
                  </div>

                  <div className="filter-group">
                    <label>Max Sugar (g):</label>
                    <input
                      type="number"
                      placeholder="e.g. 10"
                      value={filters.max_sugar}
                      onChange={(e) => handleFilterChange('max_sugar', e.target.value)}
                    />
                  </div>

                  <div className="filter-group">
                    <label>Max Sodium (mg):</label>
                    <input
                      type="number"
                      placeholder="e.g. 500"
                      value={filters.max_sodium}
                      onChange={(e) => handleFilterChange('max_sodium', e.target.value)}
                    />
                  </div>
                </div>

                <div className="filter-actions">
                  <button onClick={handleApplyFilters} className="btn btn-primary">
                    Apply Filters
                  </button>
                  <button onClick={handleClearFilters} className="btn btn-secondary">
                    Clear Filters
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Recipe Grid */}
        {!generatedRecipe && !suggestions && recipes.length > 0 && (
          <div className="recipes-section">
            <div className="recipes-header">
              <h2>All Recipes ({totalRecipes})</h2>
              <Link to="/ingredients" className="btn btn-primary">
                Generate New Recipe
              </Link>
            </div>

            {!isAuthenticated && (
              <div className="auth-notice">
                <div className="auth-notice-content">
                  <span className="auth-icon">🔐</span>
                  <p><Link to="/login">Login</Link> to save recipes to your favorites!</p>
                </div>
              </div>
            )}

            <div className="recipes-grid">
              {recipes.map((recipe, index) => renderRecipeCard(recipe, index))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && recipes.length === 0 && !generatedRecipe && !suggestions && (
          <div className="empty-state">
            <div className="empty-content">
              <span className="empty-icon">🍽️</span>
              <h3>No recipes found</h3>
              <p>Start by adding some ingredients to generate your first recipe!</p>
              <Link to="/ingredients" className="btn btn-primary">
                Add Ingredients
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recipes;

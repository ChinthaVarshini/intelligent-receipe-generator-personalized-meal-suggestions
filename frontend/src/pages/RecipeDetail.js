import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import { generateInstructions } from '../features/recipeSlice';
import ImageUploadModal from '../components/ImageUploadModal';
import './RecipeDetail.css';

const RecipeDetail = () => {
  const dispatch = useDispatch();
  const { recipeId } = useParams();
  const { currentRecipe, instructions } = useSelector(state => state.recipes);
  const { isAuthenticated } = useSelector(state => state.user);
  const [generatingInstructions, setGeneratingInstructions] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);
  const [cookLoading, setCookLoading] = useState(false);
  const [showImageUpload, setShowImageUpload] = useState(false);
  const [recipeImageUrl, setRecipeImageUrl] = useState(currentRecipe?.image_url || null);

  const getRecipeImage = (recipe) => {
    // Return actual image URL if available, otherwise fallback to emoji
    if (recipeImageUrl) {
      return recipeImageUrl;
    }

    // Fallback emoji based on recipe content or cuisine
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
    } else if (cuisine.includes('french')) {
      return '🥖';
    } else if (cuisine.includes('mediterranean')) {
      return '🫒';
    } else if (cuisine.includes('american')) {
      return '🍔';
    } else {
      return '🍽️';
    }
  };

  const getRecipeImageDisplay = (recipe) => {
    const imageSrc = getRecipeImage(recipe);
    if (imageSrc.startsWith('http') || imageSrc.startsWith('/uploads')) {
      return (
        <img
          src={imageSrc}
          alt={recipe.title || recipe.name}
          className="recipe-image-large"
          onError={(e) => {
            // Fallback to emoji if image fails to load
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'block';
          }}
        />
      );
    } else {
      return <span className="recipe-emoji-large">{imageSrc}</span>;
    }
  };

  useEffect(() => {
    // If we don't have currentRecipe, try to get it from the recipes list
    if (!currentRecipe) {
      // This would need to be implemented to fetch individual recipe
      // For now, we'll assume the recipe is passed via state
    }
  }, [currentRecipe, recipeId]);

  const handleGenerateInstructions = async () => {
    if (currentRecipe) {
      setGeneratingInstructions(true);
      const recipeData = {
        name: currentRecipe.title || currentRecipe.name,
        ingredients: currentRecipe.ingredients || [],
        cuisine: currentRecipe.cuisine_type,
        difficulty: currentRecipe.difficulty_level
      };
      await dispatch(generateInstructions(recipeData));
      setGeneratingInstructions(false);
    }
  };

  const handleToggleFavorite = async () => {
    if (!isAuthenticated) {
      alert('Please login to save favorites');
      return;
    }

    setFavoriteLoading(true);
    try {
      const token = localStorage.getItem('token');
          const response = await fetch(`/auth/favorites/${currentRecipe.id}`, {
        method: isFavorite ? 'DELETE' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setIsFavorite(!isFavorite);
      } else {
        alert('Failed to update favorites');
      }
    } catch (err) {
      console.error('Favorite toggle error:', err);
      alert('Network error. Please try again.');
    } finally {
      setFavoriteLoading(false);
    }
  };

  const handleMarkAsCooked = async () => {
    if (!isAuthenticated) {
      alert('Please login to track your cooking history');
      return;
    }

    const rating = prompt('How would you rate this recipe? (1-5 stars, optional)');
    const notes = prompt('Any notes about your cooking experience? (optional)');

    if (rating && (rating < 1 || rating > 5)) {
      alert('Rating must be between 1 and 5');
      return;
    }

    setCookLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/auth/cooking-history', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          recipe_id: currentRecipe.id,
          rating: rating ? parseInt(rating) : null,
          notes: notes || null
        })
      });

      if (response.ok) {
        alert('Recipe added to your cooking history!');
      } else {
        alert('Failed to add to cooking history');
      }
    } catch (err) {
      console.error('Cooking history error:', err);
      alert('Network error. Please try again.');
    } finally {
      setCookLoading(false);
    }
  };

  useEffect(() => {
    // Check if recipe is already in favorites when component loads
    const checkFavoriteStatus = async () => {
      if (isAuthenticated && currentRecipe?.id) {
        try {
          const token = localStorage.getItem('token');
          const response = await fetch('/auth/favorites', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            const data = await response.json();
            const isFav = data.favorites.some(fav => fav.id === currentRecipe.id);
            setIsFavorite(isFav);
          }
        } catch (err) {
          console.error('Error checking favorite status:', err);
        }
      }
    };

    checkFavoriteStatus();
  }, [isAuthenticated, currentRecipe?.id]);

  const handleImageUploaded = (imageUrl) => {
    setRecipeImageUrl(imageUrl);
    // Update the currentRecipe state to reflect the new image
    if (currentRecipe) {
      // Note: In a real app, you might want to update the Redux store or refetch the recipe
      console.log('Recipe image updated:', imageUrl);
    }
  };

  if (!currentRecipe) {
    return (
      <div className="recipe-detail-page">
        <div className="container">
          <div className="error-state">
            <span className="error-icon">❌</span>
            <h3>Recipe not found</h3>
            <p>The recipe you're looking for doesn't exist or has been removed.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="recipe-detail-page">
      <div className="container">
        <div className="recipe-hero">
          <div className="recipe-image-container">
            {getRecipeImageDisplay(currentRecipe)}
            {/* Fallback emoji - hidden by default, shown if image fails */}
            <span className="recipe-emoji-large" style={{ display: 'none' }}>
              {getRecipeImage(currentRecipe).startsWith('http') ? '🍽️' : getRecipeImage(currentRecipe)}
            </span>
            {isAuthenticated && (
              <button
                onClick={() => setShowImageUpload(true)}
                className="upload-image-btn"
                title="Upload recipe image"
              >
                📷
              </button>
            )}
          </div>
          <div className="recipe-header">
            <div className="recipe-title-section">
              <h1 className="recipe-title">{currentRecipe.title || currentRecipe.name}</h1>
              {currentRecipe.cuisine_type && (
                <span className="recipe-cuisine">{currentRecipe.cuisine_type}</span>
              )}
            </div>
            {isAuthenticated && (
              <div className="recipe-actions">
                <button
                  onClick={handleToggleFavorite}
                  className={`favorite-btn ${isFavorite ? 'favorited' : ''}`}
                  disabled={favoriteLoading}
                >
                  {favoriteLoading ? '⏳' : (isFavorite ? '❤️' : '🤍')} {favoriteLoading ? 'Saving...' : (isFavorite ? 'Saved' : 'Save Recipe')}
                </button>
                <button
                  onClick={handleMarkAsCooked}
                  className="cook-btn"
                  disabled={cookLoading}
                >
                  {cookLoading ? '⏳' : '👨‍🍳'} {cookLoading ? 'Adding...' : 'I Cooked This!'}
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="recipe-meta-grid">
          {currentRecipe.prep_time && (
            <div className="meta-card">
              <span className="meta-icon">🕒</span>
              <div>
                <h4>Prep Time</h4>
                <p>{currentRecipe.prep_time} minutes</p>
              </div>
            </div>
          )}
          {currentRecipe.cook_time && (
            <div className="meta-card">
              <span className="meta-icon">🔥</span>
              <div>
                <h4>Cook Time</h4>
                <p>{currentRecipe.cook_time} minutes</p>
              </div>
            </div>
          )}
          {currentRecipe.total_time && (
            <div className="meta-card">
              <span className="meta-icon">⏱️</span>
              <div>
                <h4>Total Time</h4>
                <p>{currentRecipe.total_time} minutes</p>
              </div>
            </div>
          )}
          {currentRecipe.servings && (
            <div className="meta-card">
              <span className="meta-icon">👥</span>
              <div>
                <h4>Servings</h4>
                <p>{currentRecipe.servings} people</p>
              </div>
            </div>
          )}
          {currentRecipe.difficulty_level && (
            <div className="meta-card">
              <span className="meta-icon">📊</span>
              <div>
                <h4>Difficulty</h4>
                <p className={`difficulty ${currentRecipe.difficulty_level.toLowerCase()}`}>
                  {currentRecipe.difficulty_level}
                </p>
              </div>
            </div>
          )}
          {currentRecipe.dietary_preferences && (
            <div className="meta-card">
              <span className="meta-icon">🥗</span>
              <div>
                <h4>Dietary</h4>
                <p>{currentRecipe.dietary_preferences}</p>
              </div>
            </div>
          )}
        </div>

        {currentRecipe.description && (
          <div className="recipe-description">
            <h3>Description</h3>
            <p>{currentRecipe.description}</p>
          </div>
        )}

        <div className="recipe-content">
          <div className="ingredients-section">
            <h3>Ingredients</h3>
            {currentRecipe.ingredients && currentRecipe.ingredients.length > 0 ? (
              <ul className="ingredients-list">
                {currentRecipe.ingredients.map((ingredient, index) => (
                  <li key={index} className="ingredient-item">
                    {typeof ingredient === 'string' ? (
                      ingredient
                    ) : (
                      <>
                        <span className="quantity">{ingredient.quantity} {ingredient.unit}</span>
                        <span className="name">{ingredient.name}</span>
                        {ingredient.notes && <span className="notes">({ingredient.notes})</span>}
                      </>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No ingredients listed</p>
            )}
          </div>

          <div className="instructions-section">
            <div className="instructions-header">
              <h3>Cooking Instructions</h3>
              {(!currentRecipe.instructions || currentRecipe.instructions.length === 0) && (
                <button
                  onClick={handleGenerateInstructions}
                  className="btn btn-primary"
                  disabled={generatingInstructions}
                >
                  {generatingInstructions ? 'Generating...' : 'Generate Instructions'}
                </button>
              )}
            </div>

            {currentRecipe.instructions && currentRecipe.instructions.length > 0 ? (
              <ol className="instructions-list">
                {currentRecipe.instructions.map((instruction, index) => (
                  <li key={index} className="instruction-item">
                    {typeof instruction === 'string' ? (
                      instruction
                    ) : (
                      instruction.description
                    )}
                  </li>
                ))}
              </ol>
            ) : instructions && instructions.length > 0 ? (
              <div className="generated-instructions">
                <h4>🤖 AI-Generated Instructions</h4>
                <ol className="instructions-list">
                  {instructions.map((instruction, index) => (
                    <li key={index} className="instruction-item">
                      {instruction.description}
                    </li>
                  ))}
                </ol>
              </div>
            ) : (
              <div className="no-instructions">
                <p>No cooking instructions available.</p>
                <button
                  onClick={handleGenerateInstructions}
                  className="btn btn-primary"
                  disabled={generatingInstructions}
                >
                  {generatingInstructions ? 'Generating...' : 'Generate with AI'}
                </button>
              </div>
            )}
          </div>

          {currentRecipe.nutrition && (
            <div className="nutrition-section">
              <h3>🥗 Nutritional Information (per serving)</h3>
              <div className="nutrition-grid">
                <div className="nutrition-item">
                  <span className="value">{currentRecipe.nutrition.calories || 'N/A'}</span>
                  <span className="unit">calories</span>
                </div>
                <div className="nutrition-item">
                  <span className="value">{currentRecipe.nutrition.protein || 'N/A'}g</span>
                  <span className="unit">protein</span>
                </div>
                <div className="nutrition-item">
                  <span className="value">{currentRecipe.nutrition.carbohydrates || 'N/A'}g</span>
                  <span className="unit">carbs</span>
                </div>
                <div className="nutrition-item">
                  <span className="value">{currentRecipe.nutrition.fat || 'N/A'}g</span>
                  <span className="unit">fat</span>
                </div>
                <div className="nutrition-item">
                  <span className="value">{currentRecipe.nutrition.fiber || 'N/A'}g</span>
                  <span className="unit">fiber</span>
                </div>
                <div className="nutrition-item">
                  <span className="value">{currentRecipe.nutrition.sugar || 'N/A'}g</span>
                  <span className="unit">sugar</span>
                </div>
              </div>
              <p className="nutrition-note">* Nutritional values are approximate and based on standard ingredient data</p>
            </div>
          )}
        </div>
      </div>

      {/* Image Upload Modal */}
      {showImageUpload && (
        <ImageUploadModal
          isOpen={showImageUpload}
          onClose={() => setShowImageUpload(false)}
          onImageUploaded={handleImageUploaded}
          recipeId={currentRecipe.id}
        />
      )}
    </div>
  );
};

export default RecipeDetail;

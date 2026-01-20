import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { processImage, addIngredient, removeIngredient, clearIngredients } from '../features/ingredientSlice';
import { generateRecipe, generateRecipeSuggestions, setRecipes } from '../features/recipeSlice';
import { useNavigate } from 'react-router-dom';
import CameraModal from '../components/CameraModal';
import './Ingredients.css';

const Ingredients = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const { detectedIngredients, matchedRecipes, loading, error } = useSelector(state => state.ingredients);
  const [manualIngredient, setManualIngredient] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [selectedCuisine, setSelectedCuisine] = useState('General');
  const [isCameraOpen, setIsCameraOpen] = useState(false);

  // Automatically navigate to recipes when matched recipes are available
  useEffect(() => {
    if (matchedRecipes && matchedRecipes.length > 0 && !loading) {
      // Set recipes in the recipe slice and navigate
      dispatch(setRecipes(matchedRecipes));
      navigate('/recipes');
    }
  }, [matchedRecipes, loading, dispatch, navigate]);

  // Track if image processing has completed (even if no ingredients found)
  const [imageProcessed, setImageProcessed] = useState(false);

  useEffect(() => {
    // Set imageProcessed to true when loading completes (whether successful or not)
    if (!loading && !imageProcessed) {
      // Check if we just finished processing an image
      // This is a simple heuristic - if we have matchedRecipes (even if empty), processing completed
      if (matchedRecipes !== undefined) {
        setImageProcessed(true);
      }
    }
  }, [loading, imageProcessed, matchedRecipes]);

  const cuisines = [
    'General',
    'Italian',
    'Chinese',
    'Indian',
    'Mexican',
    'Thai',
    'Japanese',
    'French',
    'Mediterranean',
    'American',
    'Korean',
    'Vietnamese',
    'Middle Eastern',
    'Greek',
    'Spanish'
  ];

  const handleFileUpload = (file) => {
    if (file) {
      setImageProcessed(false); // Reset flag
      dispatch(processImage(file));
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileUpload(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleAddManualIngredient = () => {
    if (manualIngredient.trim()) {
      dispatch(addIngredient(manualIngredient.trim()));
      setManualIngredient('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAddManualIngredient();
    }
  };

  const handleRemoveIngredient = (index) => {
    dispatch(removeIngredient(index));
  };

  const handleGenerateRecipe = async () => {
    if (detectedIngredients.length > 0) {
      await dispatch(generateRecipe({
        ingredients: detectedIngredients,
        cuisine: selectedCuisine
      }));
      navigate('/recipes');
    }
  };

  const handleGenerateSuggestions = async () => {
    if (detectedIngredients.length > 0) {
      await dispatch(generateRecipeSuggestions({
        ingredients: detectedIngredients,
        cuisine: selectedCuisine
      }));
      navigate('/recipes');
    }
  };

  const handleClearAll = () => {
    dispatch(clearIngredients());
  };

  return (
    <div className="ingredients-page">
      <div className="container">
        <h1 className="page-title">Add Your Ingredients</h1>

        <div className="cuisine-section">
          <h3>🍽️ Select Your Preferred Cuisine</h3>
          <p>Choose a cuisine style for your recipe</p>
          <select
            value={selectedCuisine}
            onChange={(e) => setSelectedCuisine(e.target.value)}
            className="cuisine-select"
          >
            {cuisines.map(cuisine => (
              <option key={cuisine} value={cuisine}>
                {cuisine}
              </option>
            ))}
          </select>
        </div>

        <div className="upload-section">
          <div className="upload-methods">
            <div className="upload-method">
              <h3>📸 Upload Photo</h3>
              <p>Upload an existing photo</p>
              <div
                className={`upload-area ${dragActive ? 'active' : ''}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => fileInputRef.current.click()}
              >
                <div className="upload-content">
                  <span className="upload-icon">📷</span>
                  <p>Click to upload or drag and drop</p>
                  <small>Supported formats: JPG, PNG</small>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
              </div>
            </div>

            <div className="upload-method">
              <h3>📷 Take Photo</h3>
              <p>Use your camera to capture ingredients</p>
              <div
                className="upload-area camera-area"
                onClick={() => setIsCameraOpen(true)}
              >
                <div className="upload-content">
                  <span className="upload-icon">📹</span>
                  <p>Click to open camera</p>
                  <small>Live camera capture</small>
                </div>
              </div>
            </div>

            <div className="upload-method">
              <h3>✏️ Manual Entry</h3>
              <p>Add ingredients one by one</p>
              <div className="manual-input">
                <input
                  type="text"
                  value={manualIngredient}
                  onChange={(e) => setManualIngredient(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Enter ingredient (e.g., tomatoes, onions)"
                  className="ingredient-input"
                />
                <button
                  onClick={handleAddManualIngredient}
                  className="btn btn-primary"
                  disabled={!manualIngredient.trim()}
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        </div>

        {loading && (
          <div className="loading-section">
            <div className="spinner"></div>
            <p>Analyzing your ingredients...</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            <span>⚠️</span> {error}
          </div>
        )}

        {!loading && !error && imageProcessed && detectedIngredients.length === 0 && (
          <div className="info-message">
            <span>📷</span> No ingredients were automatically detected from your image. Please add them manually below.
          </div>
        )}

        {detectedIngredients.length > 0 && (
          <div className="ingredients-list-section">
            <div className="ingredients-header">
              <h3>Detected Ingredients ({detectedIngredients.length})</h3>
              <button onClick={handleClearAll} className="btn btn-secondary">
                Clear All
              </button>
            </div>

            <div className="ingredients-list">
              {detectedIngredients.map((ingredient, index) => (
                <div key={index} className="ingredient-tag">
                  <span>{ingredient}</span>
                  <button
                    onClick={() => handleRemoveIngredient(index)}
                    className="remove-btn"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>

            <div className="action-buttons">
              <button
                onClick={handleGenerateRecipe}
                className="btn btn-primary btn-large"
                disabled={loading}
              >
                Generate Recipe
              </button>
              <button
                onClick={handleGenerateSuggestions}
                className="btn btn-secondary btn-large"
                disabled={loading}
              >
                Get Suggestions
              </button>
            </div>
          </div>
        )}

        <div className="tips-section">
          <h3>Tips for Better Results</h3>
          <ul>
            <li>Ensure good lighting when taking photos</li>
            <li>Place ingredients on a clean, contrasting background</li>
            <li>Try to capture multiple ingredients in one photo</li>
            <li>Manually add any ingredients that weren't detected</li>
          </ul>
        </div>
      </div>

      <CameraModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onCapture={handleFileUpload}
      />
    </div>
  );
};

export default Ingredients;

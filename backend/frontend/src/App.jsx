import React, { useState, useEffect } from 'react';
import ImageUploader from './components/ImageUploader';
import ResultCard from './components/ResultCard';
import { uploadImage, getAllRecipes } from './api';
import './styles.css';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [allRecipes, setAllRecipes] = useState([]);
  const [showBrowse, setShowBrowse] = useState(false);
  const [browseLoading, setBrowseLoading] = useState(false);

  const handleUpload = async (file) => {
    setUploadedImage(file);
    setLoading(true);
    try {
      const data = await uploadImage(file);
      console.log('API Response:', data); // Debug logging
      setResults(data);
    } catch (error) {
      console.error('Error uploading image:', error);
      alert('Failed to process image. Please try again. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const handleBrowseRecipes = async () => {
    if (allRecipes.length === 0) {
      setBrowseLoading(true);
      try {
        const data = await getAllRecipes();
        setAllRecipes(data.recipes || []);
      } catch (error) {
        console.error('Error fetching recipes:', error);
        alert('Failed to load recipes. Please try again.');
      } finally {
        setBrowseLoading(false);
      }
    }
    setShowBrowse(!showBrowse);
  };

  return (
    <div className="App">
      <h1>🍳 Intelligent Recipe Generator</h1>
      <p className="subtitle">
        <span className="highlight">✨ AI-Powered</span> • Upload a food image to discover ingredients and extract text using advanced machine learning
      </p>
      <ImageUploader onUpload={handleUpload} loading={loading} />
      {results && <ResultCard
        ingredients={results.ingredients}
        ocrText={results.ocr_text}
        image={uploadedImage}
        detectedItems={results.detected_items}
        matchingRecipes={results.matching_recipes}
        databaseStatus={results.database_status}
      />}

      {/* Browse Recipes Section */}
      <div className="browse-section">
        <button
          className="browse-button"
          onClick={handleBrowseRecipes}
          disabled={browseLoading}
        >
          {browseLoading ? 'Loading Recipes...' : showBrowse ? 'Hide Recipe Database' : 'Browse Recipe Database 📚'}
        </button>

        {showBrowse && (
          <div className="browse-recipes-container">
            <h3>🍳 Complete Recipe Database</h3>
            <p className="browse-description">
              Explore our collection of {allRecipes.length} recipes stored in the database.
              These recipes can be matched with ingredients detected from your uploaded images.
            </p>
            <div className="recipes-grid">
              {allRecipes.map((recipe, index) => (
                <div key={index} className="recipe-card">
                  <div className="recipe-header">
                    <h5>{recipe.title}</h5>
                    <div className="recipe-meta">
                      <span>⏱️ {recipe.prep_time + recipe.cook_time} mins</span>
                      <span>🍽️ {recipe.servings} servings</span>
                    </div>
                  </div>
                  <div className="recipe-description">
                    {recipe.description}
                  </div>
                  <div className="recipe-ingredients">
                    <strong>Ingredients:</strong>
                    <div className="ingredients-preview">
                      {recipe.ingredients.slice(0, 4).map((ing, i) => (
                        <span key={i} className="ingredient-preview">
                          {ing.quantity} {ing.unit} {ing.name}
                          {ing.notes && ` (${ing.notes})`}
                        </span>
                      ))}
                      {recipe.ingredients.length > 4 && (
                        <span className="more-ingredients">
                          +{recipe.ingredients.length - 4} more...
                        </span>
                      )}
                    </div>
                  </div>
                  {recipe.instructions && recipe.instructions.length > 0 && (
                    <div className="recipe-instructions">
                      <strong>Instructions:</strong>
                      <ol>
                        {recipe.instructions.slice(0, 2).map((step, i) => (
                          <li key={i}>{step.step_number}. {step.description}</li>
                        ))}
                        {recipe.instructions.length > 2 && (
                          <li>... and {recipe.instructions.length - 2} more steps</li>
                        )}
                      </ol>
                    </div>
                  )}
                  {recipe.nutrition && (
                    <div className="recipe-nutrition">
                      <strong>Nutrition (per serving):</strong>
                      <div className="nutrition-info">
                        {recipe.nutrition.calories && <span>{recipe.nutrition.calories} cal</span>}
                        {recipe.nutrition.protein && <span>{recipe.nutrition.protein}g protein</span>}
                        {recipe.nutrition.carbohydrates && <span>{recipe.nutrition.carbohydrates}g carbs</span>}
                        {recipe.nutrition.fat && <span>{recipe.nutrition.fat}g fat</span>}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <footer className="app-footer">
        <div className="footer-content">
          <div className="tech-stack">
            <span>🚀 Built with React & Flask</span>
            <span>🤖 Powered by AI/ML</span>
            <span>📷 Computer Vision</span>
          </div>
          <div className="footer-text">
            Transform your cooking experience with intelligent ingredient detection
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

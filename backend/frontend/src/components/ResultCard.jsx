import React from 'react';

const ResultCard = ({ ingredients, ocrText, image, detectedItems, matchingRecipes, databaseStatus }) => {
  return (
    <div className="result-card">
      <div className="ingredients-section">
        <h4>Detected Ingredients</h4>
        {ingredients && ingredients.length > 0 ? (
          <>
            <div className="ingredients-list">
              {ingredients.map((ingredient, index) => (
                <span key={index} className="ingredient-tag">
                  {ingredient}
                </span>
              ))}
            </div>
            {detectedItems && detectedItems.length > 0 && (
              <div className="detection-details">
                {detectedItems.map((item, index) => (
                  <div key={index} className="ingredient-card">
                    <div className="ingredient-name">{item.name}</div>
                    <div className="ingredient-confidence">
                      Confidence: {(item.confidence * 100).toFixed(1)}%
                    </div>
                    <div className="confidence-bar">
                      <div
                        className="confidence-fill"
                        style={{ width: `${item.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="no-ingredients-message">
            <p>No ingredients detected</p>
            <p className="help-text">
              For best results, upload images with visible text labels or ingredient names.
              The system works by reading text from images using OCR.
            </p>
          </div>
        )}
      </div>
      <div className="ocr-section">
        <h4>Extracted Text (OCR)</h4>
        <div className="ocr-text">{ocrText || 'No text detected'}</div>
      </div>
      {/* Database Matching Recipes Section */}
      {matchingRecipes && matchingRecipes.length > 0 && (
        <div className="matching-recipes-section">
          <h4>🍳 Matching Recipes from Database</h4>
          <div className="recipes-grid">
            {matchingRecipes.map((recipe, index) => (
              <div key={index} className="recipe-card">
                <div className="recipe-header">
                  <h5>{recipe.title}</h5>
                  <div className="recipe-meta">
                    <span>⏱️ {recipe.prep_time + recipe.cook_time} mins</span>
                    <span>🍽️ {recipe.servings} servings</span>
                    <span>🎯 Match: {(recipe.match_score * 100).toFixed(0)}%</span>
                  </div>
                </div>
                <div className="recipe-description">
                  {recipe.description}
                </div>
                <div className="recipe-ingredients">
                  <strong>Ingredients:</strong>
                  <div className="ingredients-preview">
                    {recipe.ingredients.slice(0, 5).map((ing, i) => (
                      <span key={i} className="ingredient-preview">
                        {ing.quantity} {ing.unit} {ing.name}
                        {ing.notes && ` (${ing.notes})`}
                      </span>
                    ))}
                    {recipe.ingredients.length > 5 && (
                      <span className="more-ingredients">
                        +{recipe.ingredients.length - 5} more...
                      </span>
                    )}
                  </div>
                </div>
                {recipe.instructions && recipe.instructions.length > 0 && (
                  <div className="recipe-instructions">
                    <strong>Instructions:</strong>
                    <ol>
                      {recipe.instructions.slice(0, 3).map((step, i) => (
                        <li key={i}>{step.step_number}. {step.description}</li>
                      ))}
                      {recipe.instructions.length > 3 && (
                        <li>... and {recipe.instructions.length - 3} more steps</li>
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

      {/* Database Status Section */}
      {databaseStatus && (
        <div className="database-status-section">
          <h4>📊 Database Status</h4>
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Total Recipes:</span>
              <span className="status-value">{databaseStatus.total_recipes}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Total Ingredients:</span>
              <span className="status-value">{databaseStatus.total_ingredients}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Total Instructions:</span>
              <span className="status-value">{databaseStatus.total_instructions}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Nutrition Entries:</span>
              <span className="status-value">{databaseStatus.total_nutrition_entries}</span>
            </div>
          </div>
          <div className="database-health">
            <span className={`status-indicator ${databaseStatus.total_recipes > 0 ? 'healthy' : 'error'}`}>
              {databaseStatus.total_recipes > 0 ? '🟢 Database Healthy' : '🔴 Database Empty'}
            </span>
          </div>
        </div>
      )}

      {image && (
        <div className="image-preview">
          <h4>Your Uploaded Image</h4>
          <img src={URL.createObjectURL(image)} alt="Uploaded food" className="uploaded-image" />
        </div>
      )}
    </div>
  );
};

export default ResultCard;

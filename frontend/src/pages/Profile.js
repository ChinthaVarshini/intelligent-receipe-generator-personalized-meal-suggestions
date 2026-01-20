import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { setUserProfile, updatePreferences, removeFromFavorites } from '../features/userSlice';
import './Profile.css';

const Profile = () => {
  const dispatch = useDispatch();
  const { profile, isAuthenticated } = useSelector(state => state.user);
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(searchParams.get('favorites') ? 'favorites' : 'preferences');
  const [favorites, setFavorites] = useState([]);
  const [cookingHistory, setCookingHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      fetchProfileData();
    }
  }, [isAuthenticated]);

  // Refresh favorites when favorites tab becomes active
  useEffect(() => {
    if (isAuthenticated && activeTab === 'favorites') {
      const refreshFavorites = async () => {
        try {
          const token = localStorage.getItem('token');
          const headers = {
            'Authorization': `Bearer ${token}`,
            'X-API-Key': 'intelligent-recipe-generator-api-key-2023'
          };

          const favoritesResponse = await fetch('/auth/favorites', { headers });
          if (favoritesResponse.ok) {
            const favoritesData = await favoritesResponse.json();
            setFavorites(favoritesData.favorites);
          }
        } catch (err) {
          console.error('Error refreshing favorites:', err);
        }
      };

      refreshFavorites();
    }
  }, [activeTab, isAuthenticated]);

  const fetchProfileData = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'X-API-Key': 'intelligent-recipe-generator-api-key-2023'
      };

      // Fetch profile
      const profileResponse = await fetch('/auth/profile', { headers });
      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        dispatch(setUserProfile(profileData.user));
        // Update preferences in Redux
        dispatch(updatePreferences(profileData.preferences));
      }

      // Fetch favorites
      const favoritesResponse = await fetch('/auth/favorites', { headers });
      if (favoritesResponse.ok) {
        const favoritesData = await favoritesResponse.json();
        setFavorites(favoritesData.favorites);
      }

      // Fetch cooking history
      const historyResponse = await fetch('/auth/cooking-history', { headers });
      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        setCookingHistory(historyData.history);
      }
    } catch (err) {
      setError('Failed to load profile data');
      console.error('Profile fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePreferenceChange = (preferenceType, value) => {
    const currentPrefs = profile.preferences[preferenceType] || [];
    const newPrefs = currentPrefs.includes(value)
      ? currentPrefs.filter(p => p !== value)
      : [...currentPrefs, value];

    dispatch(updatePreferences({ [preferenceType]: newPrefs }));
  };

  const handleRemoveFavorite = (recipeId) => {
    dispatch(removeFromFavorites(recipeId));
  };

  const handleRemoveFavoriteFromAPI = async (recipeId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/auth/favorites/${recipeId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-API-Key': 'intelligent-recipe-generator-api-key-2023'
        }
      });

      if (response.ok) {
        // Refresh favorites
        fetchProfileData();
      } else {
        setError('Failed to remove favorite');
      }
    } catch (err) {
      setError('Failed to remove favorite');
      console.error('Remove favorite error:', err);
    }
  };

  const dietaryOptions = ['Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 'Keto', 'Paleo'];
  const cuisineOptions = ['Italian', 'Chinese', 'Mexican', 'Indian', 'Japanese', 'Thai', 'French', 'Mediterranean'];
  const difficultyOptions = ['Easy', 'Medium', 'Hard'];

  return (
    <div className="profile-page">
      <div className="container">
        <h1 className="page-title">Profile</h1>

        <div className="profile-content">
          <div className="profile-tabs">
            <button
              className={`tab-button ${activeTab === 'preferences' ? 'active' : ''}`}
              onClick={() => setActiveTab('preferences')}
            >
              Preferences
            </button>
            <button
              className={`tab-button ${activeTab === 'favorites' ? 'active' : ''}`}
              onClick={() => setActiveTab('favorites')}
            >
              Favorites ({favorites.length})
            </button>
            <button
              className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              History ({cookingHistory.length})
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'preferences' && (
              <div className="preferences-tab">
                <h3>Cooking Preferences</h3>

                <div className="preference-section">
                  <h4>Dietary Preferences</h4>
                  <div className="preference-options">
                    {dietaryOptions.map(option => (
                      <label key={option} className="preference-option">
                        <input
                          type="checkbox"
                          checked={profile.preferences.dietary.includes(option)}
                          onChange={() => handlePreferenceChange('dietary', option)}
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="preference-section">
                  <h4>Favorite Cuisines</h4>
                  <div className="preference-options">
                    {cuisineOptions.map(option => (
                      <label key={option} className="preference-option">
                        <input
                          type="checkbox"
                          checked={profile.preferences.cuisine.includes(option)}
                          onChange={() => handlePreferenceChange('cuisine', option)}
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="preference-section">
                  <h4>Preferred Difficulty</h4>
                  <div className="preference-options">
                    {difficultyOptions.map(option => (
                      <label key={option} className="preference-option">
                        <input
                          type="radio"
                          name="difficulty"
                          value={option}
                          checked={profile.preferences.difficulty === option}
                          onChange={(e) => dispatch(updatePreferences({ difficulty: e.target.value }))}
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'favorites' && (
              <div className="favorites-tab">
                <h3>Favorite Recipes</h3>
                {favorites.length > 0 ? (
                  <div className="favorites-list">
                    {favorites.map(recipe => (
                      <div key={recipe.id} className="favorite-item">
                        <div className="favorite-info">
                          <h4>{recipe.title}</h4>
                          <p>{recipe.description}</p>
                          <div className="recipe-meta">
                            <span>🍳 {recipe.cuisine_type}</span>
                            <span>⚡ {recipe.difficulty_level}</span>
                            <span>⏱️ {recipe.total_time}min</span>
                          </div>
                        </div>
                        <button
                          onClick={() => handleRemoveFavoriteFromAPI(recipe.id)}
                          className="remove-btn"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <span className="empty-icon">❤️</span>
                    <p>No favorite recipes yet. Start exploring and save your favorites!</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'history' && (
              <div className="history-tab">
                <div className="history-header">
                  <h3>Cooking History</h3>
                </div>
                {cookingHistory.length > 0 ? (
                  <div className="history-list">
                    {cookingHistory.map((item) => (
                      <div key={item.id} className="history-item">
                        <div className="history-info">
                          <h4>{item.recipe_title}</h4>
                          <div className="recipe-meta">
                            <span>🍳 {item.cuisine_type}</span>
                            <span>⚡ {item.difficulty_level}</span>
                            {item.rating && <span>⭐ {item.rating}/5</span>}
                          </div>
                          <p className="cooked-date">
                            Cooked on {new Date(item.cooked_at).toLocaleDateString()}
                          </p>
                          {item.notes && <p className="notes">Notes: {item.notes}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <span className="empty-icon">👨‍🍳</span>
                    <p>Your cooking history will appear here as you cook recipes.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;

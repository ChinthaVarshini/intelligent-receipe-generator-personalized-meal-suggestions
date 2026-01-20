const API_BASE_URL = '';
const API_KEY = 'intelligent-recipe-generator-api-key-2023';

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/process-image`, {
      method: 'POST',
      headers: {
        'X-API-Key': API_KEY,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to process image');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error uploading image:', error);
    throw error;
  }
};

export const generateRecipe = async (ingredients) => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate-recipe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify({ ingredients }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to generate recipe');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating recipe:', error);
    throw error;
  }
};

export const generateRecipeSuggestions = async (ingredients, numRecipes = 3) => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate-recipe-suggestions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify({ ingredients, num_recipes: numRecipes }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to generate recipe suggestions');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating recipe suggestions:', error);
    throw error;
  }
};

export const getAllRecipes = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/get-all-recipes`, {
      method: 'GET',
      headers: {
        'X-API-Key': API_KEY,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch recipes');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching recipes:', error);
    throw error;
  }
};

export const findRecipes = async (ingredients) => {
  try {
    const response = await fetch(`${API_BASE_URL}/find-recipes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify({ ingredients }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to find recipes');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error finding recipes:', error);
    throw error;
  }
};

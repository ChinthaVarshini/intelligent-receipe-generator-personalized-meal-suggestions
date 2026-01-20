import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE_URL = '';

// Helper to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// Async thunks for API calls
export const fetchRecipes = createAsyncThunk(
  'recipes/fetchRecipes',
  async (params = {}) => {
    const response = await axios.get(`${API_BASE_URL}/get-all-recipes`, {
      headers: getAuthHeaders()
    });
    return response.data;
  }
);

export const searchRecipes = createAsyncThunk(
  'recipes/searchRecipes',
  async (searchParams) => {
    const response = await axios.post(`${API_BASE_URL}/search-recipes`, searchParams, {
      headers: { 
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      }
    });
    return response.data;
  }
);

export const generateRecipe = createAsyncThunk(
  'recipes/generateRecipe',
  async ({ ingredients, cuisine = 'General' }) => {
    const response = await axios.post(`${API_BASE_URL}/generate-recipe`,
      { ingredients, cuisine },
      {
        headers: { 
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      }
    );
    return response.data;
  }
);

export const generateRecipeSuggestions = createAsyncThunk(
  'recipes/generateRecipeSuggestions',
  async ({ ingredients, num_recipes = 3 }) => {
    const response = await axios.post(`${API_BASE_URL}/generate-recipe-suggestions`, 
      { ingredients, num_recipes }, 
      {
        headers: { 
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      }
    );
    return response.data;
  }
);

export const generateInstructions = createAsyncThunk(
  'recipes/generateInstructions',
  async (recipeData) => {
    const response = await axios.post(`${API_BASE_URL}/generate-instructions`, 
      recipeData, 
      {
        headers: { 
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      }
    );
    return response.data;
  }
);

const recipeSlice = createSlice({
  name: 'recipes',
  initialState: {
    recipes: [],
    currentRecipe: null,
    generatedRecipe: null,
    suggestions: [],
    instructions: [],
    loading: false,
    error: null,
    totalRecipes: 0,
    currentPage: 1,
    totalPages: 1,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentRecipe: (state, action) => {
      state.currentRecipe = action.payload;
    },
    setRecipes: (state, action) => {
      state.recipes = action.payload;
      state.totalRecipes = action.payload.length;
    },
    clearGeneratedRecipe: (state) => {
      state.generatedRecipe = null;
    },
    clearSuggestions: (state) => {
      state.suggestions = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch recipes
      .addCase(fetchRecipes.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchRecipes.fulfilled, (state, action) => {
        state.loading = false;
        state.recipes = action.payload.recipes;
        state.totalRecipes = action.payload.total_recipes;
      })
      .addCase(fetchRecipes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      // Search recipes
      .addCase(searchRecipes.pending, (state) => {
        state.loading = true;
      })
      .addCase(searchRecipes.fulfilled, (state, action) => {
        state.loading = false;
        state.recipes = action.payload.recipes;
        state.totalRecipes = action.payload.total_recipes;
        state.totalPages = action.payload.total_pages;
        state.currentPage = action.payload.current_page;
      })
      .addCase(searchRecipes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      // Generate recipe
      .addCase(generateRecipe.pending, (state) => {
        state.loading = true;
      })
      .addCase(generateRecipe.fulfilled, (state, action) => {
        state.loading = false;
        state.generatedRecipe = action.payload;
      })
      .addCase(generateRecipe.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      // Generate suggestions
      .addCase(generateRecipeSuggestions.pending, (state) => {
        state.loading = true;
      })
      .addCase(generateRecipeSuggestions.fulfilled, (state, action) => {
        state.loading = false;
        state.suggestions = action.payload.suggestions;
      })
      .addCase(generateRecipeSuggestions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      // Generate instructions
      .addCase(generateInstructions.pending, (state) => {
        state.loading = true;
      })
      .addCase(generateInstructions.fulfilled, (state, action) => {
        state.loading = false;
        state.instructions = action.payload.instructions;
      })
      .addCase(generateInstructions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { clearError, setCurrentRecipe, setRecipes, clearGeneratedRecipe, clearSuggestions } = recipeSlice.actions;
export default recipeSlice.reducer;

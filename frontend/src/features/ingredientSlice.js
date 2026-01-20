import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE_URL = '';
const API_KEY = 'intelligent-recipe-generator-api-key-2023';

export const processImage = createAsyncThunk(
  'ingredients/processImage',
  async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/process-image`, formData, {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }
);

export const findRecipes = createAsyncThunk(
  'ingredients/findRecipes',
  async (ingredients) => {
    const response = await axios.post(`${API_BASE_URL}/find-recipes`,
      { ingredients },
      {
        headers: { 'X-API-Key': API_KEY, 'Content-Type': 'application/json' }
      }
    );
    return response.data;
  }
);

const ingredientSlice = createSlice({
  name: 'ingredients',
  initialState: {
    detectedIngredients: [],
    uploadedImage: null,
    matchedRecipes: [],
    loading: false,
    error: null,
  },
  reducers: {
    setIngredients: (state, action) => {
      state.detectedIngredients = action.payload;
    },
    addIngredient: (state, action) => {
      state.detectedIngredients.push(action.payload);
    },
    removeIngredient: (state, action) => {
      state.detectedIngredients = state.detectedIngredients.filter(
        (_, index) => index !== action.payload
      );
    },
    clearIngredients: (state) => {
      state.detectedIngredients = [];
      state.uploadedImage = null;
      state.matchedRecipes = [];
    },
    clearError: (state) => {
      state.error = null;
    },
    setImageProcessed: (state, action) => {
      // This reducer can be used to track processing state if needed
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(processImage.pending, (state) => {
        state.loading = true;
      })
      .addCase(processImage.fulfilled, (state, action) => {
        state.loading = false;
        state.detectedIngredients = action.payload.ingredients;
        state.uploadedImage = action.payload.ocr_text;
        // Store both AI-generated and database recipes
        const aiRecipes = action.payload.ai_generated_recipes || [];
        const dbRecipes = action.payload.database_matching_recipes || [];
        state.matchedRecipes = [...aiRecipes, ...dbRecipes];
      })
      .addCase(processImage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(findRecipes.pending, (state) => {
        state.loading = true;
      })
      .addCase(findRecipes.fulfilled, (state, action) => {
        state.loading = false;
        state.matchedRecipes = action.payload.recipes || [];
      })
      .addCase(findRecipes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const {
  setIngredients,
  addIngredient,
  removeIngredient,
  clearIngredients,
  clearError
} = ingredientSlice.actions;

export default ingredientSlice.reducer;

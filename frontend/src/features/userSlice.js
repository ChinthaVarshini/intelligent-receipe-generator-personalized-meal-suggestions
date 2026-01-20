import { createSlice } from '@reduxjs/toolkit';

const userSlice = createSlice({
  name: 'user',
  initialState: {
    profile: {
      name: '',
      email: '',
      preferences: {
        dietary: [],
        cuisine: [],
        difficulty: 'Easy',
      },
      favorites: [],
      history: [],
    },
    isAuthenticated: false,
    loading: false,
    error: null,
  },
  reducers: {
    setUserProfile: (state, action) => {
      state.profile = { ...state.profile, ...action.payload };
      state.isAuthenticated = true;
    },
    updatePreferences: (state, action) => {
      state.profile.preferences = { ...state.profile.preferences, ...action.payload };
    },
    addToFavorites: (state, action) => {
      if (!state.profile.favorites.includes(action.payload)) {
        state.profile.favorites.push(action.payload);
      }
    },
    removeFromFavorites: (state, action) => {
      state.profile.favorites = state.profile.favorites.filter(
        id => id !== action.payload
      );
    },
    addToHistory: (state, action) => {
      state.profile.history.unshift(action.payload);
      // Keep only last 20 items
      state.profile.history = state.profile.history.slice(0, 20);
    },
    clearHistory: (state) => {
      state.profile.history = [];
    },
    logout: (state) => {
      state.profile = {
        name: '',
        email: '',
        preferences: {
          dietary: [],
          cuisine: [],
          difficulty: 'Easy',
        },
        favorites: [],
        history: [],
      };
      state.isAuthenticated = false;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setUserProfile,
  updatePreferences,
  addToFavorites,
  removeFromFavorites,
  addToHistory,
  clearHistory,
  logout,
  clearError
} = userSlice.actions;

export default userSlice.reducer;

import { configureStore } from '@reduxjs/toolkit';
import recipeReducer from './features/recipeSlice';
import ingredientReducer from './features/ingredientSlice';
import userReducer from './features/userSlice';

export const store = configureStore({
  reducer: {
    recipes: recipeReducer,
    ingredients: ingredientReducer,
    user: userReducer,
  },
});

export default store;

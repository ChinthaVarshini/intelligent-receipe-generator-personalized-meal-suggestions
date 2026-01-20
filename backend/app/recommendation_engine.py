"""
Content-Based and Collaborative Filtering Recommendation Engine
Implements TF-IDF cosine similarity and user-based/item-based collaborative filtering.
"""

import json
import math
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import numpy as np
from database_models import db, Recipe, Ingredient, RecipeRating, User, UserPreference
from ingredient_matcher import IngredientMatcher

class ContentBasedRecommender:
    """Content-based filtering using TF-IDF and cosine similarity"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
        self.recipe_vectors = None
        self.recipe_ids = []
        self.ingredient_matcher = IngredientMatcher()

    def _prepare_recipe_features(self, recipes):
        """Convert recipes to feature vectors for similarity calculation"""
        recipe_features = []

        for recipe in recipes:
            # Get ingredients
            ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()
            ingredient_texts = [ing.name.lower().strip() for ing in ingredients]

            # Create feature text combining ingredients and metadata
            feature_parts = []

            # Ingredient text
            feature_parts.append(' '.join(ingredient_texts))

            # Cuisine type
            if recipe.cuisine_type:
                feature_parts.append(f"cuisine_{recipe.cuisine_type}")

            # Difficulty level
            if recipe.difficulty_level:
                feature_parts.append(f"difficulty_{recipe.difficulty_level}")

            # Dietary preferences
            if recipe.dietary_preferences:
                try:
                    dietary_prefs = json.loads(recipe.dietary_preferences)
                    for pref in dietary_prefs:
                        feature_parts.append(f"dietary_{pref}")
                except:
                    pass

            # Cooking time category
            if recipe.total_time:
                if recipe.total_time <= 30:
                    feature_parts.append("quick_meal")
                elif recipe.total_time <= 60:
                    feature_parts.append("medium_meal")
                else:
                    feature_parts.append("long_meal")

            recipe_features.append(' '.join(feature_parts))

        return recipe_features

    def fit(self, recipes):
        """Fit the TF-IDF vectorizer on recipe data"""
        if not recipes:
            return

        self.recipe_ids = [recipe.id for recipe in recipes]
        recipe_features = self._prepare_recipe_features(recipes)

        # Fit and transform
        self.recipe_vectors = self.vectorizer.fit_transform(recipe_features)
        self.recipe_vectors = normalize(self.recipe_vectors, axis=1)  # L2 normalization

    def get_similar_recipes(self, recipe_id, top_n=10):
        """Get recipes similar to the given recipe"""
        if recipe_id not in self.recipe_ids or self.recipe_vectors is None:
            return []

        recipe_idx = self.recipe_ids.index(recipe_id)

        # Calculate cosine similarity
        similarities = cosine_similarity(
            self.recipe_vectors[recipe_idx:recipe_idx+1],
            self.recipe_vectors
        )[0]

        # Get top similar recipes (excluding itself)
        similar_indices = np.argsort(similarities)[::-1][1:top_n+1]

        similar_recipes = []
        for idx in similar_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                similar_recipes.append({
                    'recipe_id': self.recipe_ids[idx],
                    'similarity_score': float(similarities[idx])
                })

        return similar_recipes

    def recommend_by_ingredients(self, user_ingredients, user_preferences=None, top_n=10):
        """Recommend recipes based on available ingredients and user preferences"""
        try:
            recipes = Recipe.query.all()
            recommendations = []

            for recipe in recipes:
                # Get recipe ingredients
                recipe_ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()
                recipe_ingredient_names = [ing.name for ing in recipe_ingredients]

                # Calculate ingredient match
                match_result = self.ingredient_matcher.calculate_match_percentage(
                    user_ingredients, recipe_ingredient_names
                )

                # Skip recipes with low match percentage
                if match_result['match_percentage'] < 20:
                    continue

                # Calculate content similarity score
                similarity_score = 0
                if self.recipe_vectors is not None and recipe.id in self.recipe_ids:
                    # Create a temporary vector for user ingredients
                    user_features = ' '.join(user_ingredients).lower()
                    if user_preferences:
                        if user_preferences.get('cuisine_type'):
                            user_features += f" cuisine_{user_preferences['cuisine_type']}"
                        if user_preferences.get('dietary_preferences'):
                            for pref in user_preferences['dietary_preferences']:
                                user_features += f" dietary_{pref}"

                    user_vector = self.vectorizer.transform([user_features])
                    user_vector = normalize(user_vector, axis=1)

                    recipe_idx = self.recipe_ids.index(recipe.id)
                    similarity_score = cosine_similarity(
                        user_vector,
                        self.recipe_vectors[recipe_idx:recipe_idx+1]
                    )[0][0]

                # Combine scores (weighted average)
                ingredient_weight = 0.7
                content_weight = 0.3
                combined_score = (
                    match_result['match_percentage'] * ingredient_weight +
                    (similarity_score * 100) * content_weight
                )

                # Preference bonus
                preference_bonus = 0
                if user_preferences and recipe.dietary_preferences:
                    try:
                        recipe_prefs = json.loads(recipe.dietary_preferences)
                        user_prefs = user_preferences.get('dietary_preferences', [])
                        matching_prefs = set(recipe_prefs) & set(user_prefs)
                        preference_bonus = len(matching_prefs) * 5  # 5 points per matching preference
                    except:
                        pass

                final_score = combined_score + preference_bonus

                recommendations.append({
                    'recipe': recipe,
                    'match_percentage': match_result['match_percentage'],
                    'similarity_score': similarity_score,
                    'combined_score': final_score,
                    'preference_bonus': preference_bonus,
                    'matches': match_result['matches']
                })

            # Sort by combined score
            recommendations.sort(key=lambda x: x['combined_score'], reverse=True)

            return recommendations[:top_n]

        except Exception as e:
            print(f"Error in content-based recommendation: {e}")
            return []


class CollaborativeRecommender:
    """User-based and item-based collaborative filtering"""

    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.user_ids = []
        self.recipe_ids = []

    def _build_user_item_matrix(self):
        """Build user-item rating matrix"""
        # Get all ratings
        ratings = RecipeRating.query.all()

        if not ratings:
            return

        # Get unique users and recipes
        self.user_ids = list(set(r.user_id for r in ratings))
        self.recipe_ids = list(set(r.recipe_id for r in ratings))

        # Build matrix
        self.user_item_matrix = np.zeros((len(self.user_ids), len(self.recipe_ids)))

        user_to_idx = {user_id: idx for idx, user_id in enumerate(self.user_ids)}
        recipe_to_idx = {recipe_id: idx for idx, recipe_id in enumerate(self.recipe_ids)}

        for rating in ratings:
            user_idx = user_to_idx[rating.user_id]
            recipe_idx = recipe_to_idx[rating.recipe_id]
            self.user_item_matrix[user_idx, recipe_idx] = rating.rating

    def _calculate_user_similarity(self):
        """Calculate user-user similarity matrix using Pearson correlation"""
        if self.user_item_matrix is None:
            return

        n_users = len(self.user_ids)
        self.user_similarity_matrix = np.zeros((n_users, n_users))

        for i in range(n_users):
            for j in range(n_users):
                if i == j:
                    self.user_similarity_matrix[i, j] = 1.0
                else:
                    # Pearson correlation
                    user_i_ratings = self.user_item_matrix[i, :]
                    user_j_ratings = self.user_item_matrix[j, :]

                    # Find common rated items
                    common_items = (user_i_ratings > 0) & (user_j_ratings > 0)

                    if np.sum(common_items) < 2:  # Need at least 2 common ratings
                        self.user_similarity_matrix[i, j] = 0
                    else:
                        # Calculate Pearson correlation
                        ratings_i = user_i_ratings[common_items]
                        ratings_j = user_j_ratings[common_items]

                        mean_i = np.mean(ratings_i)
                        mean_j = np.mean(ratings_j)

                        numerator = np.sum((ratings_i - mean_i) * (ratings_j - mean_j))
                        denominator = np.sqrt(np.sum((ratings_i - mean_i)**2)) * \
                                    np.sqrt(np.sum((ratings_j - mean_j)**2))

                        if denominator > 0:
                            self.user_similarity_matrix[i, j] = numerator / denominator
                        else:
                            self.user_similarity_matrix[i, j] = 0

    def _calculate_item_similarity(self):
        """Calculate item-item similarity matrix using cosine similarity"""
        if self.user_item_matrix is None:
            return

        # Transpose matrix for item-based similarity
        item_user_matrix = self.user_item_matrix.T

        # Calculate cosine similarity between items
        self.item_similarity_matrix = cosine_similarity(item_user_matrix)
        self.item_similarity_matrix = normalize(self.item_similarity_matrix, axis=1)

    def fit(self):
        """Fit the collaborative filtering model"""
        self._build_user_item_matrix()
        self._calculate_user_similarity()
        self._calculate_item_similarity()

    def get_user_based_recommendations(self, user_id, top_n=10):
        """Get user-based collaborative filtering recommendations"""
        if self.user_item_matrix is None or user_id not in self.user_ids:
            return []

        user_idx = self.user_ids.index(user_id)

        # Find similar users
        user_similarities = self.user_similarity_matrix[user_idx, :]
        similar_users_indices = np.argsort(user_similarities)[::-1]

        recommendations = defaultdict(float)
        user_ratings = self.user_item_matrix[user_idx, :]

        # Aggregate predictions from similar users
        for sim_user_idx in similar_users_indices[:10]:  # Top 10 similar users
            if user_similarities[sim_user_idx] < 0.1:  # Skip dissimilar users
                continue

            sim_user_ratings = self.user_item_matrix[sim_user_idx, :]

            for recipe_idx in range(len(self.recipe_ids)):
                if user_ratings[recipe_idx] == 0 and sim_user_ratings[recipe_idx] > 0:
                    # Predict rating
                    predicted_rating = (user_similarities[sim_user_idx] * sim_user_ratings[recipe_idx])
                    recommendations[self.recipe_ids[recipe_idx]] += predicted_rating

        # Sort by predicted rating
        sorted_recommendations = sorted(recommendations.items(),
                                      key=lambda x: x[1], reverse=True)

        return [{'recipe_id': recipe_id, 'predicted_rating': rating}
                for recipe_id, rating in sorted_recommendations[:top_n]]

    def get_item_based_recommendations(self, user_id, top_n=10):
        """Get item-based collaborative filtering recommendations"""
        if self.user_item_matrix is None or user_id not in self.user_ids:
            return []

        user_idx = self.user_ids.index(user_id)
        user_ratings = self.user_item_matrix[user_idx, :]

        recommendations = defaultdict(float)

        # For each item the user has rated highly
        highly_rated_items = np.where(user_ratings >= 4)[0]  # Items rated 4 or 5

        for item_idx in highly_rated_items:
            # Find similar items
            similar_items = self.item_similarity_matrix[item_idx, :]
            similar_items_indices = np.argsort(similar_items)[::-1]

            for sim_item_idx in similar_items_indices[:5]:  # Top 5 similar items
                if user_ratings[sim_item_idx] == 0 and similar_items[sim_item_idx] > 0.1:
                    recommendations[self.recipe_ids[sim_item_idx]] += \
                        similar_items[sim_item_idx] * user_ratings[item_idx]

        # Sort by score
        sorted_recommendations = sorted(recommendations.items(),
                                      key=lambda x: x[1], reverse=True)

        return [{'recipe_id': recipe_id, 'score': score}
                for recipe_id, score in sorted_recommendations[:top_n]]


class HybridRecommender:
    """Combines content-based and collaborative filtering"""

    def __init__(self):
        self.content_recommender = ContentBasedRecommender()
        self.collaborative_recommender = CollaborativeRecommender()

    def fit(self, recipes):
        """Fit both recommendation models"""
        self.content_recommender.fit(recipes)
        self.collaborative_recommender.fit()

    def recommend(self, user_id=None, user_ingredients=None, user_preferences=None, top_n=10):
        """Get hybrid recommendations combining multiple approaches"""
        recommendations = []

        # Content-based recommendations (ingredient matching)
        if user_ingredients:
            content_recs = self.content_recommender.recommend_by_ingredients(
                user_ingredients, user_preferences, top_n=top_n
            )

            for rec in content_recs:
                recommendations.append({
                    'recipe': rec['recipe'],
                    'score': rec['combined_score'],
                    'method': 'content_based',
                    'details': {
                        'match_percentage': rec['match_percentage'],
                        'similarity_score': rec['similarity_score'],
                        'preference_bonus': rec['preference_bonus']
                    }
                })

        # Collaborative filtering (if user has rated recipes)
        if user_id:
            collab_user_recs = self.collaborative_recommender.get_user_based_recommendations(
                user_id, top_n=top_n//2
            )
            collab_item_recs = self.collaborative_recommender.get_item_based_recommendations(
                user_id, top_n=top_n//2
            )

            for rec in collab_user_recs + collab_item_recs:
                recipe = Recipe.query.get(rec['recipe_id'])
                if recipe:
                    score = rec.get('predicted_rating', rec.get('score', 0)) * 20  # Scale to 0-100
                    recommendations.append({
                        'recipe': recipe,
                        'score': score,
                        'method': 'collaborative',
                        'details': rec
                    })

        # Remove duplicates and sort by score
        seen_recipes = set()
        unique_recommendations = []

        for rec in recommendations:
            recipe_id = rec['recipe'].id
            if recipe_id not in seen_recipes:
                unique_recommendations.append(rec)
                seen_recipes.add(recipe_id)

        unique_recommendations.sort(key=lambda x: x['score'], reverse=True)

        return unique_recommendations[:top_n]

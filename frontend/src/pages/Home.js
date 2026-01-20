import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  console.log('Home component rendering'); // Debug log

  return (
    <div className="home-page">
      <div className="container">
        <div className="hero-section">
          <div className="hero-content">
            <div className="hero-badge">🍳 AI-Powered Recipe Generator</div>
            <h1 className="hero-title">Transform Your Ingredients into Culinary Masterpieces</h1>
            <p className="hero-description">
              Upload a photo of your ingredients or tell us what you have, and our AI will generate personalized recipes with step-by-step instructions.
            </p>
            <div className="hero-actions">
              <Link to="/ingredients" className="btn btn-primary btn-large">
                🚀 Get Started
              </Link>
              <Link to="/recipes" className="btn btn-secondary btn-large">
                📚 Browse Recipes
              </Link>
            </div>
          </div>
          <div className="hero-image">
            <div className="hero-emoji">🍳</div>
          </div>
        </div>

        <div className="features-section">
          <h2 className="section-title">Smart Recipe Generation</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📸</div>
              <h3>Image Recognition</h3>
              <p>Upload photos of your ingredients and let AI detect them automatically</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI-Powered Recipes</h3>
              <p>Get personalized recipe suggestions based on what you have</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">👤</div>
              <h3>User Profiles</h3>
              <p>Save favorites, track preferences, and build your cooking history</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;

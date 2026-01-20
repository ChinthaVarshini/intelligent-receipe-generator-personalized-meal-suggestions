import React, { useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout, setUserProfile } from '../features/userSlice';
import './Navbar.css';

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isAuthenticated, profile } = useSelector(state => state.user);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    dispatch(logout());
    navigate('/');
  };

  useEffect(() => {
    // Check authentication status on component mount
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (token && userData) {
      try {
        const user = JSON.parse(userData);
        dispatch(setUserProfile(user));
      } catch (error) {
        console.error('Error parsing user data:', error);
        handleLogout();
      }
    }
  }, [dispatch, handleLogout]);



  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          🍳 Recipe Generator
        </Link>
        <ul className="navbar-menu">
          <li className="navbar-item">
            <Link
              to="/"
              className={`navbar-link ${location.pathname === '/' ? 'active' : ''}`}
            >
              Home
            </Link>
          </li>
          <li className="navbar-item">
            <Link
              to="/ingredients"
              className={`navbar-link ${location.pathname === '/ingredients' ? 'active' : ''}`}
            >
              Ingredients
            </Link>
          </li>
          <li className="navbar-item">
            <Link
              to="/recipes"
              className={`navbar-link ${location.pathname === '/recipes' ? 'active' : ''}`}
            >
              Recipes
            </Link>
          </li>
          {isAuthenticated ? (
            <>
              <li className="navbar-item">
                <Link
                  to="/profile?favorites"
                  className={`navbar-link ${location.pathname === '/profile' && location.search === '?favorites' ? 'active' : ''}`}
                >
                  ❤️ Favorites
                </Link>
              </li>
              <li className="navbar-item">
                <Link
                  to="/profile"
                  className={`navbar-link ${location.pathname === '/profile' && !location.search ? 'active' : ''}`}
                >
                  Profile
                </Link>
              </li>
              <li className="navbar-item">
                <span className="navbar-user">
                  Welcome, {profile.first_name || profile.username}!
                </span>
              </li>
              <li className="navbar-item">
                <button
                  onClick={handleLogout}
                  className="navbar-logout-btn"
                >
                  Logout
                </button>
              </li>
            </>
          ) : (
            <li className="navbar-item">
              <Link
                to="/login"
                className={`navbar-link ${location.pathname === '/login' ? 'active' : ''}`}
              >
                Login
              </Link>
            </li>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;

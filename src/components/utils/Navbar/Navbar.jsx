// src/components/Navbar.js
import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  const isOnDashboard = location.pathname === '/login';

  // Different navigation items based on the current page
  const navItems = isOnDashboard ? [
    { title: 'Home', path: '/' },
    { title: 'Dashboard', path: '/login' },
    { title: 'Library', path: '/library' }
  ] : [
    { title: 'Home', path: '/' }
  ];

  const handleNavigation = (path) => {
    closeMenu();
    navigate(path);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand" onClick={closeMenu}>
          RecomMix
        </Link>

        <div className={`nav-menu ${isOpen ? 'active' : ''}`}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className="nav-item"
              onClick={closeMenu}
            >
              {item.title}
            </Link>
          ))}
          
          {!isOnDashboard && (
            <div className="nav-auth">
              <button 
                className="nav-button login-button" 
                onClick={() => handleNavigation('/login')}
              >
                Log In
              </button>
              <button 
                className="nav-button signup-button" 
                onClick={() => handleNavigation('/signup')}
              >
                Sign Up
              </button>
            </div>
          )}
        </div>

        <button 
          className="hamburger"
          onClick={toggleMenu}
          aria-label="Toggle navigation menu"
        >
          <span className={isOpen ? 'open' : ''}></span>
          <span className={isOpen ? 'open' : ''}></span>
          <span className={isOpen ? 'open' : ''}></span>
        </button>
      </div>
    </nav>
  );
};

export default Navbar;

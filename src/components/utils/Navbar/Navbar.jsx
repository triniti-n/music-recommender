// src/components/Navbar.js
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';
import Logout from '../LogoutButton/Logout';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  // Show nav items and hide login button on /search
  const isOnSearch = location.pathname === '/search';

  // Different navigation items based on the current page
  const navItems = isOnSearch ? [
    { title: 'Home', path: '/' },
    { title: 'Search', path: '/search' },
    { title: 'Library', path: '/library' }
  ] : [
    { title: 'Home', path: '/' }
  ];

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
          {/* Only show login button if not on search */}
          {!isOnSearch && (
            <div className="nav-auth">
              <a 
                className="nav-button login-button" 
                href="http://localhost:5000/login"
              >
                Log In
              </a>
            </div>
          )}
          {/* Only show logout button on search */}
          {isOnSearch && <Logout />}
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

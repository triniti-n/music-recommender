// src/components/Navbar.js
import React, { useState } from 'react';
import './Navbar.css';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="navigation">
      <div className="nav-container">
        <div className={`nav-items ${isOpen ? 'show' : ''}`}>
          <span className="nav-item">Log In</span>
          <span className="nav-item">Get Started</span>
        </div>
        <button className="toggle-button" onClick={toggleMenu}>
          <div className={`hamburger ${isOpen ? 'open' : ''}`}>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </button>
      </div>
    </div>
  );
};

export default Navbar;

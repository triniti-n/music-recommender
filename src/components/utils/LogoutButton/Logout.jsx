import React from 'react';
import './Logout.css';
import { FiLogOut } from 'react-icons/fi';

const Logout = () => {
  const handleLogout = () => {
    // Clear any local storage items
    localStorage.removeItem('spotify_access_token');

    // Redirect to the root URL
    window.location.href = "/";
  };

  return (
    <button className="logout-button" onClick={handleLogout}>
      <FiLogOut className="logout-icon" />
      Logout
    </button>
  );
};

export default Logout;
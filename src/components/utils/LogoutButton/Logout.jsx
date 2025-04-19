import React from 'react';
import './Logout.css';
import { FiLogOut } from 'react-icons/fi';

const Logout = () => {
  const handleLogout = () => {
    // Clear frontend session if needed (e.g., localStorage)
    window.location.href = "http://localhost:5000/logout"; // Force full page reload
  };

  return (
    <button className="logout-button" onClick={handleLogout}>
      <FiLogOut className="logout-icon" /> 
      Logout
    </button>
  );
};

export default Logout;
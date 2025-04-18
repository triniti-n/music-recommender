import React from 'react';
import './Logout.css';
import { FiLogOut } from 'react-icons/fi';

const Logout = () => {
  return (
    <a className="logout-button" href="http://localhost:5000/logout">
      <FiLogOut className="logout-icon" /> 
      Logout
    </a>
  );
};

export default Logout;


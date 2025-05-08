import React from 'react';
import './Logout.css';
import { FiLogOut } from 'react-icons/fi';
import { useAuth } from '../../../context/AuthContext';

const Logout = () => {
  const { logout } = useAuth();

  const handleLogout = async () => {
    try {
      // Call the backend logout endpoint to clear server-side session
      await fetch('/logout', {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Error logging out from server:', error);
    }

    // Clear all client-side storage
    sessionStorage.removeItem('spotify_access_token');
    sessionStorage.removeItem('currentPlaylist');

    // Also clear localStorage in case tokens were stored there previously
    localStorage.removeItem('spotify_access_token');
    localStorage.removeItem('currentPlaylist');

    // Clear all session storage
    sessionStorage.clear();

    // Use the AuthContext logout function to update auth state
    logout();

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
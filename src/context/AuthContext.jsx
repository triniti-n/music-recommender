import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [accessToken, setAccessToken] = useState(null);

  useEffect(() => {
    // Check if user is authenticated on mount
    const token = sessionStorage.getItem('spotify_access_token');
    if (token) {
      setIsAuthenticated(true);
      setAccessToken(token);
    }
  }, []);

  const login = (token) => {
    // Use sessionStorage instead of localStorage for non-permanent storage
    sessionStorage.setItem('spotify_access_token', token);
    setIsAuthenticated(true);
    setAccessToken(token);
  };

  const logout = () => {
    // Clear all authentication-related data
    sessionStorage.removeItem('spotify_access_token');
    sessionStorage.removeItem('currentPlaylist');

    // Clear any localStorage items that might have been set previously
    localStorage.removeItem('spotify_access_token');
    localStorage.removeItem('currentPlaylist');

    // Clear all session storage
    sessionStorage.clear();

    // Clear cookies by setting their expiration date to the past
    document.cookie.split(";").forEach(function(c) {
      document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });

    // Update authentication state
    setIsAuthenticated(false);
    setAccessToken(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, accessToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
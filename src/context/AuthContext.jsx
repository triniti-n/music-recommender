import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [accessToken, setAccessToken] = useState(null);

  useEffect(() => {
    // Check if user is authenticated on mount
    const token = localStorage.getItem('spotify_access_token');
    if (token) {
      setIsAuthenticated(true);
      setAccessToken(token);
    }
  }, []);

  const login = (token) => {
    localStorage.setItem('spotify_access_token', token);
    setIsAuthenticated(true);
    setAccessToken(token);
  };

  const logout = () => {
    localStorage.removeItem('spotify_access_token');
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
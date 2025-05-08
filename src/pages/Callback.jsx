import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

// This component handles authentication redirects (e.g., from Spotify)
const Callback = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Example: Parse query/hash params for access token
    const params = new URLSearchParams(location.search || location.hash.replace('#', '?'));
    const accessToken = params.get('access_token');
    const error = params.get('error');

    if (accessToken) {
      // Store token in sessionStorage (not localStorage) for non-permanent storage
      sessionStorage.setItem('spotify_access_token', accessToken);
      navigate('/search'); // Redirect to search page
    } else if (error) {
      // Handle error
      alert('Authentication failed: ' + error);
      navigate('/');
    }
    // Add more logic as needed for your app
  }, [location, navigate]);

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h2>Processing authentication...</h2>
      <p>If you are not redirected automatically, please wait or return to the home page.</p>
    </div>
  );
};

export default Callback;

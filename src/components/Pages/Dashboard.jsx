import React from 'react';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
      </div>
      <div className="dashboard-content">
        <div className="recommendations-section">
          <h2>Recommendations</h2>
          <div className="music-grid">
            <div className="music-card">
              <h3>Track 1</h3>
              <p>Artist 1</p>
            </div>
            <div className="music-card">
              <h3>Track 2</h3>
              <p>Artist 2</p>
            </div>
          </div>
        </div>
        <div className="preferences-section">
          <h2>Preferences</h2>
          <div className="genre-tags">
            <span className="tag">Genre 1</span>
            <span className="tag">Genre 2</span>
            <span className="tag">Genre 3</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
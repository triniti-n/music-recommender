import React, { useState } from 'react';
import './Dashboard.css';

const Dashboard = () => {
  const [inputs, setInputs] = useState(['', '', '', '', '']);

  const handleInputChange = (index, value) => {
    const newInputs = [...inputs];
    newInputs[index] = value;
    setInputs(newInputs);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle submission of songs/artists
    console.log('Submitted songs/artists:', inputs);
  };

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
          <div className="input-section">
            <h3>Enter Your Favorite Songs or Artists</h3>
            <form onSubmit={handleSubmit}>
              {inputs.map((input, index) => (
                <div key={index} className="input-group">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => handleInputChange(index, e.target.value)}
                    placeholder={`Song or Artist ${index + 1}`}
                    className="music-input"
                  />
                </div>
              ))}
              <button type="submit" className="submit-button">
                Get Recommendations
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
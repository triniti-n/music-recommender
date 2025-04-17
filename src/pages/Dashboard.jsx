import React, { useState } from 'react';
import './Dashboard.css';
import MusicCard from '../components/utils/MusicCard/MusicCard';

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
            <MusicCard title="Track 1" artist="Artist 1" />
            <MusicCard title="Track 2" artist="Artist 2" />
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
// src/components/utils/Hero/Hero.jsx
import React from 'react';
import './Hero.css';
import spotifyIcon from '../../assets/icons/spotify-icon.png';

const Hero = () => {
  return (
    <div className="hero">
      <div className="title-section">
        <span className="title">{"Discover new music for your playlist"}</span>
        <span className="subtitle">
          {"Unlock fresh tracks that match your vibe. Whether you're chilling, working out, or vibing through your day—our smart recommender curates the perfect playlist based on your taste."}
        </span>
      </div>
      <div className="spotify-connect">
        <a href="http://localhost:5000/login" className="spotify-button">
          <img
            src={spotifyIcon}
            alt="Spotify icon"
            className="spotify-icon"
          />
          <span className="spotify-text">{"Connect with Spotify"}</span>
        </a>
      </div>
    </div>
  );
};

export default Hero;

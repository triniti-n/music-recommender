// src/components/Hero.js
import React from 'react';
import './Hero.css';

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
        <div className="spotify-button">
          <img
            src="/icons/spotify-icon.png"
            alt="Spotify icon"
            className="spotify-icon"
          />
          <span className="spotify-text">{"Connect with Spotify"}</span>
        </div>
      </div>
    </div>
  );
};

export default Hero;

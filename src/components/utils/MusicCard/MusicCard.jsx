import React from 'react';
import './MusicCard.css';

const MusicCard = ({ title, artist, cover, children }) => {
  return (
    <div className="music-card">
      {cover && <img src={cover} alt={title} className="music-card-cover" />}
      <h3>{title}</h3>
      <p>{artist}</p>
      {children}
    </div>
  );
};

export default MusicCard;

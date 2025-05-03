import React from 'react';
import './SongList.css';

const SongList = ({ songs, currentSongIndex, onSongSelect }) => {
  return (
    <div className="song-list">
      <h3 className="song-list-title">Songs</h3>
      <div className="song-list-container">
        {songs.map((song, index) => (
          <div 
            key={song.id} 
            className={`song-item ${index === currentSongIndex ? 'active' : ''}`}
            onClick={() => onSongSelect(index)}
          >
            <div className="song-item-left">
              <img 
                src={song.cover} 
                alt={`${song.title} cover`} 
                className="song-cover"
              />
              <div className="song-info">
                <h4 className="song-title">{song.title}</h4>
                <p className="song-artist">{song.artist}</p>
              </div>
            </div>
            <div className="song-duration">{song.duration}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SongList;

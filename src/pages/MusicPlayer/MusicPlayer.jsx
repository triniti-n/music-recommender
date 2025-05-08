import React, { useState, useRef, useEffect } from 'react';
import { FaPlay, FaPause, FaStepForward, FaStepBackward } from 'react-icons/fa';
import SongList from './SongList';
import './MusicPlayer.css';

// Default songs to use if no playlist is passed
const defaultSongs = [
  {
    id: 1,
    title: 'Bohemian Rhapsody',
    artist: 'Queen',
    album: 'A Night at the Opera',
    cover: 'https://upload.wikimedia.org/wikipedia/en/4/4d/Queen_A_Night_At_The_Opera.png',
    duration: '5:55',
    url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'
  },
  {
    id: 2,
    title: 'Hotel California',
    artist: 'Eagles',
    album: 'Hotel California',
    cover: 'https://upload.wikimedia.org/wikipedia/en/4/49/Hotelcalifornia.jpg',
    duration: '6:30',
    url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3'
  },
  {
    id: 3,
    title: 'Imagine',
    artist: 'John Lennon',
    album: 'Imagine',
    cover: 'https://upload.wikimedia.org/wikipedia/en/6/69/ImagineCover.jpg',
    duration: '3:03',
    url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3'
  },
  {
    id: 4,
    title: 'Billie Jean',
    artist: 'Michael Jackson',
    album: 'Thriller',
    cover: 'https://upload.wikimedia.org/wikipedia/en/5/55/Michael_Jackson_-_Thriller.png',
    duration: '4:54',
    url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3'
  },
  {
    id: 5,
    title: 'Sweet Child O\' Mine',
    artist: 'Guns N\' Roses',
    album: 'Appetite for Destruction',
    cover: 'https://upload.wikimedia.org/wikipedia/en/6/60/GunsnRosesAppetiteforDestructionalbumcover.jpg',
    duration: '5:56',
    url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3'
  }
];

const MusicPlayer = () => {
  // Initialize state
  const [songs, setSongs] = useState(defaultSongs);
  const [playlistName, setPlaylistName] = useState('My Playlist');
  const [playlistId, setPlaylistId] = useState(null);
  const [currentSongIndex, setCurrentSongIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const audioRef = useRef(null);
  const progressRef = useRef(null);

  // Load songs from sessionStorage or fetch from API
  useEffect(() => {
    const loadSongs = async () => {
      // First try to load from sessionStorage
      const savedPlaylist = sessionStorage.getItem('currentPlaylist');
      if (savedPlaylist) {
        try {
          const playlist = JSON.parse(savedPlaylist);
          if (playlist.songs && playlist.songs.length > 0) {
            setSongs(playlist.songs);
            setPlaylistName(playlist.name || 'My Playlist');

            // Set playlist ID if available
            if (playlist.id) {
              setPlaylistId(playlist.id);
              console.log('Loaded playlist with ID:', playlist.id);
            }

            // Clear sessionStorage to avoid reloading the same playlist on refresh
            sessionStorage.removeItem('currentPlaylist');
            return; // Exit if we successfully loaded from localStorage
          }
        } catch (error) {
          console.error('Error parsing playlist from localStorage:', error);
        }
      }

      // If no songs in localStorage, fetch from the selections API
      try {
        const response = await fetch('http://localhost:5000/api/search/selections', {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error('Failed to fetch selections');
        }

        const data = await response.json();
        if (data.songs && data.songs.length > 0) {
          setSongs(data.songs);
          setPlaylistName(data.name || 'My Selected Songs');
          console.log('Loaded songs from selections API:', data.songs.length);
        }
      } catch (error) {
        console.error('Error fetching selections:', error);
      }
    };

    loadSongs();
  }, []);

  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.play().catch(error => {
          console.error('Error playing audio:', error);
          setIsPlaying(false);
        });
      } else {
        audioRef.current.pause();
      }
    }
  }, [isPlaying, currentSongIndex]);

  useEffect(() => {
    const audio = audioRef.current;

    const updateProgress = () => {
      if (audio) {
        const progressValue = (audio.currentTime / audio.duration) * 100;
        setProgress(progressValue || 0);
      }
    };

    const handleSongEnd = () => {
      handleNext();
    };

    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('ended', handleSongEnd);

    return () => {
      audio.removeEventListener('timeupdate', updateProgress);
      audio.removeEventListener('ended', handleSongEnd);
    };
  }, [currentSongIndex]);

  const handlePlay = () => {
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  const handlePrevious = () => {
    setCurrentSongIndex(prevIndex =>
      prevIndex === 0 ? songs.length - 1 : prevIndex - 1
    );
    setIsPlaying(true);
  };

  const handleNext = () => {
    setCurrentSongIndex(prevIndex =>
      prevIndex === songs.length - 1 ? 0 : prevIndex + 1
    );
    setIsPlaying(true);
  };

  const handleProgressChange = (e) => {
    const newProgress = e.target.value;
    setProgress(newProgress);

    if (audioRef.current) {
      audioRef.current.currentTime = (newProgress / 100) * audioRef.current.duration;
    }
  };

  const handleSongSelect = (index) => {
    setCurrentSongIndex(index);
    setIsPlaying(true);
  };

  const formatTime = (time) => {
    if (!time) return '0:00';

    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  const currentSong = songs[currentSongIndex];

  return (
    <div className="music-player-page">
      <div className="music-player-container">
        <div className="music-player-left">
          <div className="player-info">
            <h2 className="playlist-title">{playlistName}</h2>
            {playlistId && (
              <div className="playlist-id">
                <small>Playlist ID: {playlistId}</small>
              </div>
            )}
            <img
              src={currentSong.cover}
              alt={`${currentSong.title} cover`}
              className="current-song-cover"
            />
            <div className="song-details">
              <h3>{currentSong.title}</h3>
              <p>{currentSong.artist}</p>
            </div>
          </div>

          <div className="player-progress">
            <span className="time-current">
              {audioRef.current ? formatTime(audioRef.current.currentTime) : '0:00'}
            </span>
            <input
              type="range"
              min="0"
              max="100"
              value={progress}
              onChange={handleProgressChange}
              className="progress-bar"
              ref={progressRef}
            />
            <span className="time-total">
              {currentSong.duration}
            </span>
          </div>

          <div className="player-controls">
            <button onClick={handlePrevious} className="control-button">
              <FaStepBackward />
            </button>
            {isPlaying ? (
              <button onClick={handlePause} className="control-button play-pause">
                <FaPause />
              </button>
            ) : (
              <button onClick={handlePlay} className="control-button play-pause">
                <FaPlay />
              </button>
            )}
            <button onClick={handleNext} className="control-button">
              <FaStepForward />
            </button>
          </div>

          <audio
            ref={audioRef}
            src={currentSong.url}
            preload="metadata"
          />
        </div>

        <div className="music-player-right">
          <SongList
            songs={songs}
            currentSongIndex={currentSongIndex}
            onSongSelect={handleSongSelect}
          />
        </div>
      </div>
    </div>
  );
};

export default MusicPlayer;

import React, { Component } from 'react';
import { Card, Input, List, Avatar, Tag, Empty, Button, message } from 'antd';
import './Search.css';

const { Search } = Input;

class Dashboard extends Component {
  constructor() {
    super();
    this.state = {
      searchResults: [],
      selectedSeeds: [], // saves selected artists or tracks
      searchValue: '',
      noResults: false, // flag for no results
      isCreatingPlaylist: false // flag for playlist creation in progress
    };
    this.debounceTimeout = null;
  }

  componentDidMount() {
    // No authentication check needed for public search
  }

  // Debounced search for better UX
  handleInputChange = (e) => {
    const value = e.target.value;
    this.setState({ searchValue: value });
    clearTimeout(this.debounceTimeout);
    this.debounceTimeout = setTimeout(() => {
      if (value.trim()) {
        this.getSearchResults(value);
      }
    }, 400);
  };

  // Add selected item to the tag list
  handleSelectItem = (item) => {
    const id = item.uri || item.id;
    
    // Check if item is already selected
    if (this.state.selectedSeeds.some(i => (i.uri || i.id) === id)) {
      return;
    }
    
    // Check if we've reached the maximum number of selections
    if (this.state.selectedSeeds.length >= 10) {
      message.warning('You can only select up to 10 items');
      return;
    }
    
    // Add the item to selections
    this.setState(prevState => ({
      selectedSeeds: [...prevState.selectedSeeds, item]
    }));
  };

  // Remove a tag
  handleCloseTag = (item) => {
    const id = item.uri || item.id;
    this.setState(prevState => ({
      selectedSeeds: prevState.selectedSeeds.filter(i => (i.uri || i.id) !== id)
    }));
  };

  // Called on search button click or enter press
  handleSearch = (value) => {
    if (!value) return;
    this.setState({ searchValue: value });
    this.getSearchResults(value, true); // force search and show no results if needed
  };

  // Create a playlist from selected seeds
  handleCreatePlaylist = () => {
    const { selectedSeeds } = this.state;
    
    if (selectedSeeds.length < 10) {
      message.warning('Please select at least 10 tracks or artists');
      return;
    }
    
    this.setState({ isCreatingPlaylist: true });
    
    // Extract track IDs and artist IDs from selected seeds
    const trackIds = selectedSeeds
      .filter(item => item.type === 'track')
      .map(track => track.id);
    
    const artistIds = selectedSeeds
      .filter(item => item.type === 'artist')
      .map(artist => artist.id);
    
    // Create playlist with selected tracks and artists
    fetch('http://localhost:5000/api/playlists/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        name: 'My Music Recommender Playlist',
        public: true,
        tracks: trackIds,
        artists: artistIds
      })
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to create playlist');
        }
        return response.json();
      })
      .then(playlist => {
        // Show success message with link to the playlist
        message.success(
          <div>
            <p>Playlist created successfully!</p>
            <a 
              href={playlist.external_urls?.spotify || `https://open.spotify.com/playlist/${playlist.id}`} 
              target="_blank" 
              rel="noopener noreferrer"
            >
              Open in Spotify
            </a>
          </div>
        );
        
        console.log('Created playlist:', playlist);
        
        // Clear selections after successful playlist creation
        this.setState({ 
          selectedSeeds: [],
          isCreatingPlaylist: false
        });
      })
      .catch(error => {
        console.error('Error creating playlist:', error);
        message.error('Failed to create playlist. Please try again.');
        this.setState({ isCreatingPlaylist: false });
      });
  };

  getSearchResults(query, forceShowNoResults = false) {
    if (!query) {
      this.setState({ searchResults: [], noResults: false });
      return;
    }
    
    console.log('Searching for:', query); // Debug log
    
    fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(query)}&type=track,artist`, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
      .then(response => {
        if (!response.ok) {
          throw Error('Response Not Ok');
        }
        return response.json();
      })
      .then(({ tracks, artists }) => {
        console.log('Search response:', { tracks, artists }); // Debug log
        
        const trackResults = (tracks?.items || []).map(track => ({
          ...track,
          type: 'track',
          display: track.name + ' - ' + track.artists.map(a => a.name).join(', '),
          avatar: track.album.images[0]?.url
        }));
        
        const artistResults = (artists?.items || []).map(artist => ({
          ...artist,
          type: 'artist',
          display: artist.name,
          avatar: artist.images[0]?.url
        }));
        
        const allResults = [...trackResults, ...artistResults];
        console.log('Processed results:', allResults); // Debug log
        
        this.setState({
          searchResults: allResults,
          noResults: forceShowNoResults && allResults.length === 0
        });
      })
      .catch(error => {
        console.error('Search error:', error);
        this.setState({ searchResults: [], noResults: forceShowNoResults });
      });
  }

  render() {
    const { searchResults, selectedSeeds, searchValue, noResults, isCreatingPlaylist } = this.state;
    const hasExactlyTenSelections = selectedSeeds.length === 10;
    const hasReachedMaxSelections = selectedSeeds.length === 10;
    
    let card;
    if (noResults) {
      card = <Empty description="No results found" style={{ marginTop: 20 }} />;
    } else if (searchResults.length > 0) {
      card = (
        <Card style={{ marginTop: 20 }}>
          {hasReachedMaxSelections && (
            <div className="max-selections-message">
              <p>You've reached the maximum of 10 selections. Remove some to add more.</p>
            </div>
          )}
          <div className="search-results-scroll">
            <List
              itemLayout="horizontal"
              dataSource={searchResults}
              renderItem={item => (
                <List.Item
                  key={item.uri || item.id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => this.handleSelectItem(item)}
                >
                  <List.Item.Meta
                    avatar={<Avatar shape="square" size="large" src={item.avatar} />}
                    title={<p>{item.display}</p>}
                    description={item.type === 'artist' ? 'Artist' : 'Track'}
                  />
                </List.Item>
              )}
            />
          </div>
        </Card>
      );
    } else {
      card = <Card hidden={true} />;
    }
    
    return (
      <div className="dashboard">
        <div className="dashboard-content">
          <div className="search-section">
            <h2>Add 10 Songs or Artists</h2>
            <div className="search-container">
              <Search
                placeholder="Type a song or artist name..."
                enterButton="Search"
                size="large"
                value={searchValue}
                onChange={this.handleInputChange}
                onSearch={(value) => this.handleSearch(value)}
                allowClear
              />
              {/* Display selected tags */}
              <div className="selected-seeds-container">
                {selectedSeeds.map(item => (
                  <Tag
                    key={item.uri || item.id}
                    closable
                    onClose={() => this.handleCloseTag(item)}
                    color={item.type === 'artist' ? 'blue' : 'green'}
                    style={{ fontSize: 16, padding: '4px 12px', margin: 4 }}
                  >
                    {item.display}
                  </Tag>
                ))}
              </div>
              
              {/* Selection counter or Create Playlist button */}
              <div className="selection-counter">
                {hasExactlyTenSelections ? (
                  <Button 
                    type="primary" 
                    size="large" 
                    onClick={this.handleCreatePlaylist}
                    loading={isCreatingPlaylist}
                    disabled={isCreatingPlaylist}
                    className="create-playlist-button"
                  >
                    Create Playlist
                  </Button>
                ) : (
                  <p>{selectedSeeds.length}/10 selections</p>
                )}
              </div>
              
              {card}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Dashboard;
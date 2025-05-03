import React, { Component } from 'react';
import { Card, Input, List, Avatar, Tag, Empty, Button, message, Modal, Form } from 'antd';
import './SearchPage.css';

const { Search } = Input;

class Dashboard extends Component {
  constructor() {
    super();
    this.state = {
      searchResults: [],
      selectedSeeds: [], // saves selected artists or tracks
      searchValue: '',
      noResults: false, // flag for no results
      isCreatingPlaylist: false, // flag for playlist creation in progress
      isModalVisible: false, // flag for playlist name modal visibility
      playlistName: 'My Playlist' // default playlist name
    };
    this.debounceTimeout = null;
    this.formRef = React.createRef();
  }

  componentDidMount() {
    // Get search query from URL if it exists
    const searchParams = new URLSearchParams(window.location.search);
    const query = searchParams.get('q');
    if (query) {
      this.setState({ searchValue: query }, () => {
        this.getSearchResults(query, true);
      });
    }
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
  async handleSelectItem(item) {
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

    try {
      // Add the item to selections
      this.setState(prevState => ({
        selectedSeeds: [...prevState.selectedSeeds, item]
      }));

      // Get the current search query from state
      const searchQuery = this.state.searchValue;

      // Prepare the selection data with only necessary fields
      const selectionData = {
        id: item.id,
        type: item.type,
        display: item.display,
        fullDisplay: item.fullDisplay || item.display,
        artistNames: item.artistNames,
        avatar: item.avatar,
        uri: item.uri
      };

      // Send selection to server with search query
      const response = await fetch('/api/search/selections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          action: 'add',
          selections: [selectionData],
          searchQuery: searchQuery
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save selection');
      }

      message.success('Selection saved successfully');
    } catch (error) {
      message.error('Failed to save selection');
      console.error('Error saving selection:', error);
    }
  };

  async handleCloseTag(item) {
    const id = item.uri || item.id;

    try {
      // Remove the item from selections
      this.setState(prevState => ({
        selectedSeeds: prevState.selectedSeeds.filter(i => (i.uri || i.id) !== id)
      }));

      // Send removal to server using DELETE request
      const response = await fetch(`/api/search/selections/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to remove selection');
      }

      message.success('Selection removed successfully');
    } catch (error) {
      message.error('Failed to remove selection');
      console.error('Error removing selection:', error);
    }
  }

  // This method was removed to fix the duplicate handleCloseTag ESLint error
  // The async handleCloseTag method above handles both UI state and server communication

  // Called on search button click or enter press
  handleSearch = async (value) => {
    if (!value) return;

    try {
      // Notify the server about a new search but don't reset selections
      await fetch('/api/search/new', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          query: value,
          keepSelections: true // Indicate to keep selections
        })
      });

      // Update search value but keep selections
      this.setState({
        searchValue: value
        // No longer resetting selectedSeeds here
      });

      // Update URL with search query
      const searchParams = new URLSearchParams(window.location.search);
      searchParams.set('q', value);
      window.history.pushState({}, '', `${window.location.pathname}?${searchParams.toString()}`);

      // Perform the search
      this.getSearchResults(value, true); // force search and show no results if needed
    } catch (error) {
      console.error('Error starting new search:', error);
      // Continue with search even if the API call failed
      this.setState({ searchValue: value });
      this.getSearchResults(value, true);
    }
  };

  // Show modal to enter playlist name
  showPlaylistNameModal = () => {
    const { selectedSeeds } = this.state;

    if (selectedSeeds.length < 10) {
      message.warning('Please select at least 10 tracks');
      return;
    }

    this.setState({
      isModalVisible: true,
      playlistName: 'My Playlist' // Reset to default name
    });
  };

  // Handle modal cancel
  handleModalCancel = () => {
    this.setState({ isModalVisible: false });
  };

  // Handle playlist name change
  handlePlaylistNameChange = (e) => {
    this.setState({ playlistName: e.target.value });
  };

  // Create a playlist from selected seeds
  handleCreatePlaylist = () => {
    const { selectedSeeds, playlistName } = this.state;

    // Close the modal
    this.setState({
      isModalVisible: false,
      isCreatingPlaylist: true
    });

    // Extract track IDs from selected seeds
    const trackIds = selectedSeeds.map(track => track.id);

    // Format the selected songs for the music player
    const formattedSongs = selectedSeeds.map(track => ({
      id: track.id,
      title: track.display,
      artist: track.artistNames || 'Unknown Artist',
      album: 'Unknown Album',
      cover: track.avatar || 'https://via.placeholder.com/300',
      duration: '3:30', // Default duration
      url: `https://open.spotify.com/track/${track.id}`
    }));

    // Save the formatted songs to localStorage for the music player
    localStorage.setItem('currentPlaylist', JSON.stringify({
      name: playlistName,
      songs: formattedSongs
    }));

    // Create playlist directly without token verification
    fetch('http://localhost:5000/api/playlists/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        name: playlistName,
        public: true,
        tracks: trackIds,
        artists: []
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

        // Navigate to music player page to play the newly created playlist
        window.location.href = '/player';
      })
      .catch(error => {
        console.error('Error creating playlist:', error);
        message.error('Failed to create playlist. Please try again.');
        this.setState({ isCreatingPlaylist: false });
      });
  };

  // This method has been removed as per requirements
  // Songs are now only played when a playlist is created

  getSearchResults(query, forceShowNoResults = false) {
    if (!query) {
      this.setState({ searchResults: [], noResults: false });
      return;
    }

    console.log('Searching for:', query); // Debug log

    fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(query)}&type=track`, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      credentials: 'include'
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
          display: track.name, // Track name for the tag display
          fullDisplay: `${track.name} - ${track.artists.map(a => a.name).join(', ')}`, // Full display with artist for search results
          artistNames: track.artists.map(a => a.name).join(', '), // Artist names for description
          avatar: track.album.images[0]?.url
        }));

        const allResults = [...trackResults];
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
    const {
      searchResults,
      selectedSeeds,
      searchValue,
      noResults,
      isCreatingPlaylist,
      isModalVisible,
      playlistName
    } = this.state;
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
                    title={<p>{item.fullDisplay || item.display}</p>}
                    description={item.artistNames ? `${item.artistNames}` : 'Track'}
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
            <h2>Add Songs</h2>
            <div className="search-container">
              <Search
                placeholder="Type a song name..."
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
                    color={'green'}
                    style={{ fontSize: 16, padding: '4px 12px', margin: 4 }}
                  >
                    {item.fullDisplay || item.display}
                  </Tag>
                ))}
              </div>

              {/* Selection counter or Create Playlist button */}
              <div className="selection-counter">
                {hasExactlyTenSelections ? (
                  <div className="button-group">
                    <Button
                      type="primary"
                      size="large"
                      onClick={this.showPlaylistNameModal}
                      loading={isCreatingPlaylist}
                      disabled={isCreatingPlaylist}
                      className="create-playlist-button"
                    >
                      Create Playlist
                    </Button>
                  </div>
                ) : (
                  <div className="selection-info">
                    <p>{selectedSeeds.length}/10 Selections</p>
                  </div>
                )}
              </div>

              {card}
            </div>
          </div>
        </div>

        {/* Playlist Name Modal */}
        <Modal
          title="Create Playlist"
          open={isModalVisible}
          onOk={this.handleCreatePlaylist}
          onCancel={this.handleModalCancel}
          okText="Create"
          cancelText="Cancel"
        >
          <Form layout="vertical">
            <Form.Item
              label="Playlist Name"
              required
              rules={[{ required: true, message: 'Please enter a playlist name' }]}
            >
              <Input
                placeholder="Enter playlist name"
                value={playlistName}
                onChange={this.handlePlaylistNameChange}
                maxLength={100}
              />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    );
  }
}

export default Dashboard;
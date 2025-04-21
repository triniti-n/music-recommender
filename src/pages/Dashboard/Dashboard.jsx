import React, { Component } from 'react';
import { Card, Input, List, Avatar, Tag, Empty } from 'antd';
import './Dashboard.css';

const { Search } = Input;

class Dashboard extends Component {
  constructor() {
    super();
    this.state = {
      searchResults: [],
      selectedSeeds: [], // saves selected artists or tracks
      searchValue: '',
      noResults: false // flag for no results
    };
    this.debounceTimeout = null;
  }

  // Debounced search for better UX
  handleInputChange = (e) => {
    const value = e.target.value;
    this.setState({ searchValue: value });
    clearTimeout(this.debounceTimeout);
    this.debounceTimeout = setTimeout(() => {
      this.getSearchResults(value);
    }, 400);
  };

  // Add selected item to the tag list
  handleSelectItem = (item) => {
    const id = item.uri || item.id;
    if (!this.state.selectedSeeds.some(i => (i.uri || i.id) === id)) {
      this.setState(prevState => ({
        selectedSeeds: [...prevState.selectedSeeds, item]
      }));
    }
  };

  // Remove a tag
  handleCloseTag = (item) => {
    const id = item.uri || item.id;
    this.setState(prevState => ({
      selectedSeeds: prevState.selectedSeeds.filter(i => (i.uri || i.id) !== id)
    }));
  };

  // Called on search button click
  handleSearch = (value) => {
    this.setState({ searchValue: value });
    this.getSearchResults(value, true); // force search and show no results if needed
  };

  getSearchResults(query, forceShowNoResults = false) {
    if (!query) {
      this.setState({ searchResults: [], noResults: false });
      return;
    }
    fetch(`/api/spotify/search?q=${encodeURIComponent(query)}&type=track,artist`)
      .then(response => {
        if (!response.ok) {
          throw Error('Response Not Ok');
        }
        return response.json();
      })
      .then(({ tracks, artists }) => {
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
    const { searchResults, selectedSeeds, searchValue, noResults } = this.state;
    let card;
    if (noResults) {
      card = <Empty description="No results found" style={{ marginTop: 20 }} />;
    } else if (searchResults.length > 0) {
      card = (
        <Card style={{ marginTop: 20 }}>
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
        </Card>
      );
    } else {
      card = <Card hidden={true} />;
    }
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
        </div>
        <div className="dashboard-content">
          <div className="recommendations-section">
            <h2>Recommendations</h2>
            <div className="music-grid">
              {/* Example static cards, replace with your dynamic cards */}
            </div>
          </div>
          <div className="preferences-section">
            <h2>Search</h2>
            <div className="input-section">
              <h3>Add Songs or Artists</h3>
              <div className="Search">
                <Search
                  placeholder="Type a song or artist name..."
                  enterButton="Search"
                  size="large"
                  value={searchValue}
                  onChange={this.handleInputChange}
                  onSearch={this.handleSearch}
                  allowClear
                />
                {/* Display selected tags */}
                <div style={{ margin: '16px 0' }}>
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
                {card}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Dashboard;
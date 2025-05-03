import React, { useState, useEffect } from 'react';
import { Card, List, Empty, Button, message } from 'antd';
import { useAuth } from '../../context/AuthContext';
import { getPlaylists } from '../../services/spotifyService';
import './Library.css';

const Library = () => {
  const [playlists, setPlaylists] = useState([]);
  const { accessToken } = useAuth();

  useEffect(() => {
    const fetchPlaylists = async () => {
      if (!accessToken) return;

      try {
        const data = await getPlaylists(accessToken);
        setPlaylists(data.items || []);
      } catch (error) {
        console.error('Error fetching playlists:', error);
        message.error('Failed to load playlists');
      }
    };

    fetchPlaylists();
  }, [accessToken]);

  return (
    <div className="dashboard">
      <div className="dashboard-content">
        <h2 className="library-title">Your Library</h2>

        {playlists.length > 0 ? (
          <List
            grid={{
              gutter: 16,
              xs: 1,
              sm: 2,
              md: 3,
              lg: 3,
              xl: 4,
              xxl: 4,
            }}
            dataSource={playlists}
            renderItem={(playlist) => (
              <List.Item>
                <Card
                  hoverable
                  className="playlist-card"
                  cover={
                    <img
                      alt={playlist.name}
                      src={playlist.images[0]?.url || 'default-playlist-image.jpg'}
                      className="playlist-cover"
                    />
                  }
                >
                  <Card.Meta
                    title={playlist.name}
                    description={`${playlist.tracks.total} tracks`}
                  />
                </Card>
              </List.Item>
            )}
          />
        ) : (
          <div className="empty-state-container">
            <Card className="empty-state-card">
              <Empty
                description={
                  <span className="empty-description">
                    Your library is empty. Start by creating a playlist or saving some tracks!
                  </span>
                }
              >
                <Button type="primary" href="/search">
                  Create Playlist
                </Button>
              </Empty>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Library;



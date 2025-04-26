const SPOTIFY_API_BASE = 'https://api.spotify.com/v1';

export const getPlaylists = async (accessToken) => {
  try {
    const response = await fetch(`${SPOTIFY_API_BASE}/me/playlists`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch playlists');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in getPlaylists:', error);
    throw error;
  }
};

export const getPlaylistTracks = async (accessToken, playlistId) => {
  try {
    const response = await fetch(`${SPOTIFY_API_BASE}/playlists/${playlistId}/tracks`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch playlist tracks');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in getPlaylistTracks:', error);
    throw error;
  }
};

export const searchSpotify = async (accessToken, query, type = 'track') => {
  try {
    const response = await fetch(
      `${SPOTIFY_API_BASE}/search?q=${encodeURIComponent(query)}&type=${type}`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to search Spotify');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in searchSpotify:', error);
    throw error;
  }
}; 
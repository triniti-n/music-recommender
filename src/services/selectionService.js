const API_BASE_URL = 'http://localhost:5000/api';

export const addSelection = async (selectionData) => {
  const response = await fetch(`${API_BASE_URL}/search/selections`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify({
      action: 'add',
      selections: [selectionData],
      searchQuery: selectionData.searchQuery
    })
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to save selection');
  }

  return response.json();
};

export const removeSelection = async (selection) => {
  const response = await fetch(`${API_BASE_URL}/search/selections`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify({
      action: 'remove',
      selections: [selection]
    })
  });

  if (!response.ok) {
    throw new Error('Failed to remove selection');
  }

  return response.json();
};
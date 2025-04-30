const API_BASE_URL = 'http://localhost:5000/api';

export const addSelection = async (selectionData) => {
  const response = await fetch(`${API_BASE_URL}/selections/add`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify(selectionData)
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to save selection');
  }

  return response.json();
};

export const removeSelection = async (selectionId) => {
  const response = await fetch(`${API_BASE_URL}/selections/${selectionId}`, {
    method: 'DELETE',
    credentials: 'include'
  });

  if (!response.ok) {
    throw new Error('Failed to remove selection');
  }

  return response.json();
};
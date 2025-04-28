import { db } from "../components/config/firebase";
import { collection, addDoc, getDocs, query, where, orderBy } from "firebase/firestore";

// Add a new user selection
export const addUserSelection = async (selection) => {
  await addDoc(collection(db, "userSelections"), selection);
};

// Get all selections for a user and format them for playlist creation
export const getUserSelectionsForPlaylist = async (userId) => {
  const q = query(
    collection(db, "userSelections"), 
    where("userId", "==", userId),
    orderBy("selectedAt", "desc")
  );
  
  const querySnapshot = await getDocs(q);
  const selections = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
  
  // Format the data for playlist creation
  const playlistData = {
    userId: userId,
    timestamp: new Date().toISOString(),
    tracks: selections.filter(item => item.type === 'track').map(item => ({
      spotifyId: item.spotifyId,
      name: item.name,
      type: 'track'
    })),
    artists: selections.filter(item => item.type === 'artist').map(item => ({
      spotifyId: item.spotifyId,
      name: item.name,
      type: 'artist'
    }))
  };
  
  return playlistData;
};

// Export selections to JSON format
export const exportSelectionsToJson = async (userId) => {
  const selections = await getUserSelectionsForPlaylist(userId);
  return JSON.stringify(selections, null, 2);
};

// Example handler for selecting items
export const handleSelect = async (selection, userId) => {
  const docData = {
    imageUrl: selection.imageUrl,
    name: selection.name,
    searchQuery: selection.searchQuery,
    selectedAt: new Date(),
    spotifyId: selection.spotifyId,
    type: selection.type,
    userId: userId
  };
  await addUserSelection(docData);
};

// Export user data to JSON
export const exportUserDataToJson = async (userId) => {
  try {
    // Get user selections
    const selectionsQuery = query(
      collection(db, "userSelections"),
      where("userId", "==", userId),
      orderBy("selectedAt", "desc")
    );
    
    const selectionsSnapshot = await getDocs(selectionsQuery);
    const selections = selectionsSnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
      selectedAt: doc.data().selectedAt.toDate().toISOString() // Convert Firestore Timestamp
    }));

    // Format the data
    const exportData = {
      userId: userId,
      exportedAt: new Date().toISOString(),
      selections: {
        tracks: selections.filter(item => item.type === 'track'),
        artists: selections.filter(item => item.type === 'artist')
      }
    };

    // Send to server for storage
    const response = await fetch('http://localhost:5000/api/selections/export', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(exportData)
    });

    if (!response.ok) {
      throw new Error('Failed to export data');
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error exporting user data:', error);
    throw error;
  }
};

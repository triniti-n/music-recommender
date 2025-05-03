// Import the functions you need from the Firebase SDKs
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

// Use environment variables for sensitive config
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "AIzaSyDZPXxZQqVYMlvqzj8EdJDEJYXl-NwOGVs",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "music-recommender-app.firebaseapp.com",
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "music-recommender-app",
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "music-recommender-app.appspot.com",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "123456789012",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:123456789012:web:abcdef1234567890"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
const db = getFirestore(app);

export { app, db };
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Hero from './pages/Home/Hero';
import SearchPage from './pages/SearchPage/SearchPage';
import Library from './pages/Library/Library';
import MusicPlayer from './pages/MusicPlayer/MusicPlayer';
import Callback from './pages/Callback';
import Navbar from './components/utils/Navbar/Navbar';
import { AuthProvider } from './context/AuthContext';
import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="app">
          <div className="container">
            <div className="main-box">
              <Navbar />
              <Routes>
                <Route path="/" element={<Hero />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/callback" element={<Callback />} />
                <Route path="/library" element={<Library />} />
                <Route path="/player" element={<MusicPlayer />} />
              </Routes>
            </div>
          </div>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
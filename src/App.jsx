import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Hero from './pages/Hero/Hero';
import SearchPage from './pages/SearchPage/SearchPage';
import Callback from './pages/Callback/Callback';
import Navbar from './components/utils/Navbar/Navbar';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<Hero />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/callback" element={<Callback />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 
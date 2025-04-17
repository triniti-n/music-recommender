import './App.css';
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/utils/Navbar/Navbar';
import Hero from './components/utils/Hero/Hero';
import Dashboard from './pages/Dashboard';

const App = () => {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <div className="container">
          <div className="main-box">
            <Routes>
              <Route path="/" element={<Hero />} />
              <Route path="/login" element={<Dashboard />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
};

export default App;

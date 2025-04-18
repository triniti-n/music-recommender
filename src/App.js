import './App.css';
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/utils/Navbar/Navbar';
import Hero from './pages/Home/Hero';
import Dashboard from './pages/Dashboard/Dashboard';
import Callback from './pages/Callback';

const App = () => {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <div className="container">
          <div className="main-box">
            <Routes>
              <Route path="/" element={<Hero />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/callback" element={<Callback />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
};

export default App;

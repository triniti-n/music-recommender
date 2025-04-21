import './App.css';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/utils/Navbar/Navbar';
import Hero from './pages/Home/Hero';
import Dashboard from './pages/Dashboard/Dashboard';
import Callback from './pages/Callback';

const App = () => (
  <Router>
    <div className="app">
      <Navbar />
      <div className="container">
        <main className="main-box">
          <Routes>
            <Route path="/home" element={<Hero />} />
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/callback" element={<Callback />} />
          </Routes>
        </main>
      </div>
    </div>
  </Router>
);

export default App;

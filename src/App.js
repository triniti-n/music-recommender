import './App.css';
import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';

const App = () => {
  return (
    <div className="container">
      <div className="main-box">
        <Navbar />
        <Hero />
      </div>
    </div>
  );
};

export default App;

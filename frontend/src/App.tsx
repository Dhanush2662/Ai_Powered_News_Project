import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import NewsFeed from './pages/NewsFeed';
import FactCheck from './pages/FactCheck';
import ConsensusScore from './pages/ConsensusScore';
import Translator from './pages/Translator';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/news-feed" element={<NewsFeed />} />
            <Route path="/fact-check" element={<FactCheck />} />
            <Route path="/consensus-score" element={<ConsensusScore />} />
            <Route path="/translator" element={<Translator />} />
          </Routes>
        </main>
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;

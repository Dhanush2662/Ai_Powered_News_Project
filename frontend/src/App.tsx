import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import NewsFeed from './pages/NewsFeed';
import BiasAnalysis from './pages/BiasAnalysis';
import FactCheck from './pages/FactCheck';
import CoverageComparison from './pages/CoverageComparison';
import SentimentAnalysis from './pages/SentimentAnalysis';
import FakeNewsDetection from './pages/FakeNewsDetection';
import UserFeedback from './pages/UserFeedback';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/news" element={<NewsFeed />} />
            <Route path="/bias-analysis" element={<BiasAnalysis />} />
            <Route path="/fact-check" element={<FactCheck />} />
            <Route path="/coverage-comparison" element={<CoverageComparison />} />
            <Route path="/sentiment-analysis" element={<SentimentAnalysis />} />
            <Route path="/fake-news-detection" element={<FakeNewsDetection />} />
            <Route path="/user-feedback" element={<UserFeedback />} />
          </Routes>
        </main>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;

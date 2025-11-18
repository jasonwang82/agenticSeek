import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Navigation from './components/Navigation';
import Home from './pages/Home';
import Settings from './pages/Settings';
import History from './pages/History';
import About from './pages/About';

function App() {
    return (
        <Router>
            <div className="app">
                <header className="header">
                    <h1>AgenticSeek</h1>
                    <Navigation />
                </header>
                <main className="main">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/history" element={<History />} />
                        <Route path="/settings" element={<Settings />} />
                        <Route path="/about" element={<About />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;

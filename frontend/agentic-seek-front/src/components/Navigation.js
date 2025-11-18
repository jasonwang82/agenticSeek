import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navigation() {
    const location = useLocation();

    const isActive = (path) => {
        return location.pathname === path ? 'active' : '';
    };

    return (
        <nav className="navigation">
            <Link to="/" className={`nav-link ${isActive('/')}`}>
                Home
            </Link>
            <Link to="/history" className={`nav-link ${isActive('/history')}`}>
                History
            </Link>
            <Link to="/settings" className={`nav-link ${isActive('/settings')}`}>
                Settings
            </Link>
            <Link to="/about" className={`nav-link ${isActive('/about')}`}>
                About
            </Link>
        </nav>
    );
}

export default Navigation;

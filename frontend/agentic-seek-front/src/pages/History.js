import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

function History() {
    const [history, setHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [filter, setFilter] = useState('all'); // all, user, agent, error
    const [expandedItems, setExpandedItems] = useState(new Set());

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = () => {
        const saved = localStorage.getItem('agenticSeekHistory');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                setHistory(parsed);
            } catch (err) {
                console.error('Error loading history:', err);
            }
        }
    };

    const toggleExpand = (index) => {
        setExpandedItems(prev => {
            const newSet = new Set(prev);
            if (newSet.has(index)) {
                newSet.delete(index);
            } else {
                newSet.add(index);
            }
            return newSet;
        });
    };

    const clearHistory = () => {
        if (window.confirm('Are you sure you want to clear all history?')) {
            localStorage.removeItem('agenticSeekHistory');
            setHistory([]);
        }
    };

    const filteredHistory = history.filter(item => {
        if (filter === 'all') return true;
        return item.type === filter;
    });

    return (
        <div className="page-container">
            <div className="history-section">
                <div className="history-header">
                    <h2>Chat History</h2>
                    <div className="history-controls">
                        <select value={filter} onChange={(e) => setFilter(e.target.value)} className="filter-select">
                            <option value="all">All Messages</option>
                            <option value="user">User Messages</option>
                            <option value="agent">Agent Messages</option>
                            <option value="error">Errors</option>
                        </select>
                        <button onClick={clearHistory} className="clear-button">
                            Clear History
                        </button>
                    </div>
                </div>
                <div className="history-content">
                    {filteredHistory.length === 0 ? (
                        <p className="placeholder">No history available. Start chatting to see your conversation history here.</p>
                    ) : (
                        <div className="history-list">
                            {filteredHistory.map((item, index) => (
                                <div
                                    key={index}
                                    className={`history-item ${item.type}-message`}
                                >
                                    <div className="history-item-header">
                                        <span className="history-type">{item.type}</span>
                                        {item.agentName && (
                                            <span className="agent-name">{item.agentName}</span>
                                        )}
                                        <span className="history-time">
                                            {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Unknown time'}
                                        </span>
                                        {item.reasoning && (
                                            <button
                                                className="reasoning-toggle"
                                                onClick={() => toggleExpand(index)}
                                            >
                                                {expandedItems.has(index) ? '▼' : '▶'} Reasoning
                                            </button>
                                        )}
                                    </div>
                                    <div className="history-item-content">
                                        <ReactMarkdown>{item.content}</ReactMarkdown>
                                    </div>
                                    {item.reasoning && expandedItems.has(index) && (
                                        <div className="reasoning-content">
                                            <ReactMarkdown>{item.reasoning}</ReactMarkdown>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default History;

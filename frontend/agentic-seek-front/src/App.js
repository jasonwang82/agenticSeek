import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import './App.css';
import { colors } from './colors';

function App() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [currentView, setCurrentView] = useState('blocks');
    const [responseData, setResponseData] = useState(null);
    const [isOnline, setIsOnline] = useState(false);
    const [status, setStatus] = useState('Agents ready');
    const [expandedReasoning, setExpandedReasoning] = useState(new Set());
    const [connectionStatus, setConnectionStatus] = useState('checking');
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        checkHealth();
        const intervalId = setInterval(() => {
            checkHealth();
            fetchLatestAnswer();
            fetchScreenshot();
        }, 3000);
        return () => clearInterval(intervalId);
    }, [messages]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (!isLoading && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isLoading]);

    const checkHealth = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/health', { timeout: 3000 });
            setIsOnline(true);
            setConnectionStatus('connected');
            console.log('System is online');
        } catch (err) {
            setIsOnline(false);
            setConnectionStatus('disconnected');
            console.log('System is offline');
        }
    };

    const fetchScreenshot = async () => {
        try {
            const timestamp = new Date().getTime();
            const res = await axios.get(`http://127.0.0.1:8000/screenshots/updated_screen.png?timestamp=${timestamp}`, {
                responseType: 'blob'
            });
            console.log('Screenshot fetched successfully');
            const imageUrl = URL.createObjectURL(res.data);
            setResponseData((prev) => {
                if (prev?.screenshot && prev.screenshot !== 'placeholder.png') {
                    URL.revokeObjectURL(prev.screenshot);
                }
                return {
                    ...prev,
                    screenshot: imageUrl,
                    screenshotTimestamp: new Date().getTime()
                };
            });
        } catch (err) {
            console.error('Error fetching screenshot:', err);
            setResponseData((prev) => ({
                ...prev,
                screenshot: 'placeholder.png',
                screenshotTimestamp: new Date().getTime()
            }));
        }
    };

    const normalizeAnswer = (answer) => {
        return answer
            .trim()
            .toLowerCase()
            .replace(/\s+/g, ' ')
            .replace(/[.,!?]/g, '')
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const toggleReasoning = (messageIndex) => {
        setExpandedReasoning(prev => {
            const newSet = new Set(prev);
            if (newSet.has(messageIndex)) {
                newSet.delete(messageIndex);
            } else {
                newSet.add(messageIndex);
            }
            return newSet;
        });
    };

    const fetchLatestAnswer = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/latest_answer');
            const data = res.data;

            updateData(data);
            if (!data.answer || data.answer.trim() === '') {
                return;
            }
            const normalizedNewAnswer = normalizeAnswer(data.answer);
            const answerExists = messages.some(
                (msg) => normalizeAnswer(msg.content) === normalizedNewAnswer
            );
            if (!answerExists) {
                setMessages((prev) => [
                    ...prev,
                    {
                        type: 'agent',
                        content: data.answer,
                        reasoning: data.reasoning,
                        agentName: data.agent_name,
                        status: data.status,
                        uid: data.uid,
                    },
                ]);
                setStatus(data.status);
                scrollToBottom();
            } else {
                console.log('Duplicate answer detected, skipping:', data.answer);
            }
        } catch (error) {
            console.error('Error fetching latest answer:', error);
        }
    };

    const updateData = (data) => {
        setResponseData((prev) => ({
            ...prev,
            blocks: data.blocks || prev.blocks || null,
            done: data.done,
            answer: data.answer,
            agent_name: data.agent_name,
            status: data.status,
            uid: data.uid,
        }));
    };

    const handleStop = async (e) => {
        e.preventDefault();
        checkHealth();
        setIsLoading(false);
        setError(null);
        try {
            const res = await axios.get('http://127.0.0.1:8000/stop');
            setStatus("Requesting stop...");
        } catch (err) {
            console.error('Error stopping the agent:', err);
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        checkHealth();
        if (!query.trim()) {
            console.log('Empty query');
            return;
        }
        setMessages((prev) => [...prev, { type: 'user', content: query }]);
        setIsLoading(true);
        setError(null);

        try {
            console.log('Sending query:', query);
            setQuery('waiting for response...');
            const res = await axios.post('http://127.0.0.1:8000/query', {
                query,
                tts_enabled: false
            });
            setQuery('Enter your query...');
            console.log('Response:', res.data);
            const data = res.data;
            updateData(data);
        } catch (err) {
            console.error('Error:', err);
            setError('Failed to process query.');
            setMessages((prev) => [
                ...prev,
                { type: 'error', content: 'Error: Unable to get a response.' },
            ]);
        } finally {
            console.log('Query completed');
            setIsLoading(false);
            setQuery('');
        }
    };

    const handleGetScreenshot = async () => {
        try {
            setCurrentView('screenshot');
        } catch (err) {
            setError('Browser not in use');
        }
    };

    return (
        <div className="app">
            <header className="header">
                <div className="header-content">
                    <h1>AgenticSeek</h1>
                    <div className="connection-indicator">
                        <span className={`status-dot ${connectionStatus}`}></span>
                        <span className="status-text">
                            {connectionStatus === 'connected' ? 'Connected' : 
                             connectionStatus === 'disconnected' ? 'Disconnected' : 'Checking...'}
                        </span>
                    </div>
                </div>
            </header>
            <main className="main">
                <div className="app-sections">
                    <div className="chat-section">
                        <div className="section-header">
                            <h2>Chat Interface</h2>
                            {isOnline && status && (
                                <div className="status-badge">{status}</div>
                            )}
                        </div>
                        <div className="messages">
                            {messages.length === 0 ? (
                                <div className="welcome-message">
                                    <div className="welcome-icon">🤖</div>
                                    <p className="placeholder">Welcome to AgenticSeek!</p>
                                    <p className="placeholder-subtitle">Ask me anything - I can browse the web, write code, manage files, and more.</p>
                                </div>
                            ) : (
                                messages.map((msg, index) => (
                                    <div
                                        key={index}
                                        className={`message ${
                                            msg.type === 'user'
                                                ? 'user-message'
                                                : msg.type === 'agent'
                                                ? 'agent-message'
                                                : 'error-message'
                                        }`}
                                    >
                                        <div className="message-header">
                                            {msg.type === 'agent' && msg.agentName && (
                                                <span className="agent-name">
                                                    <span className="agent-icon">🤖</span>
                                                    {msg.agentName}
                                                </span>
                                            )}
                                            {msg.type === 'agent' && msg.reasoning && (
                                                <button 
                                                    className="reasoning-toggle"
                                                    onClick={() => toggleReasoning(index)}
                                                    title={expandedReasoning.has(index) ? "Hide reasoning" : "Show reasoning"}
                                                >
                                                    {expandedReasoning.has(index) ? '▼' : '▶'} Reasoning
                                                </button>
                                            )}
                                        </div>
                                        {msg.type === 'agent' && msg.reasoning && expandedReasoning.has(index) && (
                                            <div className="reasoning-content">
                                                <ReactMarkdown>{msg.reasoning}</ReactMarkdown>
                                            </div>
                                        )}
                                        <div className="message-content">
                                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                                        </div>
                                        {msg.type === 'agent' && msg.status && (
                                            <div className="message-status">{msg.status}</div>
                                        )}
                                    </div>
                                ))
                            )}
                            {isLoading && (
                                <div className="message agent-message loading-message">
                                    <div className="loading-dots">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                    <div className="message-content">Processing your request...</div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                        {!isOnline && (
                            <div className="offline-banner">
                                <span className="offline-icon">⚠️</span>
                                <span>Backend is offline. Please start the backend server first.</span>
                            </div>
                        )}
                        <form onSubmit={handleSubmit} className="input-form">
                            <input
                                ref={inputRef}
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder={isOnline ? "Type your query..." : "Backend offline..."}
                                disabled={isLoading || !isOnline}
                                className={!isOnline ? 'disabled-input' : ''}
                            />
                            <button 
                                type="submit" 
                                disabled={isLoading || !isOnline || !query.trim()}
                                className="send-button"
                            >
                                {isLoading ? 'Sending...' : 'Send'}
                            </button>
                            <button 
                                type="button"
                                onClick={handleStop}
                                disabled={!isLoading}
                                className="stop-button"
                            >
                                Stop
                            </button>
                        </form>
                    </div>

                    <div className="computer-section">
                        <div className="section-header">
                            <h2>Computer View</h2>
                        </div>
                        <div className="view-selector">
                            <button
                                className={currentView === 'blocks' ? 'active' : ''}
                                onClick={() => setCurrentView('blocks')}
                                title="View code editor blocks"
                            >
                                <span className="button-icon">📝</span>
                                Editor View
                            </button>
                            <button
                                className={currentView === 'screenshot' ? 'active' : ''}
                                onClick={responseData?.screenshot ? () => setCurrentView('screenshot') : handleGetScreenshot}
                                disabled={!responseData?.screenshot}
                                title="View browser screenshot"
                            >
                                <span className="button-icon">🌐</span>
                                Browser View
                            </button>
                        </div>
                        <div className="content">
                            {error && (
                                <div className="error-banner">
                                    <span className="error-icon">❌</span>
                                    <p className="error">{error}</p>
                                </div>
                            )}
                            {currentView === 'blocks' ? (
                                <div className="blocks">
                                    {responseData && responseData.blocks && Object.values(responseData.blocks).length > 0 ? (
                                        Object.values(responseData.blocks).map((block, index) => (
                                            <div key={index} className="block">
                                                <div className="block-header">
                                                    <p className="block-tool">
                                                        <span className="tool-icon">🔧</span>
                                                        Tool: {block.tool_type}
                                                    </p>
                                                    {block.success !== undefined && (
                                                        <span className={`block-status ${block.success ? 'success' : 'failure'}`}>
                                                            {block.success ? '✓ Success' : '✗ Failure'}
                                                        </span>
                                                    )}
                                                </div>
                                                <pre className="block-code">{block.block}</pre>
                                                {block.feedback && (
                                                    <p className="block-feedback">
                                                        <span className="feedback-icon">💬</span>
                                                        Feedback: {block.feedback}
                                                    </p>
                                                )}
                                            </div>
                                        ))
                                    ) : (
                                        <div className="empty-state">
                                            <div className="empty-icon">📋</div>
                                            <p className="empty-text">No active tools</p>
                                            <p className="empty-subtext">Tools will appear here when agents are working</p>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="screenshot-container">
                                    {responseData?.screenshot ? (
                                        <img
                                            src={responseData.screenshot}
                                            alt="Browser screenshot"
                                            className="screenshot-image"
                                            onError={(e) => {
                                                e.target.src = 'placeholder.png';
                                                console.error('Failed to load screenshot');
                                            }}
                                            key={responseData?.screenshotTimestamp || 'default'}
                                        />
                                    ) : (
                                        <div className="empty-state">
                                            <div className="empty-icon">🌐</div>
                                            <p className="empty-text">No browser screenshot available</p>
                                            <p className="empty-subtext">Screenshots will appear when the browser agent is active</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;
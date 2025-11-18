import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Settings() {
    const [settings, setSettings] = useState({
        apiUrl: 'http://127.0.0.1:8000',
        ttsEnabled: false,
        autoRefresh: true,
        refreshInterval: 3000,
    });
    const [isOnline, setIsOnline] = useState(false);
    const [saveStatus, setSaveStatus] = useState('');

    useEffect(() => {
        checkHealth();
        loadSettings();
    }, []);

    const checkHealth = async () => {
        try {
            await axios.get(`${settings.apiUrl}/health`);
            setIsOnline(true);
        } catch {
            setIsOnline(false);
        }
    };

    const loadSettings = () => {
        const saved = localStorage.getItem('agenticSeekSettings');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                setSettings(prev => ({ ...prev, ...parsed }));
            } catch (err) {
                console.error('Error loading settings:', err);
            }
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setSettings(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSave = () => {
        localStorage.setItem('agenticSeekSettings', JSON.stringify(settings));
        setSaveStatus('Settings saved successfully!');
        setTimeout(() => setSaveStatus(''), 3000);
    };

    const handleTestConnection = async () => {
        try {
            await axios.get(`${settings.apiUrl}/health`);
            setSaveStatus('Connection successful!');
            setIsOnline(true);
        } catch (err) {
            setSaveStatus('Connection failed. Check your API URL.');
            setIsOnline(false);
        }
        setTimeout(() => setSaveStatus(''), 3000);
    };

    return (
        <div className="page-container">
            <div className="settings-section">
                <h2>Settings</h2>
                <div className="settings-content">
                    <div className="setting-group">
                        <label htmlFor="apiUrl">API URL</label>
                        <input
                            type="text"
                            id="apiUrl"
                            name="apiUrl"
                            value={settings.apiUrl}
                            onChange={handleChange}
                            placeholder="http://127.0.0.1:8000"
                        />
                        <button onClick={handleTestConnection} className="test-button">
                            Test Connection
                        </button>
                        <div className={`status-indicator ${isOnline ? 'online' : 'offline'}`}>
                            {isOnline ? '● Online' : '● Offline'}
                        </div>
                    </div>

                    <div className="setting-group">
                        <label htmlFor="ttsEnabled">
                            <input
                                type="checkbox"
                                id="ttsEnabled"
                                name="ttsEnabled"
                                checked={settings.ttsEnabled}
                                onChange={handleChange}
                            />
                            Enable Text-to-Speech
                        </label>
                    </div>

                    <div className="setting-group">
                        <label htmlFor="autoRefresh">
                            <input
                                type="checkbox"
                                id="autoRefresh"
                                name="autoRefresh"
                                checked={settings.autoRefresh}
                                onChange={handleChange}
                            />
                            Auto-refresh Data
                        </label>
                    </div>

                    <div className="setting-group">
                        <label htmlFor="refreshInterval">Refresh Interval (ms)</label>
                        <input
                            type="number"
                            id="refreshInterval"
                            name="refreshInterval"
                            value={settings.refreshInterval}
                            onChange={handleChange}
                            min="1000"
                            step="1000"
                            disabled={!settings.autoRefresh}
                        />
                    </div>

                    <div className="setting-actions">
                        <button onClick={handleSave} className="save-button">
                            Save Settings
                        </button>
                        {saveStatus && <div className="save-status">{saveStatus}</div>}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Settings;

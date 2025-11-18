import React from 'react';

function About() {
    return (
        <div className="page-container">
            <div className="about-section">
                <h2>About AgenticSeek</h2>
                <div className="about-content">
                    <div className="about-section-item">
                        <h3>What is AgenticSeek?</h3>
                        <p>
                            AgenticSeek is an intelligent agentic system that combines multiple specialized agents
                            to help you accomplish complex tasks. It uses advanced language models and routing
                            systems to delegate tasks to the most appropriate agent for the job.
                        </p>
                    </div>

                    <div className="about-section-item">
                        <h3>Features</h3>
                        <ul>
                            <li><strong>Multi-Agent System:</strong> Different agents handle different types of tasks</li>
                            <li><strong>Browser Agent:</strong> Interacts with web pages and browsers</li>
                            <li><strong>Code Agent:</strong> Writes and executes code</li>
                            <li><strong>File Agent:</strong> Manages files and directories</li>
                            <li><strong>Planner Agent:</strong> Breaks down complex tasks into steps</li>
                            <li><strong>Real-time Updates:</strong> See what agents are doing in real-time</li>
                        </ul>
                    </div>

                    <div className="about-section-item">
                        <h3>Agents</h3>
                        <div className="agents-list">
                            <div className="agent-card">
                                <h4>Browser Agent</h4>
                                <p>Handles web browsing, form filling, and web interactions</p>
                            </div>
                            <div className="agent-card">
                                <h4>Code Agent</h4>
                                <p>Writes, executes, and debugs code in multiple languages</p>
                            </div>
                            <div className="agent-card">
                                <h4>File Agent</h4>
                                <p>Manages file operations and directory structures</p>
                            </div>
                            <div className="agent-card">
                                <h4>Planner Agent</h4>
                                <p>Creates plans and coordinates multi-step tasks</p>
                            </div>
                            <div className="agent-card">
                                <h4>Casual Agent</h4>
                                <p>Handles general conversation and questions</p>
                            </div>
                            <div className="agent-card">
                                <h4>MCP Agent</h4>
                                <p>Integrates with Model Context Protocol tools</p>
                            </div>
                        </div>
                    </div>

                    <div className="about-section-item">
                        <h3>Version</h3>
                        <p>Version 0.1.0</p>
                    </div>

                    <div className="about-section-item">
                        <h3>License</h3>
                        <p>Please refer to the LICENSE file in the repository for license information.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default About;

class DebugClient {
    constructor() {
        this.apiBase = '/api/v1/debug';
        this.currentSession = null;
        this.projectMemory = null;
        this.activeAnalysis = null;
    }

    async startSession(projectId) {
        try {
            const response = await fetch(`${this.apiBase}/session/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    project_id: projectId,
                    user_id: this.getUserId()
                })
            });

            if (!response.ok) throw new Error('Failed to start session');
            
            const result = await response.json();
            this.currentSession = result.session_id;
            
            // Load project memory
            await this.loadProjectMemory(projectId);
            
            return result;
        } catch (error) {
            console.error('❌ Failed to start debug session:', error);
            throw error;
        }
    }

    async analyzeCode(userInput, requestType = 'general') {
        if (!this.currentSession) {
            throw new Error('No active debug session');
        }

        try {
            const request = {
                session_id: this.currentSession,
                project_id: this.getCurrentProjectId(),
                user_input: userInput,
                request_type: requestType
            };

            const response = await fetch(`${this.apiBase}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request)
            });

            if (!response.ok) throw new Error('Analysis failed');
            
            const result = await response.json();
            this.activeAnalysis = result;
            
            return result;
        } catch (error) {
            console.error('❌ Code analysis failed:', error);
            throw error;
        }
    }

    async streamAnalysis(userInput, requestType = 'general') {
        if (!this.currentSession) {
            throw new Error('No active debug session');
        }

        const request = {
            session_id: this.currentSession,
            project_id: this.getCurrentProjectId(),
            user_input: userInput,
            request_type: requestType
        };

        return new EventSource(`${this.apiBase}/stream?` + new URLSearchParams({
            body: JSON.stringify(request)
        }));
    }

    async applyChanges(changeIds) {
        try {
            const response = await fetch(`${this.apiBase}/apply-changes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.currentSession,
                    change_ids: changeIds
                })
            });

            if (!response.ok) throw new Error('Failed to apply changes');
            
            return await response.json();
        } catch (error) {
            console.error('❌ Failed to apply changes:', error);
            throw error;
        }
    }

    async loadProjectMemory(projectId) {
        try {
            const response = await fetch(`${this.apiBase}/memory/${projectId}`);
            
            if (!response.ok) throw new Error('Failed to load memory');
            
            this.projectMemory = await response.json();
            this.displayProjectMemory();
            
            return this.projectMemory;
        } catch (error) {
            console.error('❌ Failed to load project memory:', error);
            throw error;
        }
    }

    // UI Integration Methods
    initializeDebugInterface() {
        const debugSection = document.getElementById('debug-section');
        if (!debugSection) return;

        debugSection.innerHTML = this.createDebugInterface();
        this.attachEventListeners();
    }

    createDebugInterface() {
        return `
            <div class="debug-container">
                <!-- Conversation Panel -->
                <div class="debug-conversation">
                    <div class="conversation-header">
                        <h3>🤖 Debug Assistant</h3>
                        <div class="conversation-controls">
                            <button id="clear-conversation" class="btn-icon">🗑️</button>
                            <button id="memory-toggle" class="btn-icon">🧠</button>
                        </div>
                    </div>
                    
                    <div class="conversation-messages" id="debug-messages">
                        <div class="ai-message">
                            <div class="message-content">
                                Hi! I'm your debugging assistant. I can help you:
                                <ul>
                                    <li>🐛 Find and fix bugs</li>
                                    <li>✨ Add new features</li>
                                    <li>📝 Explain code decisions</li>
                                    <li>🔧 Improve code quality</li>
                                    <li>🎯 Make precise changes</li>
                                </ul>
                                What would you like to work on?
                            </div>
                        </div>
                    </div>
                    
                    <div class="conversation-input">
                        <div class="input-container">
                            <textarea 
                                id="debug-input" 
                                placeholder="Describe the issue or what you'd like to change..."
                                rows="3"
                            ></textarea>
                            <div class="input-actions">
                                <button id="voice-debug" class="btn-icon" title="Voice Input">🎤</button>
                                <button id="send-debug" class="btn-primary">Send</button>
                            </div>
                        </div>
                        
                        <div class="quick-actions">
                            <button class="quick-action" data-action="fix_bug">🐛 Fix Bug</button>
                            <button class="quick-action" data-action="add_feature">✨ Add Feature</button>
                            <button class="quick-action" data-action="explain_code">📝 Explain Code</button>
                            <button class="quick-action" data-action="improve_quality">🔧 Improve Quality</button>
                        </div>
                    </div>
                </div>

                <!-- Analysis Panel -->
                <div class="debug-analysis">
                    <div class="analysis-header">
                        <h3>📊 Analysis Results</h3>
                        <div class="analysis-controls">
                            <button id="export-analysis" class="btn-secondary">Export</button>
                        </div>
                    </div>
                    
                    <div class="analysis-content" id="analysis-content">
                        <div class="analysis-placeholder">
                            <div class="placeholder-icon">🔍</div>
                            <p>Analysis results will appear here when you ask me to debug or analyze your code.</p>
                        </div>
                    </div>
                </div>

                <!-- Project Memory Panel -->
                <div class="project-memory" id="project-memory-panel" style="display: none;">
                    <div class="memory-header">
                        <h3>🧠 Project Memory</h3>
                        <button id="close-memory" class="btn-icon">✕</button>
                    </div>
                    
                    <div class="memory-content">
                        <div class="memory-section">
                            <h4>💡 Original Intent</h4>
                            <div id="original-intent" class="memory-item"></div>
                        </div>
                        
                        <div class="memory-section">
                            <h4>🗂️ Project Structure</h4>
                            <div id="project-structure" class="memory-item"></div>
                        </div>
                        
                        <div class="memory-section">
                            <h4>💬 Recent Conversations</h4>
                            <div id="recent-conversations" class="memory-item"></div>
                        </div>
                        
                        <div class="memory-section">
                            <h4>🎯 Key Decisions</h4>
                            <div id="key-decisions" class="memory-item"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Send debug message
        document.getElementById('send-debug').addEventListener('click', () => {
            this.sendDebugMessage();
        });

        // Debug input enter key
        document.getElementById('debug-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendDebugMessage();
            }
        });

        // Quick actions
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleQuickAction(action);
            });
        });

        // Memory toggle
        document.getElementById('memory-toggle').addEventListener('click', () => {
            this.toggleProjectMemory();
        });

        // Voice input
        document.getElementById('voice-debug').addEventListener('click', () => {
            this.startVoiceInput();
        });
    }

    async sendDebugMessage() {
        const input = document.getElementById('debug-input');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message to conversation
        this.addMessageToConversation(message, 'user');
        input.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Start streaming analysis
            const eventSource = await this.streamAnalysis(message);
            
            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleStreamingData(data);
            };

            eventSource.onerror = () => {
                this.hideTypingIndicator();
                this.addMessageToConversation('Sorry, something went wrong. Please try again.', 'ai');
                eventSource.close();
            };

        } catch (error) {
            this.hideTypingIndicator();
            this.addMessageToConversation('Analysis failed. Please try again.', 'ai');
        }
    }

    handleStreamingData(data) {
        switch (data.type) {
            case 'status':
                this.updateTypingIndicator(data.content);
                break;
            case 'analysis':
                this.displayAnalysisResults(data.content);
                break;
            case 'change_suggestion':
                this.addChangeSuggestion(data.content);
                break;
            case 'explanation':
                this.hideTypingIndicator();
                this.addMessageToConversation(data.content, 'ai');
                break;
            case 'complete':
                this.handleAnalysisComplete(data.response);
                break;
            case 'error':
                this.hideTypingIndicator();
                this.addMessageToConversation(data.content, 'ai');
                break;
        }
    }

    addMessageToConversation(message, sender) {
        const messagesContainer = document.getElementById('debug-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;
        
        messageDiv.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    displayAnalysisResults(analysis) {
        const analysisContent = document.getElementById('analysis-content');
        
        analysisContent.innerHTML = `
            <div class="analysis-results">
                <div class="analysis-summary">
                    <h4>📋 Analysis Summary</h4>
                    <p>${analysis.analysis_summary || 'Analysis completed'}</p>
                </div>
                
                ${analysis.issues && analysis.issues.length > 0 ? `
                    <div class="issues-found">
                        <h4>🐛 Issues Found (${analysis.issues.length})</h4>
                        ${analysis.issues.map(issue => `
                            <div class="issue-item ${issue.severity}">
                                <div class="issue-header">
                                    <span class="issue-type">${issue.issue_type}</span>
                                    <span class="issue-severity">${issue.severity}</span>
                                </div>
                                <div class="issue-description">${issue.description}</div>
                                <div class="issue-location">${issue.file_path}:${issue.line_number}</div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${analysis.recommended_actions && analysis.recommended_actions.length > 0 ? `
                    <div class="recommended-actions">
                        <h4>💡 Recommended Actions</h4>
                        <ul>
                            ${analysis.recommended_actions.map(action => `<li>${action}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    // Additional UI methods...
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'ai-message typing-indicator';
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
                <span class="typing-text">Analyzing...</span>
            </div>
        `;
        
        document.getElementById('debug-messages').appendChild(indicator);
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    // Helper methods
    getUserId() {
        return localStorage.getItem('user_id') || 'anonymous';
    }

    getCurrentProjectId() {
        return window.currentProjectId || 'default';
    }
}

// Initialize debug client
window.debugClient = new DebugClient();

// Auto-initialize when debug section is visible
document.addEventListener('DOMContentLoaded', () => {
    const debugTab = document.querySelector('[data-section="debug"]');
    if (debugTab) {
        debugTab.addEventListener('click', () => {
            setTimeout(() => {
                window.debugClient.initializeDebugInterface();
            }, 100);
        });
    }
});

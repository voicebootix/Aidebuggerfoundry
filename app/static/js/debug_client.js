class DebugClient {
    constructor() {
        this.sessionId = null;
        this.isConnected = false;
        this.currentFiles = {};
        this.analysisResults = null;
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.startSession();
        console.log('🔧 Debug client initialized');
    }
    
    bindEvents() {
        // Chat input
        const sendBtn = document.getElementById('debug-send-btn');
        const input = document.getElementById('debug-input');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.sendMessage();
                }
            });
        }
        
        // File upload
        const uploadBtn = document.getElementById('debug-upload-btn');
        const fileInput = document.getElementById('debug-file-input');
        
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.showUploadModal());
        }
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        }
        
        // Code editor
        const codeEditor = document.getElementById('code-editor-textarea');
        if (codeEditor) {
            codeEditor.addEventListener('input', () => this.updateEditorStats());
        }
        
        // Editor actions
        const saveBtn = document.getElementById('editor-save');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveCurrentFile());
        }
        
        // Modal close
        const modalClose = document.querySelector('.modal-close');
        if (modalClose) {
            modalClose.addEventListener('click', () => this.hideUploadModal());
        }
    }
    
    async startSession() {
        try {
            const response = await fetch('/api/v1/debug/session/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: 'default-project',
                    user_id: 'anonymous'
                })
            });
            
            const data = await response.json();
            this.sessionId = data.session_id;
            this.isConnected = true;
            
            console.log('✅ Debug session started:', this.sessionId);
            this.updateStatus('Connected');
            
        } catch (error) {
            console.error('❌ Failed to start debug session:', error);
            this.updateStatus('Connection failed');
        }
    }
    
    updateStatus(status) {
        const statusElement = document.querySelector('.debug-status span:last-child');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }
    
    async sendMessage() {
        const input = document.getElementById('debug-input');
        const message = input.value.trim();
        
        if (!message || !this.sessionId) return;
        
        // Add user message to chat
        this.addMessageToChat(message, 'user');
        input.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/v1/debug/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    user_input: message,
                    project_id: 'default-project',
                    context: {
                        current_files: this.currentFiles,
                        previous_analysis: this.analysisResults
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiResponse = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') continue;
                        
                        try {
                            const parsed = JSON.parse(data);
                            this.handleStreamingData(parsed);
                            
                            if (parsed.type === 'explanation') {
                                aiResponse += parsed.content;
                            }
                        } catch (e) {
                            // Ignore parsing errors for malformed chunks
                        }
                    }
                }
            }
            
        } catch (error) {
            console.error('❌ Debug request failed:', error);
            this.hideTypingIndicator();
            this.addMessageToChat('Sorry, there was an error processing your request. Please try again.', 'ai');
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
                this.addMessageToChat(data.content, 'ai');
                break;
            case 'complete':
                this.handleAnalysisComplete(data.response);
                break;
            case 'error':
                this.hideTypingIndicator();
                this.addMessageToChat(data.content, 'ai');
                break;
        }
    }
    
    addMessageToChat(message, sender) {
        const messagesContainer = document.getElementById('debug-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;
        
        messageDiv.innerHTML = `
            <div class="message-content">${this.formatMessage(message)}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    formatMessage(message) {
        // Convert markdown-style formatting to HTML
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }
    
    showTypingIndicator() {
        const indicator = document.getElementById('debug-typing-indicator');
        if (indicator) {
            indicator.style.display = 'flex';
        }
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('debug-typing-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    updateTypingIndicator(message) {
        const indicator = document.getElementById('debug-typing-indicator');
        if (indicator) {
            const textElement = indicator.querySelector('p');
            if (textElement) {
                textElement.textContent = message;
            }
        }
    }
    
    showUploadModal() {
        const modal = document.getElementById('debug-upload-modal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }
    
    hideUploadModal() {
        const modal = document.getElementById('debug-upload-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        try {
            const content = await this.readFileContent(file);
            this.addFileToEditor(file.name, content);
            this.hideUploadModal();
            
            // Automatically analyze the uploaded file
            this.addMessageToChat(`📁 Uploaded file: ${file.name}`, 'user');
            this.analyzeCurrentFile();
            
        } catch (error) {
            console.error('❌ File upload failed:', error);
            alert('Failed to read file. Please try again.');
        }
    }
    
    readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }
    
    addFileToEditor(filename, content) {
        // Store file
        this.currentFiles[filename] = {
            content: content,
            modified: false,
            timestamp: new Date().toISOString()
        };
        
        // Update file selector
        const selector = document.getElementById('debug-file-selector');
        if (selector) {
            const option = document.createElement('option');
            option.value = filename;
            option.textContent = filename;
            selector.appendChild(option);
            selector.value = filename;
        }
        
        // Load content into editor
        const editor = document.getElementById('code-editor-textarea');
        if (editor) {
            editor.value = content;
            this.updateEditorStats();
        }
    }
    
    updateEditorStats() {
        const editor = document.getElementById('code-editor-textarea');
        const lineCount = document.getElementById('editor-line-count');
        const charCount = document.getElementById('editor-char-count');
        
        if (editor && lineCount && charCount) {
            const lines = editor.value.split('\n').length;
            const chars = editor.value.length;
            
            lineCount.textContent = `Lines: ${lines}`;
            charCount.textContent = `Characters: ${chars}`;
        }
    }
    
    saveCurrentFile() {
        const selector = document.getElementById('debug-file-selector');
        const editor = document.getElementById('code-editor-textarea');
        
        if (selector && editor && selector.value) {
            const filename = selector.value;
            const content = editor.value;
            
            this.currentFiles[filename] = {
                content: content,
                modified: false,
                timestamp: new Date().toISOString()
            };
            
            console.log(`💾 Saved file: ${filename}`);
            this.addMessageToChat(`💾 Saved changes to ${filename}`, 'ai');
        }
    }
    
    async analyzeCurrentFile() {
        const selector = document.getElementById('debug-file-selector');
        if (!selector || !selector.value) return;
        
        const filename = selector.value;
        const fileData = this.currentFiles[filename];
        
        if (!fileData) return;
        
        // Send analysis request
        const message = `Please analyze this ${filename} file for potential issues and improvements:\n\n\`\`\`\n${fileData.content}\n\`\`\``;
        
        // Trigger analysis through chat
        const input = document.getElementById('debug-input');
        if (input) {
            input.value = message;
            this.sendMessage();
        }
    }
    
    displayAnalysisResults(analysis) {
        const resultsPanel = document.getElementById('analysis-results');
        const content = document.getElementById('analysis-content');
        
        if (resultsPanel && content) {
            content.innerHTML = `
                <div class="analysis-summary">
                    <h4>📋 Analysis Summary</h4>
                    <p>${analysis.analysis_summary || 'Analysis completed'}</p>
                </div>
                
                ${analysis.issues && analysis.issues.length > 0 ? `
                    <div class="analysis-section">
                        <h4>⚠️ Issues Found</h4>
                        <ul>
                            ${analysis.issues.map(issue => `<li>${issue}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${analysis.suggestions && analysis.suggestions.length > 0 ? `
                    <div class="analysis-section">
                        <h4>💡 Suggestions</h4>
                        <ul>
                            ${analysis.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
            
            resultsPanel.style.display = 'flex';
        }
        
        this.analysisResults = analysis;
    }
    
    addChangeSuggestion(suggestion) {
        const applyBtn = document.getElementById('editor-apply-suggestion');
        if (applyBtn) {
            applyBtn.style.display = 'block';
            applyBtn.onclick = () => this.applySuggestion(suggestion);
        }
    }
    
    applySuggestion(suggestion) {
        // Apply the AI suggestion to the current file
        const editor = document.getElementById('code-editor-textarea');
        if (editor && suggestion.new_code) {
            editor.value = suggestion.new_code;
            this.updateEditorStats();
            
            const applyBtn = document.getElementById('editor-apply-suggestion');
            if (applyBtn) {
                applyBtn.style.display = 'none';
            }
            
            this.addMessageToChat('✨ Applied AI suggestion to the code!', 'ai');
        }
    }
    
    handleAnalysisComplete(response) {
        this.hideTypingIndicator();
        console.log('✅ Analysis complete:', response);
    }
}

// Initialize debug client when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('debug-section')) {
        window.debugClient = new DebugClient();
    }
});

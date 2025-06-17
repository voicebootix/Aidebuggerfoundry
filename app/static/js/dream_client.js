/**
 * DreamEngine Frontend Client - FIXED VERSION (No ES6 Modules)
 * Compatible with standard HTML script tags
 */

(function() {
    'use strict';

    class DreamEngineClient {
        constructor(config = {}) {
            this.baseUrl = '/api/v1/dreamengine';
            this.userId = config.userId || this.generateUserId();
            this.activeRequests = new Map();
            this.eventSource = null;
            this.streamingActive = false;
            this.retryAttempts = 3;
            this.retryDelay = 1000;
           
            // Performance tracking
            this.performanceMetrics = {
                requestCount: 0,
                totalResponseTime: 0,
                errorCount: 0,
                streamingBytes: 0
            };
           
            this.initializeClient();
            console.log('🎯 DreamEngine Client initialized');
        }
       
        initializeClient() {
            this.setupConnectionMonitoring();
            this.validateApiEndpoints();
        }
       
        generateUserId() {
            return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
       
        async validateApiEndpoints() {
            try {
                const health = await this.checkHealth();
                console.log('✅ DreamEngine API health check passed:', health);
                return true;
            } catch (error) {
                console.warn('⚠️ DreamEngine API health check failed:', error.message);
                return false;
            }
        }
       
        setupConnectionMonitoring() {
            // Monitor online/offline status
            window.addEventListener('online', () => {
                console.log('🌐 Connection restored');
            });
           
            window.addEventListener('offline', () => {
                console.log('📱 Connection lost');
            });
        }
       
        async executeRequest(requestData) {
            const startTime = performance.now();
            this.performanceMetrics.requestCount++;
           
            try {
                console.log(`🚀 Making request to: ${this.baseUrl}${requestData.endpoint}`);
               
                const response = await fetch(`${this.baseUrl}${requestData.endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'User-Agent': 'DreamEngine-Client/1.0',
                        'X-Request-ID': requestData.id
                    },
                    body: JSON.stringify(requestData.data)
                });
               
                const responseTime = performance.now() - startTime;
                this.performanceMetrics.totalResponseTime += responseTime;
               
                console.log(`📡 Response status: ${response.status}`);
               
                if (!response.ok) {
                    this.performanceMetrics.errorCount++;
                    const errorData = await this.parseErrorResponse(response);
                    throw new Error(errorData.message || `API request failed with status ${response.status}`);
                }
               
                const result = await response.json();
               
                console.log(`✅ API Success: ${requestData.endpoint} (${responseTime.toFixed(0)}ms)`);
               
                return result;
            } catch (error) {
                this.performanceMetrics.errorCount++;
                console.error(`❌ API Error: ${requestData.endpoint}`, error);
                throw error;
            }
        }
       
        async parseErrorResponse(response) {
            try {
                const errorData = await response.json();
                return {
                    status: response.status,
                    message: errorData.detail || errorData.message || 'Unknown error',
                    code: errorData.code || 'UNKNOWN_ERROR'
                };
            } catch (e) {
                return {
                    status: response.status,
                    message: `HTTP ${response.status}: ${response.statusText}`,
                    code: 'HTTP_ERROR'
                };
            }
        }
       
        async processDream(inputText, options = {}) {
            if (!this.validateInput(inputText)) {
                throw new Error('Invalid input: Please provide a detailed description (minimum 10 characters)');
            }
           
            const requestId = this.generateRequestId();
            const requestData = {
                id: requestId,
                endpoint: '/process',
                data: {
                    id: requestId,
                    user_id: this.userId,
                    input_text: inputText.trim(),
                    options: this.sanitizeOptions(options)
                }
            };
           
            // Track request
            this.activeRequests.set(requestId, {
                startTime: Date.now(),
                status: 'processing',
                originalRequest: requestData,
                retryable: true
            });
           
            try {
                const result = await this.executeRequest(requestData);
               
                // Update request tracking
                this.activeRequests.set(requestId, {
                    ...this.activeRequests.get(requestId),
                    status: 'completed',
                    endTime: Date.now(),
                    result: result
                });
               
                return result;
            } catch (error) {
                // Update request tracking
                this.activeRequests.set(requestId, {
                    ...this.activeRequests.get(requestId),
                    status: 'failed',
                    endTime: Date.now(),
                    error: error.message
                });
               
                throw error;
            }
        }
       
        async validateIdea(inputText, options = {}) {
            if (!this.validateInput(inputText)) {
                throw new Error('Invalid input: Please provide a detailed description (minimum 10 characters)');
            }
           
            const requestId = this.generateRequestId();
            const requestData = {
                id: requestId,
                endpoint: '/validate',
                data: {
                    id: requestId,
                    user_id: this.userId,
                    input_text: inputText.trim(),
                    options: this.sanitizeOptions(options)
                }
            };
           
            try {
                const result = await this.executeRequest(requestData);
                return result;
            } catch (error) {
                throw error;
            }
        }
       
        async streamDreamGeneration(inputText, onProgress, onComplete, onError, options = {}) {
            if (!this.validateInput(inputText)) {
                if (onError) onError(new Error('Invalid input: Please provide a detailed description'));
                return null;
            }
           
            // Close any existing stream
            this.closeStream();
           
            const requestId = this.generateRequestId();
            const requestData = {
                id: requestId,
                user_id: this.userId,
                input_text: inputText.trim(),
                options: {
                    ...this.sanitizeOptions(options),
                    streaming: true
                }
            };
           
            try {
                console.log('🌊 Starting streaming request...');
               
                const response = await fetch(`${this.baseUrl}/stream`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Request-ID': requestId
                    },
                    body: JSON.stringify(requestData)
                });
               
                if (!response.ok) {
                    const errorData = await this.parseErrorResponse(response);
                    throw new Error(errorData.message);
                }
               
                this.streamingActive = true;
                this.handleServerSentEvents(response, requestId, onProgress, onComplete, onError);
               
                return requestId;
            } catch (error) {
                console.error('❌ Streaming failed:', error);
                if (onError) onError(error);
                return null;
            }
        }
       
        async handleServerSentEvents(response, requestId, onProgress, onComplete, onError) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            const chunks = [];
           
            try {
                while (this.streamingActive) {
                    const { done, value } = await reader.read();
                   
                    if (done) break;
                   
                    buffer += decoder.decode(value, { stream: true });
                    this.performanceMetrics.streamingBytes += value.length;
                   
                    const lines = buffer.split('\n');
                    buffer = lines.pop(); // Keep incomplete line
                   
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                           
                            if (data === '[DONE]') {
                                this.finishStreaming(chunks, requestId, onComplete);
                                return;
                            }
                           
                            try {
                                const chunk = JSON.parse(data);
                                chunks.push(chunk);
                               
                                // Call progress callback
                                if (onProgress) {
                                    onProgress({
                                        ...chunk,
                                        totalChunks: chunks.length,
                                        progress: this.calculateStreamProgress(chunk)
                                    });
                                }
                               
                                // Check for final chunk
                                if (chunk.is_final) {
                                    this.finishStreaming(chunks, requestId, onComplete);
                                    return;
                                }
                            } catch (parseError) {
                                console.warn('Failed to parse stream chunk:', data);
                            }
                        }
                    }
                }
            } catch (error) {
                if (onError) onError(error);
            } finally {
                reader.releaseLock();
                this.streamingActive = false;
            }
        }
       
        calculateStreamProgress(chunk) {
            return Math.min((chunk.chunk_index || 0) * 10, 95);
        }
       
        finishStreaming(chunks, requestId, onComplete) {
            this.closeStream();
           
            if (onComplete) {
                const assembledResult = this.assembleStreamResult(chunks, requestId);
                onComplete(assembledResult);
            }
        }
       
        assembleStreamResult(chunks, requestId) {
            const files = [];
            let currentFile = null;
            let explanation = '';
            let architecture = '';
           
            // Process chunks to rebuild the complete result
            chunks.forEach(chunk => {
                switch (chunk.content_type) {
                    case 'file_start':
                        currentFile = {
                            filename: chunk.file_path || 'generated_file.py',
                            content: '',
                            language: this.detectLanguage(chunk.file_path),
                            purpose: 'Generated code file'
                        };
                        break;
                       
                    case 'file_content':
                        if (currentFile) {
                            currentFile.content += chunk.content;
                        }
                        break;
                       
                    case 'file_end':
                        if (currentFile) {
                            files.push(currentFile);
                            currentFile = null;
                        }
                        break;
                       
                    case 'explanation':
                        explanation += chunk.content;
                        break;
                       
                    case 'architecture':
                        architecture += chunk.content;
                        break;
                       
                    case 'code_fragment':
                    default:
                        // Fallback: treat as generic code content
                        if (!currentFile) {
                            currentFile = {
                                filename: 'generated_code.py',
                                content: '',
                                language: 'python',
                                purpose: 'Generated code'
                            };
                        }
                        currentFile.content += chunk.content;
                        break;
                }
            });
           
            // Ensure any remaining file is added
            if (currentFile) {
                files.push(currentFile);
            }
           
            return {
                id: requestId,
                request_id: requestId,
                user_id: this.userId,
                status: 'success',
                message: 'Code generated successfully via streaming',
                files: files,
                main_file: files.length > 0 ? files[0].filename : null,
                explanation: explanation || 'Code generated via streaming',
                architecture: architecture || 'Generated architecture',
                project_type: 'web_api',
                programming_language: 'python',
                generation_time_seconds: (Date.now() - this.activeRequests.get(requestId)?.startTime || 0) / 1000,
                model_provider: 'auto',
                security_issues: [],
                quality_issues: [],
                deployment_steps: [],
                dependencies: [],
                environment_variables: []
            };
        }
       
        detectLanguage(filename) {
            if (!filename) return 'text';
           
            const extension = filename.split('.').pop()?.toLowerCase();
            const languageMap = {
                'py': 'python',
                'js': 'javascript',
                'ts': 'typescript',
                'java': 'java',
                'cpp': 'cpp',
                'c': 'c',
                'go': 'go',
                'rs': 'rust',
                'rb': 'ruby',
                'php': 'php',
                'swift': 'swift',
                'kt': 'kotlin',
                'cs': 'csharp',
                'html': 'html',
                'css': 'css',
                'sql': 'sql',
                'sh': 'bash',
                'yml': 'yaml',
                'yaml': 'yaml',
                'json': 'json',
                'xml': 'xml',
                'md': 'markdown'
            };
           
            return languageMap[extension] || 'text';
        }
       
        closeStream() {
            this.streamingActive = false;
            if (this.eventSource) {
                this.eventSource.close();
                this.eventSource = null;
            }
        }
       
        async checkHealth() {
            try {
                console.log('🏥 Checking API health...');
               
                const response = await fetch(`${this.baseUrl}/health`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
               
                if (!response.ok) {
                    throw new Error(`Health check failed: ${response.statusText}`);
                }
               
                const data = await response.json();
                console.log('✅ Health check successful:', data);
                return data;
            } catch (error) {
                console.error('❌ Health check failed:', error);
                throw new Error(`Health check error: ${error.message}`);
            }
        }
       
        validateInput(inputText) {
            return inputText &&
                   typeof inputText === 'string' &&
                   inputText.trim().length >= 10 &&
                   inputText.trim().length <= 10000;
        }
       
        sanitizeOptions(options) {
            const defaultOptions = {
                model_provider: 'auto',
                project_type: null,
                programming_language: null,
                database_type: null,
                security_level: 'standard',
                include_tests: true,
                include_documentation: true,
                include_docker: false,
                include_ci_cd: false,
                streaming: false,
                max_tokens: 8192,
                temperature: 0.7
            };
           
            // Merge with defaults and validate
            const sanitized = { ...defaultOptions, ...options };
           
            // Validate specific fields
            if (sanitized.temperature < 0 || sanitized.temperature > 1) {
                sanitized.temperature = 0.7;
            }
           
            if (sanitized.max_tokens < 100 || sanitized.max_tokens > 16384) {
                sanitized.max_tokens = 8192;
            }
           
            // Ensure boolean fields are actually booleans
            ['include_tests', 'include_documentation', 'include_docker', 'include_ci_cd', 'streaming'].forEach(field => {
                sanitized[field] = Boolean(sanitized[field]);
            });
           
            return sanitized;
        }
       
        generateRequestId() {
            return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
       
        // Draft management methods
        saveDraft(title, content, options = {}) {
            try {
                if (!content || content.trim().length < 10) {
                    throw new Error('Content too short to save as draft');
                }
               
                const drafts = this.loadDrafts();
                const draftId = this.generateRequestId();
               
                const draft = {
                    id: draftId,
                    title: title || `Draft ${new Date().toLocaleDateString()}`,
                    content: content.trim(),
                    options: this.sanitizeOptions(options),
                    timestamp: new Date().toISOString(),
                    version: '1.0'
                };
               
                drafts.push(draft);
               
                // Limit to 50 drafts maximum
                if (drafts.length > 50) {
                    drafts.splice(0, drafts.length - 50);
                }
               
                localStorage.setItem('dreamengine_drafts', JSON.stringify(drafts));
               
                console.log(`💾 Draft saved: ${draft.title}`);
                return draftId;
            } catch (error) {
                console.error('Failed to save draft:', error);
                throw new Error(`Failed to save draft: ${error.message}`);
            }
        }
       
        loadDrafts() {
            try {
                const draftsJson = localStorage.getItem('dreamengine_drafts');
                if (!draftsJson) return [];
               
                const drafts = JSON.parse(draftsJson);
               
                // Validate draft structure
                return drafts.filter(draft =>
                    draft &&
                    typeof draft === 'object' &&
                    draft.id &&
                    draft.content &&
                    draft.timestamp
                );
            } catch (error) {
                console.error('Failed to load drafts:', error);
                return [];
            }
        }
       
        loadDraft(draftId) {
            try {
                const drafts = this.loadDrafts();
                const draft = drafts.find(d => d.id === draftId);
               
                if (!draft) {
                    throw new Error('Draft not found');
                }
               
                console.log(`📂 Draft loaded: ${draft.title}`);
                return draft;
            } catch (error) {
                console.error('Failed to load draft:', error);
                throw new Error(`Failed to load draft: ${error.message}`);
            }
        }
       
        deleteDraft(draftId) {
            try {
                const drafts = this.loadDrafts();
                const initialLength = drafts.length;
                const filteredDrafts = drafts.filter(draft => draft.id !== draftId);
               
                if (filteredDrafts.length === initialLength) {
                    throw new Error('Draft not found');
                }
               
                localStorage.setItem('dreamengine_drafts', JSON.stringify(filteredDrafts));
               
                console.log(`🗑️ Draft deleted: ${draftId}`);
                return true;
            } catch (error) {
                console.error('Failed to delete draft:', error);
                throw new Error(`Failed to delete draft: ${error.message}`);
            }
        }
    }

    // Initialize and expose globally
    window.DreamEngineClient = DreamEngineClient;

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeDreamEngine);
    } else {
        initializeDreamEngine();
    }

    function initializeDreamEngine() {
        if (!window.dreamEngineClient) {
            window.dreamEngineClient = new DreamEngineClient();
            console.log('🎯 DreamEngine Client auto-initialized and ready');
        }
    }

})();


async handleStrategyValidation(ideaText) {
    console.log('🧠 Starting conversational strategy validation...');
    
    try {
        const response = await fetch('/api/v1/dream/validate-idea', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                idea: ideaText,
                user_id: 'anonymous',
                validation_depth: 'comprehensive'
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            this.currentStrategySession = data.session_id;
            this.displayConversationalValidation(data);
        } else {
            throw new Error(data.message || 'Strategy validation failed');
        }
        
    } catch (error) {
        console.error('❌ Strategy validation error:', error);
        this.showValidationError(error.message);
    }
}

displayConversationalValidation(data) {
    const validationResults = document.getElementById('validation-results');
    
    if (!validationResults) return;
    
    // Show initial analysis and start conversation
    validationResults.innerHTML = `
        <div class="strategy-conversation">
            <div class="conversation-header">
                <h3>🧠 Strategic Business Consultation</h3>
                <div class="conversation-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${data.conversation_context?.completeness || 15}%"></div>
                    </div>
                    <span>${data.conversation_context?.completeness || 15}% Complete</span>
                </div>
            </div>
            
            <!-- Initial Analysis -->
            <div class="analysis-card">
                <h4>📊 Initial Assessment</h4>
                <div class="assessment-grid">
                    <div class="metric">
                        <span class="metric-label">Opportunity Score</span>
                        <span class="metric-value">${data.initial_analysis?.initial_assessment?.opportunity_score || 'N/A'}/10</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Complexity</span>
                        <span class="metric-value">${data.initial_analysis?.initial_assessment?.complexity_level || 'Moderate'}</span>
                    </div>
                </div>
                
                <div class="insights-section">
                    <div class="challenges">
                        <h5>⚠️ Key Challenges</h5>
                        <ul>
                            ${(data.initial_analysis?.initial_assessment?.key_challenges || []).map(challenge => 
                                `<li>${challenge}</li>`
                            ).join('')}
                        </ul>
                    </div>
                    <div class="opportunities">
                        <h5>🚀 Immediate Opportunities</h5>
                        <ul>
                            ${(data.initial_analysis?.initial_assessment?.immediate_opportunities || []).map(opp => 
                                `<li>${opp}</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
            </div>
            
            <!-- Conversation Interface -->
            <div class="strategy-chat">
                <div class="chat-messages" id="strategy-messages">
                    <div class="ai-message">
                        <div class="message-content">
                            <p><strong>👋 Hi! I'm your strategic business consultant.</strong></p>
                            <p>I've done an initial assessment of your idea, and I'd like to dive deeper to give you comprehensive strategic advice.</p>
                            <p>Let's explore a few key areas that will determine your success:</p>
                        </div>
                    </div>
                </div>
                
                <div class="strategic-questions">
                    <h4>🎯 Strategic Questions</h4>
                    <div class="questions-container">
                        ${(data.next_questions || []).map((q, index) => 
                            `<div class="question-card" data-question="${q.question}">
                                <div class="question-header">
                                    <span class="question-category">${q.category}</span>
                                    <span class="importance ${q.importance}">${q.importance} priority</span>
                                </div>
                                <p class="question-text">${q.question}</p>
                                <button class="btn-secondary btn-sm answer-question" data-index="${index}">
                                    💬 Answer This
                                </button>
                            </div>`
                        ).join('')}
                    </div>
                </div>
                
                <div class="conversation-input" style="display: none;">
                    <textarea 
                        id="strategy-response-input" 
                        placeholder="Share your thoughts, experiences, and goals..."
                        rows="4"
                    ></textarea>
                    <div class="input-actions">
                        <button id="send-strategy-response" class="btn-primary">
                            Send Response
                        </button>
                        <button id="skip-question" class="btn-secondary">
                            Skip Question
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Bind conversation events
    this.bindStrategyConversationEvents();
    
    validationResults.style.display = 'block';
    validationResults.scrollIntoView({ behavior: 'smooth' });
}

bindStrategyConversationEvents() {
    // Answer question buttons
    document.querySelectorAll('.answer-question').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const questionText = e.target.closest('.question-card').dataset.question;
            this.startAnsweringQuestion(questionText);
        });
    });
    
    // Send response button
    const sendBtn = document.getElementById('send-strategy-response');
    if (sendBtn) {
        sendBtn.addEventListener('click', () => this.sendStrategyResponse());
    }
    
    // Skip question button
    const skipBtn = document.getElementById('skip-question');
    if (skipBtn) {
        skipBtn.addEventListener('click', () => this.skipCurrentQuestion());
    }
}

startAnsweringQuestion(questionText) {
    const conversationInput = document.querySelector('.conversation-input');
    const textarea = document.getElementById('strategy-response-input');
    
    if (conversationInput && textarea) {
        // Add question context to chat
        this.addStrategyMessage(`**Question:** ${questionText}`, 'ai');
        
        // Show input and focus
        conversationInput.style.display = 'block';
        textarea.placeholder = `Answer: ${questionText}`;
        textarea.focus();
        
        // Hide questions temporarily
        document.querySelector('.strategic-questions').style.display = 'none';
    }
}

async sendStrategyResponse() {
    const textarea = document.getElementById('strategy-response-input');
    const response = textarea.value.trim();
    
    if (!response || !this.currentStrategySession) return;
    
    // Add user response to chat
    this.addStrategyMessage(response, 'user');
    textarea.value = '';
    
    // Show typing indicator
    this.addStrategyMessage('💭 Analyzing your response...', 'ai', true);
    
    try {
        const result = await fetch('/api/v1/dream/continue-strategy-conversation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: this.currentStrategySession,
                user_response: response
            })
        });
        
        const data = await result.json();
        
        // Remove typing indicator
        this.removeTypingIndicator();
        
        if (data.status === 'analysis_complete') {
            this.displayFinalAnalysis(data.comprehensive_analysis);
        } else {
            this.continueStrategyConversation(data);
        }
        
    } catch (error) {
        this.removeTypingIndicator();
        this.addStrategyMessage('Sorry, there was an error processing your response. Please try again.', 'ai');
    }
}

continueStrategyConversation(data) {
    // Add AI response
    this.addStrategyMessage(data.ai_response, 'ai');
    
    // Update progress
    const progressBar = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.conversation-progress span');
    
    if (progressBar && data.conversation_context) {
        progressBar.style.width = `${data.conversation_context.completeness}%`;
        progressText.textContent = `${data.conversation_context.completeness}% Complete`;
    }
    
    // Show new questions if any
    if (data.strategic_questions && data.strategic_questions.length > 0) {
        this.displayNewQuestions(data.strategic_questions);
    }
    
    // Hide input temporarily
    document.querySelector('.conversation-input').style.display = 'none';
    document.querySelector('.strategic-questions').style.display = 'block';
}

displayNewQuestions(questions) {
    const questionsContainer = document.querySelector('.questions-container');
    
    questionsContainer.innerHTML = questions.map((q, index) => 
        `<div class="question-card" data-question="${q.question}">
            <div class="question-header">
                <span class="question-category">${q.category}</span>
                <span class="importance ${q.importance || 'medium'}">${q.importance || 'medium'} priority</span>
            </div>
            <p class="question-text">${q.question}</p>
            <button class="btn-secondary btn-sm answer-question" data-index="${index}">
                💬 Answer This
            </button>
        </div>`
    ).join('');
    
    // Re-bind events
    this.bindStrategyConversationEvents();
}

addStrategyMessage(message, sender, isTyping = false) {
    const messagesContainer = document.getElementById('strategy-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `${sender}-message ${isTyping ? 'typing-indicator' : ''}`;
    
    messageDiv.innerHTML = `
        <div class="message-content">
            ${message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

removeTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

displayFinalAnalysis(analysis) {
    // Hide conversation interface
    document.querySelector('.strategy-chat').style.display = 'none';
    
    // Show comprehensive analysis
    const validationResults = document.getElementById('validation-results');
    
    const analysisHTML = `
        <div class="final-analysis">
            <div class="analysis-header">
                <h3>📋 Comprehensive Strategic Analysis</h3>
                <div class="analysis-score">
                    <span class="score-value">${analysis.executive_summary?.confidence_score || 7.5}</span>
                    <span class="score-label">/ 10</span>
                </div>
            </div>
            
            <div class="executive-summary">
                <h4>🎯 Executive Summary</h4>
                <div class="summary-content">
                    <p><strong>Recommendation:</strong> ${analysis.executive_summary?.recommendation}</p>
                    <p><strong>Risk Level:</strong> ${analysis.executive_summary?.risk_level}</p>
                    <p><strong>Assessment:</strong> ${analysis.executive_summary?.opportunity_assessment}</p>
                </div>
            </div>
            
            <div class="analysis-sections">
                <div class="analysis-section">
                    <h4>📊 Market Analysis</h4>
                    <ul>
                        <li><strong>Target Market:</strong> ${analysis.market_analysis?.target_market}</li>
                        <li><strong>Competition Level:</strong> ${analysis.market_analysis?.competition_level}</li>
                        <li><strong>Market Size:</strong> ${analysis.market_analysis?.market_size_estimate}</li>
                    </ul>
                    <div class="strategy-list">
                        <h5>Market Entry Strategy:</h5>
                        <ul>
                            ${(analysis.market_analysis?.market_entry_strategy || []).map(step => 
                                `<li>${step}</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
                
                <div class="analysis-section">
                    <h4>💰 Business Model</h4>
                    <ul>
                        <li><strong>Revenue Streams:</strong> ${(analysis.business_model_assessment?.revenue_streams || []).join(', ')}</li>
                        <li><strong>Pricing Strategy:</strong> ${analysis.business_model_assessment?.pricing_strategy}</li>
                        <li><strong>Scalability:</strong> ${analysis.business_model_assessment?.scalability_potential}</li>
                    </ul>
                </div>
                
                <div class="analysis-section">
                    <h4>⚡ Technical Feasibility</h4>
                    <ul>
                        <li><strong>Complexity:</strong> ${analysis.technical_feasibility?.complexity_rating}</li>
                        <li><strong>Timeline:</strong> ${analysis.technical_feasibility?.development_timeline}</li>
                        <li><strong>Required Team:</strong> ${(analysis.technical_feasibility?.team_requirements || []).join(', ')}</li>
                        <li><strong>Technologies:</strong> ${(analysis.technical_feasibility?.required_technologies || []).join(', ')}</li>
                    </ul>
                </div>
                
                <div class="analysis-section risk-section">
                    <h4>⚠️ Risk Assessment</h4>
                    <div class="risk-levels">
                        <div class="high-risks">
                            <h5>High Risks:</h5>
                            <ul>
                                ${(analysis.risk_assessment?.high_risks || []).map(risk => 
                                    `<li>${risk}</li>`
                                ).join('')}
                            </ul>
                        </div>
                        <div class="mitigation-strategies">
                            <h5>Mitigation Strategies:</h5>
                            <ul>
                                ${(analysis.risk_assessment?.mitigation_strategies || []).map(strategy => 
                                    `<li>${strategy}</li>`
                                ).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="action-plan">
                <h4>🚀 Action Plan</h4>
                <div class="timeline-sections">
                    <div class="timeline-section">
                        <h5>Immediate Next Steps:</h5>
                        <ul>
                            ${(analysis.action_plan?.immediate_next_steps || []).map(step => 
                                `<li>${step}</li>`
                            ).join('')}
                        </ul>
                    </div>
                    <div class="timeline-section">
                        <h5>30-Day Goals:</h5>
                        <ul>
                            ${(analysis.action_plan?.['30_day_goals'] || []).map(goal => 
                                `<li>${goal}</li>`
                            ).join('')}
                        </ul>
                    </div>
                    <div class="timeline-section">
                        <h5>90-Day Goals:</h5>
                        <ul>
                            ${(analysis.action_plan?.['90_day_goals'] || []).map(goal => 
                                `<li>${goal}</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="analysis-actions">
                <button class="btn-primary" onclick="window.dreamClient.proceedToCodeGeneration()">
                    ✅ Proceed to Code Generation
                </button>
                <button class="btn-secondary" onclick="window.dreamClient.downloadAnalysis()">
                    📄 Download Analysis Report
                </button>
                <button class="btn-secondary" onclick="window.dreamClient.scheduleFollowUp()">
                    📅 Schedule Follow-up Consultation
                </button>
            </div>
        </div>
    `;
    
    validationResults.innerHTML = analysisHTML;
}

proceedToCodeGeneration() {
    // Auto-fill the main prompt with validated idea
    const ideaInput = document.getElementById('idea-input');
    if (ideaInput && this.validatedIdea) {
        ideaInput.value = this.validatedIdea;
        
        // Scroll to generation section
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.scrollIntoView({ behavior: 'smooth' });
            generateBtn.focus();
        }
    }
}

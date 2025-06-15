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

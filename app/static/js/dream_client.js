
/**
 * DreamEngine Frontend Client - Apple-Inspired Enhanced Version
 * Seamless integration with backend APIs and delightful user interactions
 */

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
        console.log('🎯 DreamEngine Client initialized with Apple-grade reliability');
    }
    
    initializeClient() {
        this.setupConnectionMonitoring();
        this.setupPerformanceTracking();
        this.validateApiEndpoints();
    }
    
    generateUserId() {
        return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    async validateApiEndpoints() {
        try {
            const health = await this.checkHealth();
            console.log('✅ DreamEngine API health check passed:', health);
        } catch (error) {
            console.warn('⚠️ DreamEngine API health check failed:', error.message);
        }
    }
    
    setupConnectionMonitoring() {
        // Monitor online/offline status
        window.addEventListener('online', () => {
            console.log('🌐 Connection restored');
            this.handleConnectionRestore();
        });
        
        window.addEventListener('offline', () => {
            console.log('📱 Connection lost');
            this.handleConnectionLoss();
        });
    }
    
    setupPerformanceTracking() {
        // Track performance metrics for optimization
        setInterval(() => {
            if (this.performanceMetrics.requestCount > 0) {
                const avgResponseTime = this.performanceMetrics.totalResponseTime / this.performanceMetrics.requestCount;
                console.log(`📊 Performance: ${avgResponseTime.toFixed(0)}ms avg, ${this.performanceMetrics.errorCount} errors`);
            }
        }, 30000); // Log every 30 seconds
    }
    
    handleConnectionRestore() {
        // Retry failed requests when connection is restored
        this.activeRequests.forEach((request, requestId) => {
            if (request.status === 'failed' && request.retryable) {
                this.retryRequest(requestId);
            }
        });
    }
    
    handleConnectionLoss() {
        // Gracefully handle connection loss
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
    }
    
    async retryRequest(requestId) {
        const request = this.activeRequests.get(requestId);
        if (!request || request.retries >= this.retryAttempts) {
            return false;
        }
        
        request.retries = (request.retries || 0) + 1;
        
        try {
            // Exponential backoff
            const delay = this.retryDelay * Math.pow(2, request.retries - 1);
            await this.sleep(delay);
            
            // Retry the original request
            const result = await this.executeRequest(request.originalRequest);
            request.status = 'completed';
            request.result = result;
            
            return true;
        } catch (error) {
            request.status = 'failed';
            request.lastError = error.message;
            return false;
        }
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    async executeRequest(requestData) {
        const startTime = performance.now();
        this.performanceMetrics.requestCount++;
        
        try {
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
            
            if (!response.ok) {
                this.performanceMetrics.errorCount++;
                const errorData = await this.parseErrorResponse(response);
                throw new Error(errorData.message || `API request failed with status ${response.status}`);
            }
            
            const result = await response.json();
            
            // Log successful requests for debugging
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
            
            // Validate response structure
            this.validateGenerationResult(result);
            
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
            this.validateValidationResult(result);
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
                            
                            // Call progress callback with enhanced data
                            if (onProgress) {
                                onProgress({
                                    ...chunk,
                                    totalChunks: chunks.length,
                                    bytesReceived: this.performanceMetrics.streamingBytes,
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
        // Estimate progress based on chunk metadata
        if (chunk.chunk_index && chunk.total_chunks) {
            return (chunk.chunk_index / chunk.total_chunks) * 100;
        }
        
        // Fallback: estimate based on content length
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
    
    async cancelGeneration(requestId) {
        try {
            await fetch(`${this.baseUrl}/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    request_id: requestId,
                    user_id: this.userId
                })
            });
            
            this.closeStream();
            
            // Update request status
            if (this.activeRequests.has(requestId)) {
                this.activeRequests.set(requestId, {
                    ...this.activeRequests.get(requestId),
                    status: 'cancelled',
                    endTime: Date.now()
                });
            }
            
            return true;
        } catch (error) {
            console.error('Failed to cancel generation:', error);
            return false;
        }
    }
    
    async checkHealth() {
        try {
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
            return data;
        } catch (error) {
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
    
    validateGenerationResult(result) {
        if (!result || typeof result !== 'object') {
            throw new Error('Invalid generation result: Expected object');
        }
        
        if (!result.id || !result.status) {
            throw new Error('Invalid generation result: Missing required fields');
        }
        
        if (result.status !== 'success') {
            throw new Error(result.message || 'Generation failed');
        }
        
        return true;
    }
    
    validateValidationResult(result) {
        if (!result || typeof result !== 'object') {
            throw new Error('Invalid validation result: Expected object');
        }
        
        if (typeof result.overall_score !== 'number') {
            throw new Error('Invalid validation result: Missing overall score');
        }
        
        return true;
    }
    
    generateRequestId() {
        return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    // Draft management methods with enhanced error handling
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
    
    exportDrafts() {
        try {
            const drafts = this.loadDrafts();
            const exportData = {
                version: '1.0',
                exported_at: new Date().toISOString(),
                user_id: this.userId,
                drafts: drafts
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
                type: 'application/json' 
            });
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `dreamengine-drafts-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            console.log(`📤 Exported ${drafts.length} drafts`);
            return true;
        } catch (error) {
            console.error('Failed to export drafts:', error);
            throw new Error(`Failed to export drafts: ${error.message}`);
        }
    }
    
    async importDrafts(file) {
        try {
            const text = await file.text();
            const importData = JSON.parse(text);
            
            if (!importData.drafts || !Array.isArray(importData.drafts)) {
                throw new Error('Invalid import file format');
            }
            
            const existingDrafts = this.loadDrafts();
            const newDrafts = importData.drafts.filter(draft => 
                draft && 
                typeof draft === 'object' && 
                draft.content
            );
            
            // Merge with existing drafts
            const mergedDrafts = [...existingDrafts, ...newDrafts];
            
            // Limit to 50 drafts
            if (mergedDrafts.length > 50) {
                mergedDrafts.splice(0, mergedDrafts.length - 50);
            }
            
            localStorage.setItem('dreamengine_drafts', JSON.stringify(mergedDrafts));
            
            console.log(`📥 Imported ${newDrafts.length} drafts`);
            return newDrafts.length;
        } catch (error) {
            console.error('Failed to import drafts:', error);
            throw new Error(`Failed to import drafts: ${error.message}`);
        }
    }
    
    // Analytics and performance methods
    getPerformanceMetrics() {
        return {
            ...this.performanceMetrics,
            averageResponseTime: this.performanceMetrics.requestCount > 0 
                ? this.performanceMetrics.totalResponseTime / this.performanceMetrics.requestCount 
                : 0,
            errorRate: this.performanceMetrics.requestCount > 0 
                ? (this.performanceMetrics.errorCount / this.performanceMetrics.requestCount) * 100 
                : 0,
            activeRequests: this.activeRequests.size,
            isStreaming: this.streamingActive
        };
    }
    
    getRequestHistory() {
        const history = [];
        this.activeRequests.forEach((request, id) => {
            history.push({
                id: id,
                status: request.status,
                startTime: request.startTime,
                endTime: request.endTime,
                duration: request.endTime ? request.endTime - request.startTime : null,
                error: request.error || null
            });
        });
        
        return history.sort((a, b) => b.startTime - a.startTime);
    }
    
    clearRequestHistory() {
        this.activeRequests.clear();
        this.performanceMetrics = {
            requestCount: 0,
            totalResponseTime: 0,
            errorCount: 0,
            streamingBytes: 0
        };
        
        console.log('🧹 Request history cleared');
    }
    
    // Debug and development helpers
    enableDebugMode() {
        this.debugMode = true;
        console.log('🐛 Debug mode enabled');
        
        // Override console methods to add timestamps
        const originalLog = console.log;
        const originalError = console.error;
        const originalWarn = console.warn;
        
        console.log = (...args) => originalLog(`[${new Date().toISOString()}] [LOG]`, ...args);
        console.error = (...args) => originalError(`[${new Date().toISOString()}] [ERROR]`, ...args);
        console.warn = (...args) => originalWarn(`[${new Date().toISOString()}] [WARN]`, ...args);
    }
    
    disableDebugMode() {
        this.debugMode = false;
        console.log('🐛 Debug mode disabled');
    }
    
    // Network quality assessment
    async assessNetworkQuality() {
        const startTime = performance.now();
        
        try {
            await this.checkHealth();
            const responseTime = performance.now() - startTime;
            
            let quality = 'excellent';
            if (responseTime > 1000) quality = 'poor';
            else if (responseTime > 500) quality = 'fair';
            else if (responseTime > 200) quality = 'good';
            
            return {
                responseTime: responseTime,
                quality: quality,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                responseTime: null,
                quality: 'offline',
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }
    
    // Cleanup method
    destroy() {
        this.closeStream();
        this.activeRequests.clear();
        
        // Remove event listeners
        window.removeEventListener('online', this.handleConnectionRestore);
        window.removeEventListener('offline', this.handleConnectionLoss);
        
        console.log('🔄 DreamEngine Client destroyed');
    }
}

/**
 * Enhanced Event Emitter for DreamEngine Client
 */
class DreamEngineEventEmitter {
    constructor() {
        this.events = {};
    }
    
    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
    }
    
    off(event, callback) {
        if (this.events[event]) {
            this.events[event] = this.events[event].filter(cb => cb !== callback);
        }
    }
    
    emit(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }
    
    once(event, callback) {
        const onceCallback = (data) => {
            callback(data);
            this.off(event, onceCallback);
        };
        this.on(event, onceCallback);
    }
}

// Enhanced DreamEngine Client with events
class EnhancedDreamEngineClient extends DreamEngineClient {
    constructor(config = {}) {
        super(config);
        this.events = new DreamEngineEventEmitter();
        
        // Emit client ready event
        setTimeout(() => {
            this.events.emit('client:ready', {
                userId: this.userId,
                timestamp: new Date().toISOString()
            });
        }, 100);
    }
    
    async processDream(inputText, options = {}) {
        this.events.emit('generation:start', {
            inputLength: inputText.length,
            options: options
        });
        
        try {
            const result = await super.processDream(inputText, options);
            
            this.events.emit('generation:success', {
                result: result,
                duration: result.generation_time_seconds
            });
            
            return result;
        } catch (error) {
            this.events.emit('generation:error', {
                error: error.message,
                inputText: inputText
            });
            
            throw error;
        }
    }
    
    async streamDreamGeneration(inputText, onProgress, onComplete, onError, options = {}) {
        this.events.emit('streaming:start', {
            inputLength: inputText.length,
            options: options
        });
        
        const enhancedOnProgress = (data) => {
            this.events.emit('streaming:progress', data);
            if (onProgress) onProgress(data);
        };
        
        const enhancedOnComplete = (result) => {
            this.events.emit('streaming:complete', result);
            if (onComplete) onComplete(result);
        };
        
        const enhancedOnError = (error) => {
            this.events.emit('streaming:error', { error: error.message });
            if (onError) onError(error);
        };
        
        return await super.streamDreamGeneration(
            inputText, 
            enhancedOnProgress, 
            enhancedOnComplete, 
            enhancedOnError, 
            options
        );
    }
}

// Initialize and export
window.DreamEngineClient = EnhancedDreamEngineClient;
window.DreamEngineEventEmitter = DreamEngineEventEmitter;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (!window.dreamEngineClient) {
        window.dreamEngineClient = new EnhancedDreamEngineClient();
        
        // Set up global event handlers for debugging
        window.dreamEngineClient.events.on('generation:start', (data) => {
            console.log('🚀 Generation started:', data);
        });
        
        window.dreamEngineClient.events.on('generation:success', (data) => {
            console.log('✅ Generation completed:', data);
        });
        
        window.dreamEngineClient.events.on('generation:error', (data) => {
            console.error('❌ Generation failed:', data);
        });
        
        console.log('🎯 DreamEngine Client auto-initialized and ready');
    }
});

export { EnhancedDreamEngineClient as DreamEngineClient, DreamEngineEventEmitter };
Made with

/**
 * DreamEngine Frontend Client
 * Integrates with AI Debugger Factory UI patterns
 * 
 * This client provides a seamless interface to the DreamEngine backend,
 * allowing users to convert natural language descriptions into deployable code.
 */

class DreamEngineClient {
    /**
     * Initialize the DreamEngine client
     * @param {Object} config - Configuration options
     */
    constructor(config = {}) {
        this.baseUrl = '/api/v1/dreamengine';
        this.userId = config.userId || this.generateUserId();
        this.activeRequests = new Map();
        this.eventSource = null;
        this.streamingActive = false;
        this.loadingOverlay = document.getElementById('loading-overlay');
        
        // Initialize storage for drafts
        this.initializeStorage();
        
        // Bind methods to maintain 'this' context
        this.processDream = this.processDream.bind(this);
        this.streamDreamGeneration = this.streamDreamGeneration.bind(this);
        this.validateIdea = this.validateIdea.bind(this);
        this.checkHealth = this.checkHealth.bind(this);
        this.cancelRequest = this.cancelRequest.bind(this);
        this.saveDraft = this.saveDraft.bind(this);
        this.loadDraft = this.loadDraft.bind(this);
        this.clearDrafts = this.clearDrafts.bind(this);
    }
    
    /**
     * Generate a unique user ID if not provided
     * @returns {string} - Generated UUID
     */
    generateUserId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    /**
     * Initialize local storage for drafts
     */
    initializeStorage() {
        if (!localStorage.getItem('dreamEngineDrafts')) {
            localStorage.setItem('dreamEngineDrafts', JSON.stringify([]));
        }
    }
    
    /**
     * Process a dream request
     * @param {string} inputText - Natural language description
     * @param {Object} options - Generation options
     * @returns {Promise<Object>} - Generation result
     */
    async processDream(inputText, options = {}) {
        if (!inputText || inputText.trim().length < 10) {
            throw new Error('Please provide a more detailed description (at least 10 characters)');
        }
        
        const requestId = this.generateUserId();
        
        // Show loading overlay
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.remove('hidden');
        }
        
        // Prepare request data
        const requestData = {
            id: requestId,
            user_id: this.userId,
            input_text: inputText,
            options: options
        };
        
        console.log('Sending dream request:', requestData);
        
        try {
            // Track this request
            this.activeRequests.set(requestId, {
                startTime: Date.now(),
                status: 'processing',
                inputText: inputText
            });
            
            // Call the API
            const response = await fetch(`${this.baseUrl}/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`API request failed: ${errorData.message || response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Dream API response:', data);
            
            // Update request tracking
            this.activeRequests.set(requestId, {
                ...this.activeRequests.get(requestId),
                status: 'completed',
                endTime: Date.now(),
                result: data
            });
            
            // Hide loading overlay
            if (this.loadingOverlay) {
                this.loadingOverlay.classList.add('hidden');
            }
            
            return data;
        } catch (error) {
            console.error('Error:', error);
            
            // Update request tracking
            this.activeRequests.set(requestId, {
                ...this.activeRequests.get(requestId),
                status: 'failed',
                endTime: Date.now(),
                error: error.message
            });
            
            // Hide loading overlay
            if (this.loadingOverlay) {
                this.loadingOverlay.classList.add('hidden');
            }
            
            throw error;
        }
    }
    
    /**
     * Stream dream generation with real-time updates
     * @param {string} inputText - Natural language description
     * @param {Function} onProgress - Progress callback
     * @param {Function} onComplete - Completion callback
     * @param {Object} options - Generation options
     * @returns {string} - Request ID
     */
    streamDreamGeneration(inputText, onProgress, onComplete, options = {}) {
        if (!inputText || inputText.trim().length < 10) {
            throw new Error('Please provide a more detailed description (at least 10 characters)');
        }
        
        // Close any existing stream
        this.closeStream();
        
        const requestId = this.generateUserId();
        
        // Prepare request data
        const requestData = {
            id: requestId,
            user_id: this.userId,
            input_text: inputText,
            options: {
                ...options,
                streaming: true
            }
        };
        
        console.log('Starting streaming dream generation:', requestData);
        
        // Track this request
        this.activeRequests.set(requestId, {
            startTime: Date.now(),
            status: 'streaming',
            inputText: inputText
        });
        
        // Set up event source for server-sent events
        const queryParams = new URLSearchParams({
            request_id: requestId,
            user_id: this.userId
        }).toString();
        
        this.eventSource = new EventSource(`${this.baseUrl}/stream?${queryParams}`);
        this.streamingActive = true;
        
        // Collect chunks for final result
        const chunks = [];
        
        // Handle incoming events
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                chunks.push(data);
                
                // Call progress callback
                if (onProgress && typeof onProgress === 'function') {
                    onProgress(data);
                }
                
                // Check if this is the final chunk
                if (data.is_final) {
                    this.closeStream();
                    
                    // Assemble complete result
                    const completeResult = this.assembleStreamResult(chunks);
                    
                    // Update request tracking
                    this.activeRequests.set(requestId, {
                        ...this.activeRequests.get(requestId),
                        status: 'completed',
                        endTime: Date.now(),
                        result: completeResult
                    });
                    
                    // Call completion callback
                    if (onComplete && typeof onComplete === 'function') {
                        onComplete(completeResult);
                    }
                }
            } catch (error) {
                console.error('Error processing stream chunk:', error);
            }
        };
        
        // Handle errors
        this.eventSource.onerror = (error) => {
            console.error('Stream error:', error);
            this.closeStream();
            
            // Update request tracking
            this.activeRequests.set(requestId, {
                ...this.activeRequests.get(requestId),
                status: 'failed',
                endTime: Date.now(),
                error: 'Stream connection error'
            });
            
            // Call completion callback with error
            if (onComplete && typeof onComplete === 'function') {
                onComplete(null, new Error('Stream connection error'));
            }
        };
        
        // Initiate the stream by posting the request
        fetch(`${this.baseUrl}/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        }).catch(error => {
            console.error('Error initiating stream:', error);
            this.closeStream();
            
            // Update request tracking
            this.activeRequests.set(requestId, {
                ...this.activeRequests.get(requestId),
                status: 'failed',
                endTime: Date.now(),
                error: error.message
            });
        });
        
        return requestId;
    }
    
    /**
     * Close the active stream
     */
    closeStream() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            this.streamingActive = false;
        }
    }
    
    /**
     * Assemble complete result from stream chunks
     * @param {Array} chunks - Stream chunks
     * @returns {Object} - Complete result
     */
    assembleStreamResult(chunks) {
        // Group chunks by file path
        const fileChunks = {};
        const textChunks = [];
        
        chunks.forEach(chunk => {
            if (chunk.file_path) {
                if (!fileChunks[chunk.file_path]) {
                    fileChunks[chunk.file_path] = [];
                }
                fileChunks[chunk.file_path].push(chunk);
            } else {
                textChunks.push(chunk);
            }
        });
        
        // Assemble files
        const files = Object.keys(fileChunks).map(filePath => {
            const sortedChunks = fileChunks[filePath].sort((a, b) => a.chunk_index - b.chunk_index);
            const content = sortedChunks.map(chunk => chunk.content).join('');
            
            return {
                filename: filePath,
                content: content,
                language: this.detectLanguageFromFilename(filePath),
                purpose: 'Generated code file'
            };
        });
        
        // Assemble explanation from text chunks
        const explanation = textChunks
            .filter(chunk => chunk.content_type === 'text')
            .sort((a, b) => a.chunk_index - b.chunk_index)
            .map(chunk => chunk.content)
            .join('');
        
        // Find the last chunk which should contain the final metadata
        const finalChunk = chunks.find(chunk => chunk.is_final);
        const requestId = chunks[0]?.request_id || '';
        
        // Construct result object
        return {
            id: this.generateUserId(),
            request_id: requestId,
            user_id: this.userId,
            status: 'success',
            message: 'Code generated successfully',
            timestamp: new Date().toISOString(),
            files: files,
            explanation: explanation,
            architecture: explanation.split('\n\n')[0] || 'Generated architecture',
            generation_time_seconds: (Date.now() - this.activeRequests.get(requestId)?.startTime || 0) / 1000,
            ...(finalChunk?.metadata || {})
        };
    }
    
    /**
     * Detect programming language from filename
     * @param {string} filename - Filename
     * @returns {string} - Detected language
     */
    detectLanguageFromFilename(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        
        const extensionMap = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'html': 'html',
            'css': 'css',
            'java': 'java',
            'cs': 'csharp',
            'go': 'go',
            'rs': 'rust',
            'rb': 'ruby',
            'php': 'php',
            'swift': 'swift',
            'kt': 'kotlin',
            'cpp': 'cpp',
            'c': 'c',
            'h': 'c',
            'hpp': 'cpp',
            'md': 'markdown',
            'json': 'json',
            'yaml': 'yaml',
            'yml': 'yaml',
            'xml': 'xml',
            'sql': 'sql',
            'sh': 'shell',
            'bat': 'batch',
            'ps1': 'powershell',
            'dockerfile': 'dockerfile',
            'dockerignore': 'dockerignore',
            'gitignore': 'gitignore'
        };
        
        return extensionMap[extension] || 'text';
    }
    
    /**
     * Validate an idea before generation
     * @param {string} inputText - Natural language description
     * @param {Object} options - Validation options
     * @returns {Promise<Object>} - Validation result
     */
    async validateIdea(inputText, options = {}) {
        if (!inputText || inputText.trim().length < 10) {
            throw new Error('Please provide a more detailed description (at least 10 characters)');
        }
        
        // Show loading overlay
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.remove('hidden');
        }
        
        // Prepare request data
        const requestData = {
            id: this.generateUserId(),
            user_id: this.userId,
            input_text: inputText,
            options: options
        };
        
        console.log('Sending validation request:', requestData);
        
        try {
            // Call the API
            const response = await fetch(`${this.baseUrl}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`API request failed: ${errorData.message || response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Validation API response:', data);
            
            // Hide loading overlay
            if (this.loadingOverlay) {
                this.loadingOverlay.classList.add('hidden');
            }
            
            return data;
        } catch (error) {
            console.error('Error:', error);
            
            // Hide loading overlay
            if (this.loadingOverlay) {
                this.loadingOverlay.classList.add('hidden');
            }
            
            throw error;
        }
    }
    
    /**
     * Check DreamEngine health status
     * @returns {Promise<Object>} - Health status
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            
            if (!response.ok) {
                throw new Error(`Health check failed: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Health check response:', data);
            
            return data;
        } catch (error) {
            console.error('Health check error:', error);
            throw error;
        }
    }
    
    /**
     * Cancel an active request
     * @param {string} requestId - Request ID to cancel
     * @returns {Promise<boolean>} - Success status
     */
    async cancelRequest(requestId) {
        if (!this.activeRequests.has(requestId)) {
            return false;
        }
        
        // If streaming, close the stream
        if (this.streamingActive && this.eventSource) {
            this.closeStream();
        }
        
        try {
            // Call cancel endpoint
            const response = await fetch(`${this.baseUrl}/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    request_id: requestId,
                    user_id: this.userId
                })
            });
            
            if (!response.ok) {
                console.error('Failed to cancel request:', response.statusText);
                return false;
            }
            
            // Update request tracking
            this.activeRequests.set(requestId, {
                ...this.activeRequests.get(requestId),
                status: 'cancelled',
                endTime: Date.now()
            });
            
            return true;
        } catch (error) {
            console.error('Error cancelling request:', error);
            return false;
        }
    }
    
    /**
     * Save a draft to local storage
     * @param {string} title - Draft title
     * @param {string} content - Draft content
     * @param {Object} options - Draft options
     * @returns {string} - Draft ID
     */
    saveDraft(title, content, options = {}) {
        const drafts = JSON.parse(localStorage.getItem('dreamEngineDrafts') || '[]');
        
        const draftId = this.generateUserId();
        const draft = {
            id: draftId,
            title: title || 'Untitled Draft',
            content: content,
            options: options,
            timestamp: new Date().toISOString()
        };
        
        drafts.push(draft);
        localStorage.setItem('dreamEngineDrafts', JSON.stringify(drafts));
        
        return draftId;
    }
    
    /**
     * Load drafts from local storage
     * @returns {Array} - List of drafts
     */
    loadDrafts() {
        return JSON.parse(localStorage.getItem('dreamEngineDrafts') || '[]');
    }
    
    /**
     * Load a specific draft by ID
     * @param {string} draftId - Draft ID
     * @returns {Object|null} - Draft object or null if not found
     */
    loadDraft(draftId) {
        const drafts = this.loadDrafts();
        return drafts.find(draft => draft.id === draftId) || null;
    }
    
    /**
     * Delete a draft by ID
     * @param {string} draftId - Draft ID
     * @returns {boolean} - Success status
     */
    deleteDraft(draftId) {
        const drafts = this.loadDrafts();
        const filteredDrafts = drafts.filter(draft => draft.id !== draftId);
        
        if (filteredDrafts.length === drafts.length) {
            return false; // Draft not found
        }
        
        localStorage.setItem('dreamEngineDrafts', JSON.stringify(filteredDrafts));
        return true;
    }
    
    /**
     * Clear all drafts
     */
    clearDrafts() {
        localStorage.setItem('dreamEngineDrafts', JSON.stringify([]));
    }
    
    /**
     * Get active request status
     * @param {string} requestId - Request ID
     * @returns {Object|null} - Request status or null if not found
     */
    getRequestStatus(requestId) {
        return this.activeRequests.get(requestId) || null;
    }
    
    /**
     * Get all active requests
     * @returns {Array} - List of active requests
     */
    getAllRequests() {
        return Array.from(this.activeRequests.entries()).map(([id, request]) => ({
            id,
            ...request
        }));
    }
}

/**
 * DreamEngine UI Manager
 * Handles UI interactions for DreamEngine
 */
class DreamEngineUI {
    /**
     * Initialize the DreamEngine UI
     * @param {DreamEngineClient} client - DreamEngine client instance
     */
    constructor(client) {
        this.client = client;
        this.editorContainer = document.getElementById('dream-editor-container');
        this.resultContainer = document.getElementById('dream-result-container');
        this.validationContainer = document.getElementById('dream-validation-container');
        this.codeDisplay = document.getElementById('dream-code-display');
        this.fileSelector = document.getElementById('dream-file-selector');
        this.progressBar = document.getElementById('dream-progress-bar');
        this.progressStatus = document.getElementById('dream-progress-status');
        
        // Bind methods
        this.setupEventListeners = this.setupEventListeners.bind(this);
        this.handleGenerateClick = this.handleGenerateClick.bind(this);
        this.handleValidateClick = this.handleValidateClick.bind(this);
        this.handleStreamingClick = this.handleStreamingClick.bind(this);
        this.handleCancelClick = this.handleCancelClick.bind(this);
        this.handleSaveDraftClick = this.handleSaveDraftClick.bind(this);
        this.handleLoadDraftClick = this.handleLoadDraftClick.bind(this);
        this.displayResult = this.displayResult.bind(this);
        this.displayValidation = this.displayValidation.bind(this);
        this.updateProgress = this.updateProgress.bind(this);
        this.showError = this.showError.bind(this);
        
        // Initialize UI
        this.setupEventListeners();
    }
    
    /**
     * Set up event listeners for UI elements
     */
    setupEventListeners() {
        // Generate button
        const generateBtn = document.getElementById('dream-generate-button');
        if (generateBtn) {
            generateBtn.addEventListener('click', this.handleGenerateClick);
        }
        
        // Validate button
        const validateBtn = document.getElementById('dream-validate-button');
        if (validateBtn) {
            validateBtn.addEventListener('click', this.handleValidateClick);
        }
        
        // Streaming button
        const streamingBtn = document.getElementById('dream-streaming-button');
        if (streamingBtn) {
            streamingBtn.addEventListener('click', this.handleStreamingClick);
        }
        
        // Cancel button
        const cancelBtn = document.getElementById('dream-cancel-button');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', this.handleCancelClick);
        }
        
        // Save draft button
        const saveDraftBtn = document.getElementById('dream-save-draft-button');
        if (saveDraftBtn) {
            saveDraftBtn.addEventListener('click', this.handleSaveDraftClick);
        }
        
        // Load draft button
        const loadDraftBtn = document.getElementById('dream-load-draft-button');
        if (loadDraftBtn) {
            loadDraftBtn.addEventListener('click', this.handleLoadDraftClick);
        }
        
        // File selector
        if (this.fileSelector) {
            this.fileSelector.addEventListener('change', (e) => {
                const selectedFile = e.target.value;
                this.displaySelectedFile(selectedFile);
            });
        }
    }
    
    /**
     * Handle generate button click
     */
    async handleGenerateClick() {
        const inputText = document.getElementById('dream-input').value;
        const options = this.getOptions();
        
        if (!inputText || inputText.trim().length < 10) {
            this.showError('Please provide a more detailed description (at least 10 characters)');
            return;
        }
        
        try {
            // Reset UI
            this.resetUI();
            
            // Show progress
            this.updateProgress(0, 'Starting code generation...');
            
            // Process dream
            const result = await this.client.processDream(inputText, options);
            
            // Display result
            this.displayResult(result);
            
            // Update progress
            this.updateProgress(100, 'Code generation complete!');
        } catch (error) {
            console.error('Error generating code:', error);
            this.showError(`Error generating code: ${error.message}`);
            this.updateProgress(0, 'Generation failed');
        }
    }
    
    /**
     * Handle validate button click
     */
    async handleValidateClick() {
        const inputText = document.getElementById('dream-input').value;
        
        if (!inputText || inputText.trim().length < 10) {
            this.showError('Please provide a more detailed description (at least 10 characters)');
            return;
        }
        
        try {
            // Reset UI
            this.resetUI();
            
            // Show progress
            this.updateProgress(0, 'Validating idea...');
            
            // Validate idea
            const result = await this.client.validateIdea(inputText);
            
            // Display validation result
            this.displayValidation(result);
            
            // Update progress
            this.updateProgress(100, 'Validation complete!');
        } catch (error) {
            console.error('Error validating idea:', error);
            this.showError(`Error validating idea: ${error.message}`);
            this.updateProgress(0, 'Validation failed');
        }
    }
    
    /**
     * Handle streaming button click
     */
    handleStreamingClick() {
        const inputText = document.getElementById('dream-input').value;
        const options = this.getOptions();
        
        if (!inputText || inputText.trim().length < 10) {
            this.showError('Please provide a more detailed description (at least 10 characters)');
            return;
        }
        
        try {
            // Reset UI
            this.resetUI();
            
            // Show progress
            this.updateProgress(0, 'Starting streaming code generation...');
            
            // Initialize result containers
            if (this.resultContainer) {
                this.resultContainer.classList.remove('hidden');
            }
            
            if (this.codeDisplay) {
                this.codeDisplay.textContent = '';
            }
            
            // Track files and content
            const files = {};
            let currentProgress = 0;
            
            // Start streaming
            const requestId = this.client.streamDreamGeneration(
                inputText,
                // Progress callback
                (chunk) => {
                    // Update progress
                    currentProgress += 1;
                    this.updateProgress(
                        Math.min(95, currentProgress), 
                        `Generating code... (chunk ${chunk.chunk_index})`
                    );
                    
                    // Handle file chunks
                    if (chunk.file_path) {
                        if (!files[chunk.file_path]) {
                            files[chunk.file_path] = '';
                            
                            // Add to file selector
                            if (this.fileSelector) {
                                const option = document.createElement('option');
                                option.value = chunk.file_path;
                                option.textContent = chunk.file_path;
                                this.fileSelector.appendChild(option);
                            }
                        }
                        
                        files[chunk.file_path] += chunk.content;
                        
                        // If this is the currently selected file, update display
                        if (this.fileSelector && this.fileSelector.value === chunk.file_path) {
                            if (this.codeDisplay) {
                                this.codeDisplay.textContent = files[chunk.file_path];
                            }
                        }
                    } else if (chunk.content_type === 'text') {
                        // Display explanation text
                        const explanationElement = document.getElementById('dream-explanation');
                        if (explanationElement) {
                            explanationElement.textContent = (explanationElement.textContent || '') + chunk.content;
                        }
                    }
                },
                // Complete callback
                (result, error) => {
                    if (error) {
                        console.error('Streaming error:', error);
                        this.showError(`Streaming error: ${error.message}`);
                        this.updateProgress(0, 'Streaming failed');
                        return;
                    }
                    
                    // Display complete result
                    this.displayResult(result);
                    
                    // Update progress
                    this.updateProgress(100, 'Code generation complete!');
                },
                options
            );
            
            // Store request ID for potential cancellation
            this.currentRequestId = requestId;
        } catch (error) {
            console.error('Error starting streaming:', error);
            this.showError(`Error starting streaming: ${error.message}`);
            this.updateProgress(0, 'Streaming failed');
        }
    }
    
    /**
     * Handle cancel button click
     */
    async handleCancelClick() {
        if (this.currentRequestId) {
            const success = await this.client.cancelRequest(this.currentRequestId);
            
            if (success) {
                this.updateProgress(0, 'Generation cancelled');
            } else {
                this.showError('Failed to cancel request');
            }
            
            this.currentRequestId = null;
        }
    }
    
    /**
     * Handle save draft button click
     */
    handleSaveDraftClick() {
        const inputText = document.getElementById('dream-input').value;
        
        if (!inputText || inputText.trim().length === 0) {
            this.showError('Nothing to save');
            return;
        }
        
        const title = prompt('Enter a title for this draft:', 'My Dream Project');
        
        if (!title) {
            return; // User cancelled
        }
        
        const options = this.getOptions();
        const draftId = this.client.saveDraft(title, inputText, options);
        
        alert(`Draft saved successfully! ID: ${draftId}`);
    }
    
    /**
     * Handle load draft button click
     */
    handleLoadDraftClick() {
        const drafts = this.client.loadDrafts();
        
        if (drafts.length === 0) {
            alert('No drafts found');
            return;
        }
        
        // Create draft selection dialog
        const draftList = drafts.map((draft, index) => 
            `${index + 1}. ${draft.title} (${new Date(draft.timestamp).toLocaleString()})`
        ).join('\n');
        
        const selection = prompt(`Select a draft to load:\n\n${draftList}\n\nEnter number:`);
        
        if (!selection) {
            return; // User cancelled
        }
        
        const index = parseInt(selection) - 1;
        
        if (isNaN(index) || index < 0 || index >= drafts.length) {
            alert('Invalid selection');
            return;
        }
        
        const draft = drafts[index];
        
        // Load draft content
        const inputElement = document.getElementById('dream-input');
        if (inputElement) {
            inputElement.value = draft.content;
        }
        
        // Load draft options
        this.setOptions(draft.options);
        
        alert(`Draft "${draft.title}" loaded successfully!`);
    }
    
    /**
     * Get options from UI
     * @returns {Object} - Options object
     */
    getOptions() {
        const options = {};
        
        // Model provider
        const providerSelect = document.getElementById('dream-provider-select');
        if (providerSelect) {
            options.model_provider = providerSelect.value;
        }
        
        // Project type
        const projectTypeSelect = document.getElementById('dream-project-type-select');
        if (projectTypeSelect) {
            options.project_type = projectTypeSelect.value;
        }
        
        // Programming language
        const languageSelect = document.getElementById('dream-language-select');
        if (languageSelect) {
            options.programming_language = languageSelect.value;
        }
        
        // Database type
        const databaseSelect = document.getElementById('dream-database-select');
        if (databaseSelect) {
            options.database_type = databaseSelect.value;
        }
        
        // Security level
        const securitySelect = document.getElementById('dream-security-select');
        if (securitySelect) {
            options.security_level = securitySelect.value;
        }
        
        // Include tests
        const includeTestsCheckbox = document.getElementById('dream-include-tests-checkbox');
        if (includeTestsCheckbox) {
            options.include_tests = includeTestsCheckbox.checked;
        }
        
        // Include documentation
        const includeDocsCheckbox = document.getElementById('dream-include-docs-checkbox');
        if (includeDocsCheckbox) {
            options.include_documentation = includeDocsCheckbox.checked;
        }
        
        // Include Docker
        const includeDockerCheckbox = document.getElementById('dream-include-docker-checkbox');
        if (includeDockerCheckbox) {
            options.include_docker = includeDockerCheckbox.checked;
        }
        
        // Include CI/CD
        const includeCiCdCheckbox = document.getElementById('dream-include-cicd-checkbox');
        if (includeCiCdCheckbox) {
            options.include_ci_cd = includeCiCdCheckbox.checked;
        }
        
        return options;
    }
    
    /**
     * Set options in UI
     * @param {Object} options - Options object
     */
    setOptions(options) {
        if (!options) {
            return;
        }
        
        // Model provider
        const providerSelect = document.getElementById('dream-provider-select');
        if (providerSelect && options.model_provider) {
            providerSelect.value = options.model_provider;
        }
        
        // Project type
        const projectTypeSelect = document.getElementById('dream-project-type-select');
        if (projectTypeSelect && options.project_type) {
            projectTypeSelect.value = options.project_type;
        }
        
        // Programming language
        const languageSelect = document.getElementById('dream-language-select');
        if (languageSelect && options.programming_language) {
            languageSelect.value = options.programming_language;
        }
        
        // Database type
        const databaseSelect = document.getElementById('dream-database-select');
        if (databaseSelect && options.database_type) {
            databaseSelect.value = options.database_type;
        }
        
        // Security level
        const securitySelect = document.getElementById('dream-security-select');
        if (securitySelect && options.security_level) {
            securitySelect.value = options.security_level;
        }
        
        // Include tests
        const includeTestsCheckbox = document.getElementById('dream-include-tests-checkbox');
        if (includeTestsCheckbox && options.include_tests !== undefined) {
            includeTestsCheckbox.checked = options.include_tests;
        }
        
        // Include documentation
        const includeDocsCheckbox = document.getElementById('dream-include-docs-checkbox');
        if (includeDocsCheckbox && options.include_documentation !== undefined) {
            includeDocsCheckbox.checked = options.include_documentation;
        }
        
        // Include Docker
        const includeDockerCheckbox = document.getElementById('dream-include-docker-checkbox');
        if (includeDockerCheckbox && options.include_docker !== undefined) {
            includeDockerCheckbox.checked = options.include_docker;
        }
        
        // Include CI/CD
        const includeCiCdCheckbox = document.getElementById('dream-include-cicd-checkbox');
        if (includeCiCdCheckbox && options.include_ci_cd !== undefined) {
            includeCiCdCheckbox.checked = options.include_ci_cd;
        }
    }
    
    /**
     * Display generation result
     * @param {Object} result - Generation result
     */
    displayResult(result) {
        if (!result) {
            return;
        }
        
        // Show result container
        if (this.resultContainer) {
            this.resultContainer.classList.remove('hidden');
        }
        
        // Update file selector
        if (this.fileSelector) {
            // Clear existing options
            this.fileSelector.innerHTML = '';
            
            // Add files
            result.files.forEach(file => {
                const option = document.createElement('option');
                option.value = file.filename;
                option.textContent = file.filename;
                this.fileSelector.appendChild(option);
            });
            
            // Select first file
            if (result.files.length > 0) {
                this.fileSelector.value = result.files[0].filename;
                this.displaySelectedFile(result.files[0].filename);
            }
        }
        
        // Update explanation
        const explanationElement = document.getElementById('dream-explanation');
        if (explanationElement) {
            explanationElement.textContent = result.explanation || '';
        }
        
        // Update architecture
        const architectureElement = document.getElementById('dream-architecture');
        if (architectureElement) {
            architectureElement.textContent = result.architecture || '';
        }
        
        // Update deployment steps
        const deploymentElement = document.getElementById('dream-deployment-steps');
        if (deploymentElement && result.deployment_steps) {
            deploymentElement.innerHTML = '';
            
            result.deployment_steps.forEach(step => {
                const stepElement = document.createElement('div');
                stepElement.className = 'dream-deployment-step';
                
                const stepTitle = document.createElement('h4');
                stepTitle.textContent = `Step ${step.step_number}: ${step.description}`;
                stepElement.appendChild(stepTitle);
                
                if (step.command) {
                    const commandElement = document.createElement('pre');
                    commandElement.className = 'dream-command';
                    commandElement.textContent = step.command;
                    stepElement.appendChild(commandElement);
                }
                
                if (step.verification) {
                    const verificationElement = document.createElement('p');
                    verificationElement.className = 'dream-verification';
                    verificationElement.textContent = `Verification: ${step.verification}`;
                    stepElement.appendChild(verificationElement);
                }
                
                deploymentElement.appendChild(stepElement);
            });
        }
        
        // Update dependencies
        const dependenciesElement = document.getElementById('dream-dependencies');
        if (dependenciesElement && result.dependencies) {
            dependenciesElement.innerHTML = '';
            
            const list = document.createElement('ul');
            result.dependencies.forEach(dep => {
                const item = document.createElement('li');
                item.textContent = dep;
                list.appendChild(item);
            });
            
            dependenciesElement.appendChild(list);
        }
        
        // Update environment variables
        const envVarsElement = document.getElementById('dream-env-vars');
        if (envVarsElement && result.environment_variables) {
            envVarsElement.innerHTML = '';
            
            const list = document.createElement('ul');
            result.environment_variables.forEach(env => {
                const item = document.createElement('li');
                item.textContent = env;
                list.appendChild(item);
            });
            
            envVarsElement.appendChild(list);
        }
        
        // Update generation time
        const timeElement = document.getElementById('dream-generation-time');
        if (timeElement) {
            timeElement.textContent = `${result.generation_time_seconds.toFixed(2)} seconds`;
        }
    }
    
    /**
     * Display selected file
     * @param {string} filename - Selected filename
     */
    displaySelectedFile(filename) {
        if (!this.codeDisplay || !this.currentRequestId) {
            return;
        }
        
        const request = this.client.getRequestStatus(this.currentRequestId);
        
        if (!request || !request.result || !request.result.files) {
            return;
        }
        
        const file = request.result.files.find(f => f.filename === filename);
        
        if (file) {
            this.codeDisplay.textContent = file.content;
            
            // Apply syntax highlighting if available
            if (window.hljs) {
                window.hljs.highlightElement(this.codeDisplay);
            }
        }
    }
    
    /**
     * Display validation result
     * @param {Object} result - Validation result
     */
    displayValidation(result) {
        if (!result) {
            return;
        }
        
        // Show validation container
        if (this.validationContainer) {
            this.validationContainer.classList.remove('hidden');
        }
        
        // Update overall score
        const scoreElement = document.getElementById('dream-validation-score');
        if (scoreElement) {
            const score = result.overall_score * 100;
            scoreElement.textContent = `${score.toFixed(1)}%`;
            
            // Update score color
            if (score >= 80) {
                scoreElement.className = 'dream-score-high';
            } else if (score >= 60) {
                scoreElement.className = 'dream-score-medium';
            } else {
                scoreElement.className = 'dream-score-low';
            }
        }
        
        // Update summary
        const summaryElement = document.getElementById('dream-validation-summary');
        if (summaryElement) {
            summaryElement.textContent = result.summary || '';
        }
        
        // Update detected project type
        const projectTypeElement = document.getElementById('dream-detected-project-type');
        if (projectTypeElement) {
            projectTypeElement.textContent = result.detected_project_type || 'Unknown';
        }
        
        // Update detected language
        const languageElement = document.getElementById('dream-detected-language');
        if (languageElement) {
            languageElement.textContent = result.detected_language || 'Unknown';
        }
        
        // Update detected database
        const databaseElement = document.getElementById('dream-detected-database');
        if (databaseElement) {
            databaseElement.textContent = result.detected_database || 'None';
        }
        
        // Update estimated time
        const timeElement = document.getElementById('dream-estimated-time');
        if (timeElement) {
            timeElement.textContent = result.estimated_time || 'Unknown';
        }
        
        // Update scores
        this.updateScoreDisplay('dream-feasibility-score', result.feasibility);
        this.updateScoreDisplay('dream-complexity-score', result.complexity);
        this.updateScoreDisplay('dream-clarity-score', result.clarity);
        this.updateScoreDisplay('dream-security-score', result.security_considerations);
    }
    
    /**
     * Update score display
     * @param {string} elementId - Element ID
     * @param {Object} scoreData - Score data
     */
    updateScoreDisplay(elementId, scoreData) {
        if (!scoreData) {
            return;
        }
        
        const container = document.getElementById(elementId);
        if (!container) {
            return;
        }
        
        // Clear container
        container.innerHTML = '';
        
        // Create score display
        const scoreElement = document.createElement('div');
        scoreElement.className = 'dream-score';
        
        const score = scoreData.score * 100;
        scoreElement.textContent = `${score.toFixed(1)}%`;
        
        // Set score color
        if (score >= 80) {
            scoreElement.classList.add('dream-score-high');
        } else if (score >= 60) {
            scoreElement.classList.add('dream-score-medium');
        } else {
            scoreElement.classList.add('dream-score-low');
        }
        
        container.appendChild(scoreElement);
        
        // Add explanation
        const explanationElement = document.createElement('div');
        explanationElement.className = 'dream-score-explanation';
        explanationElement.textContent = scoreData.explanation || '';
        container.appendChild(explanationElement);
        
        // Add recommendations
        if (scoreData.recommendations && scoreData.recommendations.length > 0) {
            const recommendationsElement = document.createElement('ul');
            recommendationsElement.className = 'dream-recommendations';
            
            scoreData.recommendations.forEach(rec => {
                const item = document.createElement('li');
                item.textContent = rec;
                recommendationsElement.appendChild(item);
            });
            
            container.appendChild(recommendationsElement);
        }
    }
    
    /**
     * Update progress bar and status
     * @param {number} percent - Progress percentage
     * @param {string} status - Status message
     */
    updateProgress(percent, status) {
        if (this.progressBar) {
            this.progressBar.style.width = `${percent}%`;
            this.progressBar.setAttribute('aria-valuenow', percent);
        }
        
        if (this.progressStatus) {
            this.progressStatus.textContent = status || '';
        }
    }
    
    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        const errorElement = document.getElementById('dream-error');
        
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorElement.classList.add('hidden');
            }, 5000);
        } else {
            alert(`Error: ${message}`);
        }
    }
    
    /**
     * Reset UI elements
     */
    resetUI() {
        // Hide result and validation containers
        if (this.resultContainer) {
            this.resultContainer.classList.add('hidden');
        }
        
        if (this.validationContainer) {
            this.validationContainer.classList.add('hidden');
        }
        
        // Clear file selector
        if (this.fileSelector) {
            this.fileSelector.innerHTML = '';
        }
        
        // Clear code display
        if (this.codeDisplay) {
            this.codeDisplay.textContent = '';
        }
        
        // Reset progress
        this.updateProgress(0, '');
        
        // Hide error
        const errorElement = document.getElementById('dream-error');
        if (errorElement) {
            errorElement.classList.add('hidden');
        }
    }
}

// Initialize DreamEngine when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if dream engine container exists
    const dreamContainer = document.getElementById('dream-engine-container');
    
    if (!dreamContainer) {
        console.warn('DreamEngine container not found. Skipping initialization.');
        return;
    }
    
    console.log('Initializing DreamEngine client...');
    
    // Initialize client
    const client = new DreamEngineClient();
    
    // Initialize UI
    const ui = new DreamEngineUI(client);
    
    // Check health status
    client.checkHealth()
        .then(status => {
            console.log('DreamEngine health status:', status);
            
            // Update status indicator if it exists
            const statusIndicator = document.querySelector('.dream-status-indicator');
            if (statusIndicator && status.status === 'healthy') {
                statusIndicator.classList.add('online');
                statusIndicator.classList.remove('offline');
            }
        })
        .catch(error => {
            console.error('DreamEngine health check error:', error);
            
            // Update status indicator if it exists
            const statusIndicator = document.querySelector('.dream-status-indicator');
            if (statusIndicator) {
                statusIndicator.classList.remove('online');
                statusIndicator.classList.add('offline');
            }
        });
    
    // Make client and UI available globally
    window.dreamEngineClient = client;
    window.dreamEngineUI = ui;
});

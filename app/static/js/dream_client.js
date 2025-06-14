
/**
 * DreamEngine Frontend Client - FIXED VERSION
 * Integrates with AI Debugger Factory UI patterns
 */

class DreamEngineClient {
    constructor(config = {}) {
        this.baseUrl = '/api/v1/dreamengine';
        this.userId = config.userId || this.generateUserId();
        this.activeRequests = new Map();
        this.eventSource = null;
        this.streamingActive = false;
        this.loadingOverlay = document.getElementById('loading-overlay');
        
        // Initialize storage for drafts
        this.initializeStorage();
        
        console.log('DreamEngine Client initialized with baseUrl:', this.baseUrl);
    }
    
    generateUserId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    initializeStorage() {
        if (!localStorage.getItem('dreamEngineDrafts')) {
            localStorage.setItem('dreamEngineDrafts', JSON.stringify([]));
        }
    }
    
    async processDream(inputText, options = {}) {
        if (!inputText || inputText.trim().length < 10) {
            throw new Error('Please provide a more detailed description (at least 10 characters)');
        }
        
        const requestId = this.generateUserId();
        
        console.log('Processing dream request:', { inputText, options });
        
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
        
        try {
            // Track this request
            this.activeRequests.set(requestId, {
                startTime: Date.now(),
                status: 'processing',
                inputText: inputText
            });
            
            console.log('Sending request to:', `${this.baseUrl}/process`);
            
            // Call the API
            const response = await fetch(`${this.baseUrl}/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                let errorMessage = `API request failed with status ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || errorMessage;
                } catch (e) {
                    // If we can't parse the error response, use the status text
                    errorMessage = `${response.status} ${response.statusText}`;
                }
                throw new Error(errorMessage);
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
            console.error('Error in processDream:', error);
            
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
    
    async validateIdea(inputText, options = {}) {
        if (!inputText || inputText.trim().length < 10) {
            throw new Error('Please provide a more detailed description (at least 10 characters)');
        }
        
        console.log('Validating idea:', inputText);
        
        // Show loading overlay
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.remove('hidden');
        }
        
        const requestData = {
            id: this.generateUserId(),
            user_id: this.userId,
            input_text: inputText,
            options: options
        };
        
        try {
            const response = await fetch(`${this.baseUrl}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                let errorMessage = `Validation failed with status ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || errorMessage;
                } catch (e) {
                    errorMessage = `${response.status} ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }
            
            const data = await response.json();
            console.log('Validation API response:', data);
            
            // Hide loading overlay
            if (this.loadingOverlay) {
                this.loadingOverlay.classList.add('hidden');
            }
            
            return data;
        } catch (error) {
            console.error('Error in validateIdea:', error);
            
            // Hide loading overlay
            if (this.loadingOverlay) {
                this.loadingOverlay.classList.add('hidden');
            }
            
            throw error;
        }
    }
    
    streamDreamGeneration(inputText, onProgress, onComplete, options = {}) {
        if (!inputText || inputText.trim().length < 10) {
            throw new Error('Please provide a more detailed description (at least 10 characters)');
        }
        
        console.log('Starting streaming generation:', inputText);
        
        // Close any existing stream
        this.closeStream();
        
        const requestId = this.generateUserId();
        
        const requestData = {
            id: requestId,
            user_id: this.userId,
            input_text: inputText,
            options: {
                ...options,
                streaming: true
            }
        };
        
        // Track this request
        this.activeRequests.set(requestId, {
            startTime: Date.now(),
            status: 'streaming',
            inputText: inputText
        });
        
        // Set up event source for server-sent events
        this.eventSource = new EventSource(`${this.baseUrl}/stream`);
        this.streamingActive = true;
        
        const chunks = [];
        
        // Handle incoming events
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                chunks.push(data);
                
                console.log('Received stream chunk:', data);
                
                // Call progress callback
                if (onProgress && typeof onProgress === 'function') {
                    onProgress(data);
                }
                
                // Check if this is the final chunk
                if (data.is_final) {
                    this.closeStream();
                    
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
        });
        
        return requestId;
    }
    
    closeStream() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            this.streamingActive = false;
        }
    }
    
    assembleStreamResult(chunks) {
        // Simple assembly for now - in a real implementation this would be more sophisticated
        const content = chunks.map(chunk => chunk.content).join('');
        
        return {
            id: this.generateUserId(),
            status: 'success',
            message: 'Code generated successfully via streaming',
            files: [{
                filename: 'generated_code.py',
                content: content,
                language: 'python',
                purpose: 'Generated code'
            }],
            explanation: 'Code generated via streaming',
            architecture: 'Generated architecture',
            generation_time_seconds: 0
        };
    }
    
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
    
    // Draft management methods
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
    
    loadDrafts() {
        return JSON.parse(localStorage.getItem('dreamEngineDrafts') || '[]');
    }
    
    loadDraft(draftId) {
        const drafts = this.loadDrafts();
        return drafts.find(draft => draft.id === draftId) || null;
    }
    
    deleteDraft(draftId) {
        const drafts = this.loadDrafts();
        const filteredDrafts = drafts.filter(draft => draft.id !== draftId);
        
        if (filteredDrafts.length === drafts.length) {
            return false;
        }
        
        localStorage.setItem('dreamEngineDrafts', JSON.stringify(filteredDrafts));
        return true;
    }
}

/**
 * DreamEngine UI Manager - FIXED VERSION
 */
class DreamEngineUI {
    constructor(client) {
        this.client = client;
        console.log('DreamEngine UI Manager initialized');
        
        // Wait for DOM to be ready before setting up
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupEventListeners());
        } else {
            this.setupEventListeners();
        }
    }
    
    setupEventListeners() {
        console.log('Setting up DreamEngine event listeners');
        
        // Validate Idea button
        const validateBtn = document.getElementById('dream-validate-button') || 
                           document.querySelector('[data-action="validate"]') ||
                           document.querySelector('button:contains("Validate")');
        
        if (validateBtn) {
            validateBtn.addEventListener('click', () => this.handleValidateClick());
            console.log('Validate button listener attached');
        } else {
            console.warn('Validate button not found');
        }
        
        // Generate Code button  
        const generateBtn = document.getElementById('dream-generate-button') ||
                           document.querySelector('[data-action="generate"]') ||
                           document.querySelector('button:contains("Generate")');
        
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.handleGenerateClick());
            console.log('Generate button listener attached');
        } else {
            console.warn('Generate button not found');
        }
        
        // Stream Generation button
        const streamBtn = document.getElementById('dream-streaming-button') ||
                         document.querySelector('[data-action="stream"]') ||
                         document.querySelector('button:contains("Stream")');
        
        if (streamBtn) {
            streamBtn.addEventListener('click', () => this.handleStreamingClick());
            console.log('Stream button listener attached');
        } else {
            console.warn('Stream button not found');
        }
        
        // Cancel button
        const cancelBtn = document.getElementById('dream-cancel-button') ||
                         document.querySelector('[data-action="cancel"]');
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.handleCancelClick());
        }
        
        // Draft buttons
        const saveDraftBtn = document.getElementById('dream-save-draft-button');
        if (saveDraftBtn) {
            saveDraftBtn.addEventListener('click', () => this.handleSaveDraftClick());
        }
        
        const loadDraftBtn = document.getElementById('dream-load-draft-button');
        if (loadDraftBtn) {
            loadDraftBtn.addEventListener('click', () => this.handleLoadDraftClick());
        }
    }
    
    getInputText() {
        // Try different possible input field IDs
        const inputField = document.getElementById('dream-input') ||
                          document.getElementById('prompt-editor') ||
                          document.querySelector('textarea[placeholder*="vision"]') ||
                          document.querySelector('textarea[placeholder*="idea"]') ||
                          document.querySelector('textarea');
        
        if (!inputField) {
            console.error('Input field not found');
            return '';
        }
        
        return inputField.value.trim();
    }
    
    setStatus(message, type = 'info') {
        console.log(`Status [${type}]: ${message}`);
        
        // Try to find status display elements
        const statusElements = [
            document.querySelector('.dream-status'),
            document.querySelector('.generation-status'),
            document.querySelector('.status-message')
        ];
        
        statusElements.forEach(element => {
            if (element) {
                element.textContent = message;
                element.className = `status-message ${type}`;
            }
        });
        
        // Also log to console for debugging
        if (type === 'error') {
            console.error(message);
        } else {
            console.log(message);
        }
    }
    
    async handleValidateClick() {
        console.log('Validate button clicked');
        
        const inputText = this.getInputText();
        
        if (!inputText || inputText.length < 10) {
            this.setStatus('Please provide a more detailed description (at least 10 characters)', 'error');
            return;
        }
        
        try {
            this.setStatus('Validating your idea...', 'info');
            
            const result = await this.client.validateIdea(inputText);
            
            this.setStatus('Validation completed successfully!', 'success');
            console.log('Validation result:', result);
            
            // Display validation results
            this.displayValidationResult(result);
            
        } catch (error) {
            console.error('Validation error:', error);
            this.setStatus(`Validation failed: ${error.message}`, 'error');
        }
    }
    
    async handleGenerateClick() {
        console.log('Generate button clicked');
        
        const inputText = this.getInputText();
        
        if (!inputText || inputText.length < 10) {
            this.setStatus('Please provide a more detailed description (at least 10 characters)', 'error');
            return;
        }
        
        try {
            this.setStatus('Generating code...', 'info');
            
            const options = this.getGenerationOptions();
            const result = await this.client.processDream(inputText, options);
            
            this.setStatus('Code generated successfully!', 'success');
            console.log('Generation result:', result);
            
            // Display generation results
            this.displayGenerationResult(result);
            
        } catch (error) {
            console.error('Generation error:', error);
            this.setStatus(`Generation failed: ${error.message}`, 'error');
        }
    }
    
    handleStreamingClick() {
        console.log('Stream button clicked');
        
        const inputText = this.getInputText();
        
        if (!inputText || inputText.length < 10) {
            this.setStatus('Please provide a more detailed description (at least 10 characters)', 'error');
            return;
        }
        
        try {
            this.setStatus('Starting streaming generation...', 'info');
            
            const options = this.getGenerationOptions();
            
            const requestId = this.client.streamDreamGeneration(
                inputText,
                // Progress callback
                (chunk) => {
                    this.setStatus(`Generating... (chunk ${chunk.chunk_index})`, 'info');
                    console.log('Stream chunk received:', chunk);
                },
                // Complete callback
                (result, error) => {
                    if (error) {
                        console.error('Streaming error:', error);
                        this.setStatus(`Streaming failed: ${error.message}`, 'error');
                        return;
                    }
                    
                    this.setStatus('Streaming completed successfully!', 'success');
                    console.log('Streaming result:', result);
                    this.displayGenerationResult(result);
                },
                options
            );
            
            console.log('Streaming started with request ID:', requestId);
            
        } catch (error) {
            console.error('Streaming error:', error);
            this.setStatus(`Streaming failed: ${error.message}`, 'error');
        }
    }
    
    handleCancelClick() {
        console.log('Cancel button clicked');
        this.client.closeStream();
        this.setStatus('Generation cancelled', 'info');
    }
    
    handleSaveDraftClick() {
        const inputText = this.getInputText();
        
        if (!inputText || inputText.trim().length === 0) {
            this.setStatus('Nothing to save', 'error');
            return;
        }
        
        const title = prompt('Enter a title for this draft:', 'My Dream Project');
        
        if (!title) {
            return; // User cancelled
        }
        
        const options = this.getGenerationOptions();
        const draftId = this.client.saveDraft(title, inputText, options);
        
        this.setStatus(`Draft "${title}" saved successfully!`, 'success');
    }
    
    handleLoadDraftClick() {
        const drafts = this.client.loadDrafts();
        
        if (drafts.length === 0) {
            alert('No drafts found');
            return;
        }
        
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
        const inputField = document.getElementById('dream-input') ||
                          document.getElementById('prompt-editor') ||
                          document.querySelector('textarea');
        
        if (inputField) {
            inputField.value = draft.content;
        }
        
        this.setStatus(`Draft "${draft.title}" loaded successfully!`, 'success');
    }
    
    getGenerationOptions() {
        // Extract options from the UI
        const options = {};
        
        // Try to get model provider
        const providerSelect = document.getElementById('dream-provider-select');
        if (providerSelect) {
            options.model_provider = providerSelect.value;
        }
        
        // Add more option extraction as needed
        return options;
    }
    
    displayValidationResult(result) {
        console.log('Displaying validation result:', result);
        this.setStatus('Validation completed - check console for details', 'success');
    }
    
    displayGenerationResult(result) {
        console.log('Displaying generation result:', result);
        this.setStatus('Code generated - check console for details', 'success');
        
        // Try to display in code area if it exists
        const codeDisplay = document.getElementById('code-display') ||
                           document.querySelector('.code-display') ||
                           document.querySelector('pre');
        
        if (codeDisplay && result.files && result.files.length > 0) {
            codeDisplay.textContent = result.files[0].content;
        }
    }
}

// Initialize DreamEngine when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing DreamEngine...');
    
    // Initialize client
    const client = new DreamEngineClient();
    
    // Initialize UI
    const ui = new DreamEngineUI(client);
    
    // Check health status
    client.checkHealth()
        .then(status => {
            console.log('DreamEngine health status:', status);
        })
        .catch(error => {
            console.error('DreamEngine health check error:', error);
        });
    
    // Make client and UI available globally for debugging
    window.dreamEngineClient = client;
    window.dreamEngineUI = ui;
    
    console.log('DreamEngine initialization complete');
});
Made with

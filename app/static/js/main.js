/**
 * DreamEngine - Complete Working JavaScript
 * Single file solution to avoid conflicts
 */

// Global DreamEngine object
window.DreamEngine = {
    client: null,
    ui: null,
    activeSection: 'build',
    isGenerating: false,
   
    // Initialize everything
    init: function() {
        console.log('🚀 Initializing DreamEngine...');
        this.client = new DreamEngineClient();
        this.ui = new DreamEngineUI();
        this.setupGlobalEvents();
    },
   
    setupGlobalEvents: function() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('Page hidden - pausing operations');
            } else {
                console.log('Page visible - resuming operations');
                this.checkSystemHealth();
            }
        });
    },
   
    checkSystemHealth: async function() {
        try {
            const health = await this.client.checkHealth();
            this.ui.updateStatusIndicator('online', 'System Online');
        } catch (error) {
            this.ui.updateStatusIndicator('offline', 'System Offline');
        }
    }
};

/**
 * DreamEngine Client - Handles API communication
 */
class DreamEngineClient {
    constructor() {
        this.baseUrl = '/api/v1/dreamengine';
        this.userId = this.generateUserId();
        console.log('🎯 DreamEngine Client initialized');
    }
   
    generateUserId() {
        return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
   
    async makeRequest(endpoint, data = null, method = 'GET') {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
       
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
       
        try {
            const response = await fetch(url, options);
           
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
           
            return await response.json();
        } catch (error) {
            console.error(`❌ API Error: ${endpoint}`, error);
            throw error;
        }
    }
   
    async checkHealth() {
        return await this.makeRequest('/health');
    }
   
    async validateIdea(inputText, options = {}) {
        return await this.makeRequest('/validate', {
            id: this.generateRequestId(),
            user_id: this.userId,
            input_text: inputText,
            options: options
        }, 'POST');
    }
   
    async generateCode(inputText, options = {}) {
        return await this.makeRequest('/process', {
            id: this.generateRequestId(),
            user_id: this.userId,
            input_text: inputText,
            options: options
        }, 'POST');
    }
   
    async processVoice(audioBlob) {
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.webm');
       
        const response = await fetch('/api/v1/voice', {
            method: 'POST',
            body: formData
        });
       
        if (!response.ok) {
            throw new Error('Voice processing failed');
        }
       
        return await response.json();
    }
   
    generateRequestId() {
        return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
}

/**
 * DreamEngine UI - Handles all user interface interactions
 */
class DreamEngineUI {
    constructor() {
        this.optionsExpanded = false;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.setupEventListeners();
        console.log('🎨 DreamEngine UI initialized');
    }
   
    setupEventListeners() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.bindEvents());
        } else {
            this.bindEvents();
        }
    }
   
    bindEvents() {
        console.log('🔗 Binding UI events...');
       
        // Navigation
        this.bindNavigation();
       
        // Input area
        this.bindInputEvents();
       
        // Action buttons
        this.bindActionButtons();
       
        // Options
        this.bindOptions();
       
        // Voice input
        this.bindVoiceInput();
       
        // Templates
        this.bindTemplates();
       
        // File operations
        this.bindFileOperations();
       
        // Info tabs
        this.bindInfoTabs();
       
        // Draft management
        this.bindDraftManagement();
       
        console.log('✅ All events bound successfully');
    }
   
    bindNavigation() {
        const navPills = document.querySelectorAll('.nav-pill');
        navPills.forEach(pill => {
            pill.addEventListener('click', (e) => {
                e.preventDefault();
                const section = pill.dataset.section;
                this.switchSection(section);
            });
        });
    }
   
    switchSection(sectionName) {
        // Update active nav pill
        document.querySelectorAll('.nav-pill').forEach(pill => {
            pill.classList.remove('active');
        });
       
        const activeNav = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }
       
        // Update active section
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
       
        const activeSection = document.getElementById(`${sectionName}-section`);
        if (activeSection) {
            activeSection.classList.add('active');
        }
       
        DreamEngine.activeSection = sectionName;
        window.scrollTo({ top: 0, behavior: 'smooth' });
       
        this.showNotification(`Switched to ${sectionName} section`, 'info');
    }
   
    bindInputEvents() {
        const dreamInput = document.getElementById('dream-input');
        const charCount = document.getElementById('char-count');
       
        if (dreamInput) {
            dreamInput.addEventListener('input', () => {
                this.updateCharacterCount();
                this.autoResizeTextarea(dreamInput);
            });
        }
    }
   
    updateCharacterCount() {
        const dreamInput = document.getElementById('dream-input');
        const charCountElement = document.getElementById('char-count');
       
        if (dreamInput && charCountElement) {
            const count = dreamInput.value.length;
            charCountElement.textContent = count;
           
            // Update color based on count
            const inputMeta = document.querySelector('.input-meta');
            if (inputMeta) {
                if (count < 50) {
                    inputMeta.style.color = '#ff9500';
                } else if (count > 5000) {
                    inputMeta.style.color = '#ff3b30';
                } else {
                    inputMeta.style.color = '#8e8e93';
                }
            }
        }
    }
   
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        const newHeight = Math.min(textarea.scrollHeight, 300);
        textarea.style.height = newHeight + 'px';
    }
   
    bindActionButtons() {
        // Validate button
        const validateBtn = document.getElementById('dream-validate-button');
        if (validateBtn) {
            validateBtn.addEventListener('click', () => this.handleValidate());
        }
       
        // Generate button
        const generateBtn = document.getElementById('dream-generate-button');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.handleGenerate());
        }
       
        // Streaming button
        const streamBtn = document.getElementById('dream-streaming-button');
        if (streamBtn) {
            streamBtn.addEventListener('click', () => this.handleStreaming());
        }
       
        // New project button
        const newProjectBtn = document.getElementById('new-project-button');
        if (newProjectBtn) {
            newProjectBtn.addEventListener('click', () => this.handleNewProject());
        }
    }
   
    async handleValidate() {
        const input = this.getInputText();
        if (!this.validateInput(input)) return;
       
        this.showLoading('Validating your idea...');
       
        try {
            const options = this.getGenerationOptions();
            const result = await DreamEngine.client.validateIdea(input, options);
           
            this.hideLoading();
            this.showValidationResults(result);
            this.showNotification('Idea validated successfully!', 'success');
        } catch (error) {
            this.hideLoading();
            this.showNotification('Validation failed: ' + error.message, 'error');
        }
    }
   
    async handleGenerate() {
        const input = this.getInputText();
        if (!this.validateInput(input)) return;
       
        this.startGeneration();
       
        try {
            const options = this.getGenerationOptions();
            const result = await DreamEngine.client.generateCode(input, options);
           
            this.stopGeneration();
            this.showGenerationResults(result);
            this.showNotification('Code generated successfully!', 'success');
        } catch (error) {
            this.stopGeneration();
            this.showNotification('Generation failed: ' + error.message, 'error');
        }
    }
   
    async handleStreaming() {
        this.showNotification('Streaming feature coming soon!', 'info');
    }
   
    handleNewProject() {
        const dreamInput = document.getElementById('dream-input');
        if (dreamInput) {
            dreamInput.value = '';
            this.updateCharacterCount();
            this.autoResizeTextarea(dreamInput);
        }
       
        // Reset all options
        this.resetOptions();
       
        // Hide results
        const resultsSection = document.getElementById('dream-result-container');
        if (resultsSection) {
            resultsSection.classList.remove('active');
        }
       
        this.showNotification('New project started', 'success');
    }
   
    getInputText() {
        const dreamInput = document.getElementById('dream-input');
        return dreamInput ? dreamInput.value.trim() : '';
    }
   
    validateInput(input) {
        if (!input) {
            this.showNotification('Please enter your project description', 'error');
            const dreamInput = document.getElementById('dream-input');
            if (dreamInput) dreamInput.focus();
            return false;
        }
       
        if (input.length < 50) {
            this.showNotification('Please provide more details (minimum 50 characters)', 'error');
            const dreamInput = document.getElementById('dream-input');
            if (dreamInput) dreamInput.focus();
            return false;
        }
       
        return true;
    }
   
    getGenerationOptions() {
        return {
            model_provider: 'auto',
            project_type: this.getSelectValue('dream-project-type-select'),
            programming_language: this.getSelectValue('dream-language-select'),
            database_type: this.getSelectValue('dream-database-select'),
            security_level: this.getSelectValue('dream-security-select') || 'standard',
            include_tests: this.getCheckboxValue('dream-include-tests-checkbox'),
            include_documentation: this.getCheckboxValue('dream-include-docs-checkbox'),
            include_docker: this.getCheckboxValue('dream-include-docker-checkbox'),
            include_ci_cd: this.getCheckboxValue('dream-include-cicd-checkbox'),
            temperature: 0.7
        };
    }
   
    getSelectValue(id) {
        const element = document.getElementById(id);
        return element ? element.value : null;
    }
   
    getCheckboxValue(id) {
        const element = document.getElementById(id);
        return element ? element.checked : false;
    }
   
    resetOptions() {
        // Reset selects to first option
        const selects = ['dream-project-type-select', 'dream-language-select', 'dream-database-select'];
        selects.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.selectedIndex = 0;
        });
       
        // Reset security to standard
        const securitySelect = document.getElementById('dream-security-select');
        if (securitySelect) securitySelect.value = 'standard';
       
        // Reset checkboxes to defaults
        this.setCheckboxValue('dream-include-tests-checkbox', true);
        this.setCheckboxValue('dream-include-docs-checkbox', true);
        this.setCheckboxValue('dream-include-docker-checkbox', false);
        this.setCheckboxValue('dream-include-cicd-checkbox', false);
    }
   
    setCheckboxValue(id, value) {
        const element = document.getElementById(id);
        if (element) element.checked = value;
    }
   
    bindOptions() {
        const optionsToggle = document.getElementById('options-toggle');
        if (optionsToggle) {
            optionsToggle.addEventListener('click', () => this.toggleOptions());
        }
    }
   
    toggleOptions() {
        const optionsPanel = document.getElementById('options-panel');
        const optionsToggle = document.getElementById('options-toggle');
       
        if (!optionsPanel || !optionsToggle) return;
       
        this.optionsExpanded = !this.optionsExpanded;
       
        if (this.optionsExpanded) {
            optionsPanel.classList.add('active');
            optionsPanel.style.display = 'block';
            optionsToggle.setAttribute('aria-expanded', 'true');
        } else {
            optionsPanel.classList.remove('active');
            optionsPanel.style.display = 'none';
            optionsToggle.setAttribute('aria-expanded', 'false');
        }
       
        this.showNotification('Options ' + (this.optionsExpanded ? 'expanded' : 'collapsed'), 'info');
    }
   
    bindVoiceInput() {
        const voiceBtn = document.getElementById('voice-input-button');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.handleVoiceInput());
        }
    }
   
    async handleVoiceInput() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.showNotification('Voice input not supported in this browser', 'error');
            return;
        }
       
        if (this.isRecording) {
            this.stopRecording();
            return;
        }
       
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.startRecording(stream);
        } catch (error) {
            this.showNotification('Microphone access denied', 'error');
        }
    }
   
    startRecording(stream) {
        this.mediaRecorder = new MediaRecorder(stream);
        const chunks = [];
       
        this.mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
        this.mediaRecorder.onstop = () => this.processRecording(chunks);
       
        this.mediaRecorder.start();
        this.isRecording = true;
       
        // Update UI
        const voiceBtn = document.getElementById('voice-input-button');
        if (voiceBtn) {
            voiceBtn.style.backgroundColor = '#ff3b30';
            voiceBtn.title = 'Stop Recording';
        }
       
        this.showNotification('Recording... Click again to stop', 'info');
       
        // Auto-stop after 30 seconds
        setTimeout(() => {
            if (this.isRecording) {
                this.stopRecording();
            }
        }, 30000);
    }
   
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
           
            // Reset UI
            const voiceBtn = document.getElementById('voice-input-button');
            if (voiceBtn) {
                voiceBtn.style.backgroundColor = '';
                voiceBtn.title = 'Voice Input';
            }
        }
    }
   
    async processRecording(chunks) {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
       
        this.showLoading('Processing voice input...');
       
        try {
            const result = await DreamEngine.client.processVoice(audioBlob);
            this.hideLoading();
           
            if (result.transcribed_text) {
                const dreamInput = document.getElementById('dream-input');
                if (dreamInput) {
                    dreamInput.value = result.transcribed_text;
                    this.updateCharacterCount();
                    this.autoResizeTextarea(dreamInput);
                }
                this.showNotification('Voice input processed successfully!', 'success');
            }
        } catch (error) {
            this.hideLoading();
            this.showNotification('Voice processing failed: ' + error.message, 'error');
        }
    }
   
    bindTemplates() {
        const templateBtn = document.getElementById('template-button');
        if (templateBtn) {
            templateBtn.addEventListener('click', () => this.showTemplates());
        }
    }
   
    showTemplates() {
        const templates = [
            {
                name: 'Task Management API',
                content: `Create a FastAPI backend for a task management application with:

1. User authentication with JWT tokens
2. CRUD operations for tasks (title, description, due date, priority, status)
3. Task categories and tags
4. User-specific task filtering
5. PostgreSQL database with proper relationships
6. Input validation and error handling
7. API documentation with OpenAPI/Swagger
8. Comprehensive unit tests and logging`
            },
            {
                name: 'E-commerce API',
                content: `Build a comprehensive e-commerce API with:

1. Product catalog management (products, variants, categories)
2. Inventory tracking and search functionality
3. User management (customers, profiles, admin roles)
4. Shopping cart and checkout system
5. Order processing and tracking
6. Payment integration (Stripe)
7. PostgreSQL database with optimized queries
8. Redis caching for performance`
            },
            {
                name: 'Blog Platform API',
                content: `Create a modern blog platform API featuring:

1. Content management (create, edit, delete posts)
2. Rich text content with markdown support
3. Image upload and SEO-friendly URLs
4. User system with role-based permissions
5. Social features (comments, likes, follows)
6. Full-text search and analytics
7. Email subscriptions and RSS feeds
8. FastAPI with PostgreSQL and caching`
            }
        ];
       
        this.createTemplateModal(templates);
    }
   
    createTemplateModal(templates) {
        // Remove existing modal
        const existingModal = document.querySelector('.template-modal');
        if (existingModal) {
            existingModal.remove();
        }
       
        const modal = document.createElement('div');
        modal.className = 'template-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;
       
        const content = document.createElement('div');
        content.className = 'template-modal-content';
        content.style.cssText = `
            background: white;
            border-radius: 16px;
            padding: 32px;
            max-width: 600px;
            max-height: 80vh;
            overflow: auto;
            margin: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        `;
       
        content.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                <h2 style="margin: 0; color: #1d1d1f;">Choose a Template</h2>
                <button class="close-btn" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #8e8e93;">×</button>
            </div>
            <div class="template-list">
                ${templates.map((template, index) => `
                    <div class="template-item" data-index="${index}" style="
                        padding: 20px;
                        border: 1px solid #e5e5ea;
                        border-radius: 12px;
                        margin-bottom: 16px;
                        cursor: pointer;
                        transition: all 0.2s ease;
                    ">
                        <h3 style="margin: 0 0 8px 0; color: #1d1d1f;">${template.name}</h3>
                        <p style="margin: 0; color: #8e8e93; font-size: 14px;">${template.content.substring(0, 100)}...</p>
                    </div>
                `).join('')}
            </div>
        `;
       
        modal.appendChild(content);
        document.body.appendChild(modal);
       
        // Event handlers
        content.querySelector('.close-btn').addEventListener('click', () => {
            modal.remove();
        });
       
        content.querySelectorAll('.template-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                this.useTemplate(templates[index]);
                modal.remove();
            });
           
            item.addEventListener('mouseenter', () => {
                item.style.borderColor = '#007aff';
                item.style.transform = 'translateY(-2px)';
            });
           
            item.addEventListener('mouseleave', () => {
                item.style.borderColor = '#e5e5ea';
                item.style.transform = 'translateY(0)';
            });
        });
       
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
   
    useTemplate(template) {
        const dreamInput = document.getElementById('dream-input');
        if (dreamInput) {
            dreamInput.value = template.content;
            this.updateCharacterCount();
            this.autoResizeTextarea(dreamInput);
            dreamInput.focus();
        }
       
        this.showNotification(`Template "${template.name}" loaded`, 'success');
    }
   
    bindFileOperations() {
        const copyBtn = document.getElementById('dream-copy-code-button');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyCode());
        }
       
        const downloadBtn = document.getElementById('dream-download-code-button');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadCode());
        }
    }
   
    async copyCode() {
        const codeDisplay = document.getElementById('dream-code-display');
        if (!codeDisplay) return;
       
        try {
            await navigator.clipboard.writeText(codeDisplay.textContent);
            this.showNotification('Code copied to clipboard!', 'success');
        } catch (error) {
            this.showNotification('Failed to copy code', 'error');
        }
    }
   
    downloadCode() {
        const codeDisplay = document.getElementById('dream-code-display');
        if (!codeDisplay) return;
       
        const content = codeDisplay.textContent;
        const filename = 'generated_code.py';
       
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
       
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
       
        this.showNotification(`Downloaded ${filename}`, 'success');
    }
   
    bindInfoTabs() {
        const tabs = document.querySelectorAll('.info-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTab = tab.dataset.tab;
               
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
               
                // Update active panel
                const panels = document.querySelectorAll('.info-panel');
                panels.forEach(p => p.classList.remove('active'));
               
                const targetPanel = document.getElementById(`${targetTab}-panel`);
                if (targetPanel) {
                    targetPanel.classList.add('active');
                }
            });
        });
    }
   
    bindDraftManagement() {
        const saveBtn = document.getElementById('dream-save-draft-button');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveDraft());
        }
       
        const loadBtn = document.getElementById('dream-load-draft-button');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadDraft());
        }
    }
   
    saveDraft() {
        const input = this.getInputText();
        if (!input) {
            this.showNotification('Nothing to save', 'error');
            return;
        }
       
        const title = prompt('Enter a title for this draft:') || `Draft ${new Date().toLocaleDateString()}`;
        const draft = {
            id: Date.now().toString(),
            title,
            content: input,
            options: this.getGenerationOptions(),
            timestamp: new Date().toISOString()
        };
       
        const drafts = JSON.parse(localStorage.getItem('dreamengine_drafts') || '[]');
        drafts.push(draft);
       
        // Limit to 10 drafts
        if (drafts.length > 10) {
            drafts.shift();
        }
       
        localStorage.setItem('dreamengine_drafts', JSON.stringify(drafts));
        this.showNotification(`Draft "${title}" saved`, 'success');
    }
   
    loadDraft() {
        const drafts = JSON.parse(localStorage.getItem('dreamengine_drafts') || '[]');
       
        if (drafts.length === 0) {
            this.showNotification('No drafts found', 'error');
            return;
        }
       
        // Simple implementation - load the most recent draft
        const latestDraft = drafts[drafts.length - 1];
       
        const dreamInput = document.getElementById('dream-input');
        if (dreamInput) {
            dreamInput.value = latestDraft.content;
            this.updateCharacterCount();
            this.autoResizeTextarea(dreamInput);
        }
       
        this.showNotification(`Draft "${latestDraft.title}" loaded`, 'success');
    }
   
    startGeneration() {
        DreamEngine.isGenerating = true;
        this.showProgress();
        this.updateProgress(0);
       
        // Disable buttons
        const buttons = ['dream-validate-button', 'dream-generate-button', 'dream-streaming-button'];
        buttons.forEach(id => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.disabled = true;
                btn.style.opacity = '0.6';
            }
        });
    }
   
    stopGeneration() {
        DreamEngine.isGenerating = false;
        this.hideProgress();
       
        // Re-enable buttons
        const buttons = ['dream-validate-button', 'dream-generate-button', 'dream-streaming-button'];
        buttons.forEach(id => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.disabled = false;
                btn.style.opacity = '1';
            }
        });
    }
   
    showProgress() {
        const progressSection = document.getElementById('progress-section');
        if (progressSection) {
            progressSection.classList.add('active');
        }
    }
   
    hideProgress() {
        const progressSection = document.getElementById('progress-section');
        if (progressSection) {
            progressSection.classList.remove('active');
        }
    }
   
    updateProgress(percentage) {
        const progressBar = document.getElementById('dream-progress-bar');
        if (progressBar) {
            progressBar.style.width = `${Math.min(percentage, 100)}%`;
        }
    }
   
    showValidationResults(data) {
        console.log('Validation results:', data);
        // For now, just show a simple message
        if (data.overall_score) {
            this.showNotification(`Idea validation score: ${data.overall_score}/10`, 'success');
        }
    }
   
    showGenerationResults(data) {
        console.log('Generation results:', data);
       
        // Show results section
        const resultsSection = document.getElementById('dream-result-container');
        if (resultsSection) {
            resultsSection.classList.add('active');
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
       
        // Update generation time
        const timeElement = document.getElementById('dream-generation-time');
        if (timeElement && data.generation_time_seconds) {
            timeElement.textContent = data.generation_time_seconds.toFixed(2);
        }
       
        // Show code
        if (data.files && data.files.length > 0) {
            this.displayCode(data.files[0]);
            this.populateFileSelector(data.files);
        }
       
        // Show explanation
        if (data.explanation) {
            const explanationPanel = document.getElementById('dream-explanation');
            if (explanationPanel) {
                explanationPanel.innerHTML = this.formatText(data.explanation);
            }
        }
       
        // Show architecture
        if (data.architecture) {
            const architecturePanel = document.getElementById('dream-architecture');
            if (architecturePanel) {
                architecturePanel.innerHTML = this.formatText(data.architecture);
            }
        }
    }
   
    displayCode(file) {
        const codeDisplay = document.getElementById('dream-code-display');
        const languageElement = document.getElementById('code-language');
       
        if (codeDisplay) {
            codeDisplay.textContent = file.content || 'No code generated';
        }
       
        if (languageElement) {
            languageElement.textContent = file.language || 'Text';
        }
    }
   
    populateFileSelector(files) {
        const fileSelector = document.getElementById('dream-file-selector');
        if (!fileSelector) return;
       
        fileSelector.innerHTML = '<option value="">Select a file...</option>';
       
        files.forEach((file, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = file.filename || `File ${index + 1}`;
            fileSelector.appendChild(option);
        });
       
        fileSelector.addEventListener('change', (e) => {
            const index = parseInt(e.target.value);
            if (!isNaN(index) && files[index]) {
                this.displayCode(files[index]);
            }
        });
    }
   
    formatText(text) {
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }
   
    showLoading(text = 'Processing...') {
        const overlay = document.getElementById('loading-overlay');
        const loadingText = overlay?.querySelector('.loading-text');
       
        if (loadingText) loadingText.textContent = text;
        if (overlay) overlay.classList.add('active');
    }
   
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.remove('active');
    }
   
    showNotification(message, type = 'info') {
        const toast = document.getElementById('dream-error');
        if (!toast) return;
       
        toast.textContent = message;
        toast.className = `error-toast ${type} show`;
       
        // Auto-hide after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
   
    updateStatusIndicator(status, text) {
        const indicator = document.getElementById('status-indicator');
        const statusText = indicator?.querySelector('.status-text');
        const statusDot = indicator?.querySelector('.status-dot');
       
        if (statusText) statusText.textContent = text;
        if (statusDot) {
            statusDot.style.backgroundColor = status === 'online' ? '#34c759' : '#ff3b30';
        }
    }
}

// Initialize DreamEngine when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌟 Starting DreamEngine initialization...');
    DreamEngine.init();
   
    // Initial character count update
    const dreamInput = document.getElementById('dream-input');
    if (dreamInput && DreamEngine.ui) {
        DreamEngine.ui.updateCharacterCount();
    }
   
    // Check system health
    setTimeout(() => {
        DreamEngine.checkSystemHealth();
    }, 1000);
   
    console.log('✅ DreamEngine fully initialized and ready!');
});

// Make sure DreamEngine is available globally
window.DreamEngine = DreamEngine;

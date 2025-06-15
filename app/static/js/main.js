/**
 * DreamEngine - Main UI Controller (Fixed Version)
 * No ES6 modules, fully compatible with standard HTML
 */

(function() {
    'use strict';

    class DreamEngineUI {
        constructor() {
            this.activeSection = 'build';
            this.optionsExpanded = false;
            this.charCount = 0;
            this.isGenerating = false;
            this.client = null;
           
            this.init();
        }
       
        init() {
            // Wait for client to be available
            this.waitForClient(() => {
                this.client = window.dreamEngineClient;
                this.setupEventListeners();
                this.setupCharacterCounter();
                this.setupKeyboardShortcuts();
                this.checkSystemStatus();
               
                console.log('🚀 DreamEngine UI initialized successfully');
            });
        }
       
        waitForClient(callback) {
            if (window.dreamEngineClient) {
                callback();
            } else {
                setTimeout(() => this.waitForClient(callback), 100);
            }
        }
       
        setupEventListeners() {
            // Navigation
            this.setupNavigation();
           
            // Input interactions
            this.setupInputInteractions();
           
            // Options panel
            this.setupOptionsPanel();
           
            // Action buttons
            this.setupActionButtons();
           
            // File operations
            this.setupFileOperations();
           
            // Info tabs
            this.setupInfoTabs();
           
            // Voice input
            this.setupVoiceInput();
           
            // Template functionality
            this.setupTemplates();
        }
       
        setupNavigation() {
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
            const targetPill = document.querySelector(`[data-section="${sectionName}"]`);
            if (targetPill) {
                targetPill.classList.add('active');
            }
           
            // Update active section
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            const targetSection = document.getElementById(`${sectionName}-section`);
            if (targetSection) {
                targetSection.classList.add('active');
            }
           
            this.activeSection = sectionName;
           
            // Smooth scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
           
            console.log(`🔄 Switched to section: ${sectionName}`);
        }
       
        setupInputInteractions() {
            const dreamInput = document.getElementById('dream-input');
            const inputArea = document.querySelector('.input-area');
           
            if (dreamInput && inputArea) {
                // Focus effects
                dreamInput.addEventListener('focus', () => {
                    inputArea.style.transform = 'scale(1.01)';
                    inputArea.style.transition = 'all 0.3s ease';
                });
               
                dreamInput.addEventListener('blur', () => {
                    inputArea.style.transform = 'scale(1)';
                });
               
                // Auto-resize textarea
                dreamInput.addEventListener('input', () => {
                    this.autoResizeTextarea(dreamInput);
                    this.updateCharacterCount();
                });
               
                console.log('✅ Input interactions setup complete');
            }
        }
       
        autoResizeTextarea(textarea) {
            textarea.style.height = 'auto';
            const newHeight = Math.min(textarea.scrollHeight, 300); // Max height
            textarea.style.height = newHeight + 'px';
           
            // Smooth height transition
            textarea.style.transition = 'height 0.2s ease-out';
        }
       
        setupCharacterCounter() {
            const dreamInput = document.getElementById('dream-input');
            const charCountElement = document.getElementById('char-count');
           
            if (dreamInput && charCountElement) {
                dreamInput.addEventListener('input', () => {
                    this.updateCharacterCount();
                });
                console.log('✅ Character counter setup complete');
            }
        }
       
        updateCharacterCount() {
            const dreamInput = document.getElementById('dream-input');
            const charCountElement = document.getElementById('char-count');
           
            if (dreamInput && charCountElement) {
                this.charCount = dreamInput.value.length;
                charCountElement.textContent = this.charCount;
               
                // Add color coding
                const inputMeta = document.querySelector('.input-meta');
                if (inputMeta) {
                    if (this.charCount < 50) {
                        inputMeta.style.color = '#ff9500'; // warning
                    } else if (this.charCount > 5000) {
                        inputMeta.style.color = '#ff3b30'; // danger
                    } else {
                        inputMeta.style.color = ''; // reset
                    }
                }
            }
        }
       
        setupOptionsPanel() {
            const optionsToggle = document.getElementById('options-toggle');
            const optionsPanel = document.getElementById('options-panel');
           
            if (optionsToggle && optionsPanel) {
                optionsToggle.addEventListener('click', () => {
                    this.toggleOptionsPanel();
                });
                console.log('✅ Options panel setup complete');
            }
        }
       
        toggleOptionsPanel() {
            const optionsToggle = document.getElementById('options-toggle');
            const optionsPanel = document.getElementById('options-panel');
            const chevron = document.querySelector('.options-chevron');
           
            this.optionsExpanded = !this.optionsExpanded;
           
            if (this.optionsExpanded) {
                optionsPanel.style.display = 'block';
                optionsPanel.classList.add('active');
                optionsToggle.setAttribute('aria-expanded', 'true');
               
                // Smooth expand animation
                optionsPanel.style.maxHeight = '0px';
                optionsPanel.style.opacity = '0';
               
                requestAnimationFrame(() => {
                    optionsPanel.style.transition = 'all 0.3s ease';
                    optionsPanel.style.maxHeight = '500px';
                    optionsPanel.style.opacity = '1';
                });
            } else {
                optionsPanel.style.transition = 'all 0.3s ease';
                optionsPanel.style.maxHeight = '0px';
                optionsPanel.style.opacity = '0';
                optionsToggle.setAttribute('aria-expanded', 'false');
               
                setTimeout(() => {
                    optionsPanel.style.display = 'none';
                    optionsPanel.classList.remove('active');
                }, 300);
            }
           
            // Animate chevron
            if (chevron) {
                chevron.style.transform = this.optionsExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
            }
        }
       
        setupActionButtons() {
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
           
            // Draft buttons
            const saveDraftBtn = document.getElementById('dream-save-draft-button');
            if (saveDraftBtn) {
                saveDraftBtn.addEventListener('click', () => this.handleSaveDraft());
            }
           
            const loadDraftBtn = document.getElementById('dream-load-draft-button');
            if (loadDraftBtn) {
                loadDraftBtn.addEventListener('click', () => this.handleLoadDraft());
            }
           
            console.log('✅ Action buttons setup complete');
        }
       
        async handleValidate() {
            const input = this.getInputText();
            if (!this.validateInput(input)) return;
           
            this.showLoading('Validating your idea...');
           
            try {
                console.log('🔍 Starting validation...');
                const response = await this.client.validateIdea(input, this.getGenerationOptions());
               
                this.hideLoading();
                this.showValidationResults(response);
                this.showNotification('Idea validated successfully!', 'success');
            } catch (error) {
                console.error('❌ Validation failed:', error);
                this.hideLoading();
                this.showNotification('Validation failed: ' + error.message, 'error');
            }
        }
       
        async handleGenerate() {
            const input = this.getInputText();
            if (!this.validateInput(input)) return;
           
            this.startGeneration();
           
            try {
                console.log('🚀 Starting generation...');
                const response = await this.client.processDream(input, this.getGenerationOptions());
               
                this.stopGeneration();
                this.showGenerationResults(response);
                this.showNotification('Code generated successfully!', 'success');
            } catch (error) {
                console.error('❌ Generation failed:', error);
                this.stopGeneration();
                this.showNotification('Generation failed: ' + error.message, 'error');
            }
        }
       
        async handleStreaming() {
            const input = this.getInputText();
            if (!this.validateInput(input)) return;
           
            this.startGeneration();
           
            try {
                console.log('🌊 Starting streaming generation...');
               
                await this.client.streamDreamGeneration(
                    input,
                    (progress) => {
                        console.log('📈 Progress:', progress);
                        this.updateProgress(progress.progress || 0);
                        this.updateProgressStatus(`Processing... ${Math.round(progress.progress || 0)}%`);
                        this.appendStreamContent(progress.content || '');
                    },
                    (result) => {
                        console.log('✅ Streaming completed:', result);
                        this.stopGeneration();
                        this.showGenerationResults(result);
                        this.showNotification('Streaming completed!', 'success');
                    },
                    (error) => {
                        console.error('❌ Streaming failed:', error);
                        this.stopGeneration();
                        this.showNotification('Streaming failed: ' + error.message, 'error');
                    },
                    this.getGenerationOptions()
                );
            } catch (error) {
                console.error('❌ Streaming setup failed:', error);
                this.stopGeneration();
                this.showNotification('Streaming failed: ' + error.message, 'error');
            }
        }
       
        getInputText() {
            const dreamInput = document.getElementById('dream-input');
            return dreamInput ? dreamInput.value.trim() : '';
        }
       
        validateInput(input) {
            if (!input) {
                this.showNotification('Please enter your project description', 'error');
                document.getElementById('dream-input')?.focus();
                return false;
            }
           
            if (input.length < 50) {
                this.showNotification('Please provide more details (minimum 50 characters)', 'error');
                document.getElementById('dream-input')?.focus();
                return false;
            }
           
            return true;
        }
       
        getGenerationOptions() {
            return {
                model_provider: 'auto',
                project_type: document.getElementById('dream-project-type-select')?.value || null,
                programming_language: document.getElementById('dream-language-select')?.value || null,
                database_type: document.getElementById('dream-database-select')?.value || null,
                security_level: document.getElementById('dream-security-select')?.value || 'standard',
                include_tests: document.getElementById('dream-include-tests-checkbox')?.checked || true,
                include_documentation: document.getElementById('dream-include-docs-checkbox')?.checked || true,
                include_docker: document.getElementById('dream-include-docker-checkbox')?.checked || false,
                include_ci_cd: document.getElementById('dream-include-cicd-checkbox')?.checked || false,
                streaming: false,
                temperature: 0.7
            };
        }
       
        startGeneration() {
            this.isGenerating = true;
            this.showProgress();
            this.updateProgress(0);
            this.updateProgressStatus('Initializing generation...');
           
            // Disable action buttons
            const buttons = document.querySelectorAll('#dream-validate-button, #dream-generate-button, #dream-streaming-button');
            buttons.forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.6';
            });
           
            console.log('🚀 Generation started');
        }
       
        stopGeneration() {
            this.isGenerating = false;
            this.hideProgress();
           
            // Re-enable action buttons
            const buttons = document.querySelectorAll('#dream-validate-button, #dream-generate-button, #dream-streaming-button');
            buttons.forEach(btn => {
                btn.disabled = false;
                btn.style.opacity = '1';
            });
           
            console.log('🛑 Generation stopped');
        }
       
        showProgress() {
            const progressSection = document.getElementById('progress-section');
            if (progressSection) {
                progressSection.classList.add('active');
                progressSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }
       
        hideProgress() {
            const progressSection = document.getElementById('progress-section');
            if (progressSection) {
                progressSection.classList.remove('active');
            }
        }
       
        updateProgress(percentage) {
            const progressFill = document.getElementById('dream-progress-bar');
            if (progressFill) {
                progressFill.style.width = `${Math.min(percentage, 100)}%`;
            }
        }
       
        updateProgressStatus(status) {
            const progressStatus = document.getElementById('dream-progress-status');
            if (progressStatus) {
                progressStatus.textContent = status;
            }
        }
       
        appendStreamContent(content) {
            if (!content) return;
           
            const codeDisplay = document.getElementById('dream-code-display');
            if (codeDisplay) {
                codeDisplay.textContent += content;
                this.showResults();
            }
        }
       
        showResults() {
            const resultsSection = document.getElementById('dream-result-container');
            if (resultsSection) {
                resultsSection.classList.add('active');
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
       
        showValidationResults(data) {
            console.log('📊 Validation results:', data);
            this.showNotification('Validation completed successfully!', 'success');
           
            // You can expand this to show detailed validation results
            if (data.overall_score !== undefined) {
                this.showNotification(`Validation score: ${data.overall_score}/10`, 'info');
            }
        }
       
        showGenerationResults(data) {
            this.showResults();
           
            // Update generation time
            const timeElement = document.getElementById('dream-generation-time');
            if (timeElement && data.generation_time_seconds) {
                timeElement.textContent = data.generation_time_seconds.toFixed(2);
            }
           
            // Populate file selector
            this.populateFileSelector(data.files || []);
           
            // Show first file
            if (data.files && data.files.length > 0) {
                this.displayFile(data.files[0]);
            }
           
            // Update explanation and architecture
            this.updateInfoPanels(data);
           
            console.log('📁 Results displayed successfully');
        }
       
        populateFileSelector(files) {
            const fileSelector = document.getElementById('dream-file-selector');
            if (fileSelector) {
                fileSelector.innerHTML = '<option value="">Select a file...</option>';
               
                files.forEach((file, index) => {
                    const option = document.createElement('option');
                    option.value = index;
                    option.textContent = file.filename;
                    fileSelector.appendChild(option);
                });
               
                fileSelector.addEventListener('change', (e) => {
                    const fileIndex = parseInt(e.target.value);
                    if (!isNaN(fileIndex) && files[fileIndex]) {
                        this.displayFile(files[fileIndex]);
                    }
                });
            }
        }
       
        displayFile(file) {
            const codeDisplay = document.getElementById('dream-code-display');
            const languageElement = document.getElementById('code-language');
           
            if (codeDisplay) {
                codeDisplay.textContent = file.content;
            }
           
            if (languageElement) {
                languageElement.textContent = file.language || 'Text';
            }
        }
       
        updateInfoPanels(data) {
            const explanationPanel = document.getElementById('dream-explanation');
            const architecturePanel = document.getElementById('dream-architecture');
            const deploymentPanel = document.getElementById('dream-deployment-steps');
           
            if (explanationPanel && data.explanation) {
                explanationPanel.innerHTML = this.markdownToHtml(data.explanation);
            }
           
            if (architecturePanel && data.architecture) {
                architecturePanel.innerHTML = this.markdownToHtml(data.architecture);
            }
           
            if (deploymentPanel && data.deployment_steps) {
                this.renderDeploymentSteps(data.deployment_steps);
            }
        }
       
        markdownToHtml(markdown) {
            // Simple markdown conversion
            return markdown
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/`(.*?)`/g, '<code>$1</code>');
        }
       
        renderDeploymentSteps(steps) {
            const container = document.getElementById('dream-deployment-steps');
            if (!container) return;
           
            container.innerHTML = '';
           
            steps.forEach(step => {
                const stepElement = document.createElement('div');
                stepElement.className = 'deployment-step';
                stepElement.innerHTML = `
                    <h4>Step ${step.step_number}: ${step.description}</h4>
                    ${step.command ? `<code class="deployment-command">${step.command}</code>` : ''}
                    ${step.verification ? `<p class="deployment-verification">${step.verification}</p>` : ''}
                `;
                container.appendChild(stepElement);
            });
        }
       
        setupFileOperations() {
            // Copy code button
            const copyBtn = document.getElementById('dream-copy-code-button');
            if (copyBtn) {
                copyBtn.addEventListener('click', () => this.copyCode());
            }
           
            // Download code button
            const downloadBtn = document.getElementById('dream-download-code-button');
            if (downloadBtn) {
                downloadBtn.addEventListener('click', () => this.downloadCode());
            }
           
            console.log('✅ File operations setup complete');
        }
       
        async copyCode() {
            const codeDisplay = document.getElementById('dream-code-display');
            if (!codeDisplay) return;
           
            try {
                await navigator.clipboard.writeText(codeDisplay.textContent);
                this.showNotification('Code copied to clipboard!', 'success');
               
                // Visual feedback
                const copyBtn = document.getElementById('dream-copy-code-button');
                if (copyBtn) {
                    const originalContent = copyBtn.innerHTML;
                    copyBtn.innerHTML = '✓';
                    copyBtn.style.color = '#34c759';
                   
                    setTimeout(() => {
                        copyBtn.innerHTML = originalContent;
                        copyBtn.style.color = '';
                    }, 2000);
                }
            } catch (error) {
                console.error('Failed to copy code:', error);
                this.showNotification('Failed to copy code', 'error');
            }
        }
       
        downloadCode() {
            const codeDisplay = document.getElementById('dream-code-display');
            const fileSelector = document.getElementById('dream-file-selector');
           
            if (!codeDisplay) return;
           
            const content = codeDisplay.textContent;
            const filename = fileSelector?.selectedOptions[0]?.textContent || 'generated-code.txt';
           
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
       
        setupInfoTabs() {
            const tabs = document.querySelectorAll('.info-tab');
            const panels = document.querySelectorAll('.info-panel');
           
            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    const targetTab = tab.dataset.tab;
                   
                    // Update active tab
                    tabs.forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                   
                    // Update active panel
                    panels.forEach(p => p.classList.remove('active'));
                    const targetPanel = document.getElementById(`${targetTab}-panel`);
                    if (targetPanel) {
                        targetPanel.classList.add('active');
                    }
                });
            });
           
            console.log('✅ Info tabs setup complete');
        }
       
        setupVoiceInput() {
            const voiceBtn = document.getElementById('voice-input-button');
            if (voiceBtn) {
                voiceBtn.addEventListener('click', () => this.handleVoiceInput());
            }
           
            console.log('✅ Voice input setup complete');
        }
       
        handleVoiceInput() {
            this.showNotification('Voice input feature coming soon!', 'info');
        }
       
        setupTemplates() {
            const templateBtn = document.getElementById('template-button');
            if (templateBtn) {
                templateBtn.addEventListener('click', () => this.showTemplateModal());
            }
           
            console.log('✅ Templates setup complete');
        }
       
        showTemplateModal() {
            const templates = [
                {
                    name: 'Task Management API',
                    description: 'FastAPI backend with user auth and CRUD operations',
                    content: `Create a FastAPI backend for a task management application with the following features:

1. User authentication with JWT tokens
2. CRUD operations for tasks with the following fields:
   - Title (required)
   - Description
   - Due date
   - Priority (low, medium, high)
   - Status (todo, in_progress, completed)
3. Task categories and tags
4. User-specific task filtering
5. PostgreSQL database with proper relationships
6. Input validation and error handling
7. API documentation with OpenAPI/Swagger

Include comprehensive unit tests and proper logging.`
                },
                {
                    name: 'E-commerce API',
                    description: 'Complete e-commerce backend with payments',
                    content: `Build a comprehensive e-commerce API with:

1. Product catalog management
2. User management with authentication
3. Shopping cart and checkout
4. Order processing
5. Payment integration (Stripe)
6. PostgreSQL database with optimized queries
7. Redis caching for performance`
                },
                {
                    name: 'Blog Platform API',
                    description: 'Content management system with social features',
                    content: `Create a modern blog platform API featuring:

1. Content Management
2. User System with role-based permissions
3. Social Features (comments, likes, follows)
4. Advanced Features (search, analytics, RSS)

Use FastAPI with PostgreSQL and implement proper caching strategies.`
                }
            ];
           
            const modal = this.createTemplateModal(templates);
            document.body.appendChild(modal);
        }
       
        createTemplateModal(templates) {
            const modal = document.createElement('div');
            modal.className = 'template-modal';
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            `;
           
            const modalContent = document.createElement('div');
            modalContent.className = 'template-modal-content';
            modalContent.style.cssText = `
                background-color: white;
                border-radius: 16px;
                padding: 32px;
                max-width: 600px;
                max-height: 80vh;
                overflow: auto;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            `;
           
            modalContent.innerHTML = `
                <div class="template-modal-header">
                    <h2>Choose a Template</h2>
                    <button class="template-close-btn" style="float: right; background: none; border: none; font-size: 24px; cursor: pointer;">×</button>
                </div>
                <div class="template-modal-body">
                    ${templates.map((template, index) => `
                        <div class="template-card" data-template="${index}" style="
                            padding: 20px;
                            border: 1px solid #ddd;
                            border-radius: 8px;
                            margin-bottom: 16px;
                            cursor: pointer;
                            transition: all 0.2s ease;
                        ">
                            <h3>${template.name}</h3>
                            <p style="color: #666; margin: 8px 0;">${template.description}</p>
                            <button class="btn-primary template-select-btn" style="
                                background: #007aff;
                                color: white;
                                border: none;
                                padding: 8px 16px;
                                border-radius: 6px;
                                cursor: pointer;
                            ">Use Template</button>
                        </div>
                    `).join('')}
                </div>
            `;
           
            modal.appendChild(modalContent);
           
            // Event handlers
            modal.querySelector('.template-close-btn').addEventListener('click', () => {
                document.body.removeChild(modal);
            });
           
            modal.querySelectorAll('.template-select-btn').forEach((btn, index) => {
                btn.addEventListener('click', () => {
                    this.useTemplate(templates[index]);
                    document.body.removeChild(modal);
                });
            });
           
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    document.body.removeChild(modal);
                }
            });
           
            return modal;
        }
       
        useTemplate(template) {
            const dreamInput = document.getElementById('dream-input');
            if (dreamInput) {
                dreamInput.value = template.content;
                this.updateCharacterCount();
                this.autoResizeTextarea(dreamInput);
                dreamInput.focus();
               
                this.showNotification(`Template "${template.name}" loaded`, 'success');
            }
        }
       
        handleSaveDraft() {
            const input = this.getInputText();
            if (!input) {
                this.showNotification('Nothing to save', 'error');
                return;
            }
           
            const title = prompt('Enter a title for this draft:') || `Draft ${new Date().toLocaleDateString()}`;
           
            try {
                this.client.saveDraft(title, input, this.getGenerationOptions());
                this.showNotification(`Draft "${title}" saved`, 'success');
            } catch (error) {
                this.showNotification('Failed to save draft: ' + error.message, 'error');
            }
        }
       
        handleLoadDraft() {
            const drafts = this.client.loadDrafts();
           
            if (drafts.length === 0) {
                this.showNotification('No drafts found', 'error');
                return;
            }
           
            // Simple draft selection (you can enhance this with a modal)
            const draftTitles = drafts.map(d => d.title);
            const selection = prompt('Available drafts:\n' + draftTitles.map((title, i) => `${i + 1}. ${title}`).join('\n') + '\n\nEnter number:');
           
            if (selection) {
                const index = parseInt(selection) - 1;
                if (index >= 0 && index < drafts.length) {
                    const draft = drafts[index];
                    const dreamInput = document.getElementById('dream-input');
                    if (dreamInput) {
                        dreamInput.value = draft.content;
                        this.updateCharacterCount();
                        this.autoResizeTextarea(dreamInput);
                        this.showNotification(`Draft "${draft.title}" loaded`, 'success');
                    }
                }
            }
        }
       
        setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Command/Ctrl + Enter to generate
                if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                    e.preventDefault();
                    if (!this.isGenerating) {
                        this.handleGenerate();
                    }
                }
               
                // Command/Ctrl + S to save draft
                if ((e.metaKey || e.ctrlKey) && e.key === 's') {
                    e.preventDefault();
                    this.handleSaveDraft();
                }
               
                // Escape to close modals
                if (e.key === 'Escape') {
                    const modals = document.querySelectorAll('.template-modal');
                    modals.forEach(modal => {
                        if (modal.parentNode) {
                            modal.parentNode.removeChild(modal);
                        }
                    });
                }
            });
           
            console.log('✅ Keyboard shortcuts setup complete');
        }
       
        async checkSystemStatus() {
            try {
                const response = await this.client.checkHealth();
               
                if (response.status === 'healthy') {
                    this.updateStatusIndicator('online', 'System Online');
                } else {
                    this.updateStatusIndicator('offline', 'System Offline');
                }
            } catch (error) {
                console.error('Health check failed:', error);
                this.updateStatusIndicator('offline', 'Connection Error');
            }
           
            // Check again in 30 seconds
            setTimeout(() => this.checkSystemStatus(), 30000);
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
            console.log(`📢 ${type.toUpperCase()}: ${message}`);
           
            const toast = document.getElementById('dream-error');
            if (!toast) {
                // Create a simple notification if toast doesn't exist
                const notification = document.createElement('div');
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: ${type === 'error' ? '#ff3b30' : type === 'success' ? '#34c759' : '#007aff'};
                    color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    z-index: 10000;
                    animation: slideIn 0.3s ease;
                `;
                notification.textContent = message;
                document.body.appendChild(notification);
               
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 5000);
                return;
            }
           
            toast.textContent = message;
            toast.className = `error-toast ${type}`;
            toast.classList.add('show');
           
            // Auto-hide after 5 seconds
            setTimeout(() => {
                toast.classList.remove('show');
            }, 5000);
        }
    }

    // Initialize the UI when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeUI);
    } else {
        initializeUI();
    }

    function initializeUI() {
        window.dreamEngineUI = new DreamEngineUI();
        console.log('🎯 DreamEngine UI initialized and ready!');
    }

})();



/**
 * DreamEngine Diagnostic Script
 * Add this to your HTML temporarily to diagnose issues
 */

(function() {
    'use strict';
   
    console.log('🔍 DreamEngine Diagnostic Script Starting...');
   
    // 1. Check current file structure
    function checkFileStructure() {
        console.log('\n📁 Checking File Structure:');
       
        // Test if static files are accessible
        const filesToCheck = [
            '/static/js/dream_client.js',
            '/static/js/main.js',
            '/static/css/styles.css'
        ];
       
        filesToCheck.forEach(file => {
            fetch(file)
                .then(response => {
                    if (response.ok) {
                        console.log(`✅ ${file} - Accessible`);
                    } else {
                        console.error(`❌ ${file} - ${response.status} ${response.statusText}`);
                    }
                })
                .catch(error => {
                    console.error(`❌ ${file} - Network Error:`, error.message);
                });
        });
    }
   
    // 2. Check API endpoints
    function checkAPIEndpoints() {
        console.log('\n🌐 Checking API Endpoints:');
       
        const endpoints = [
            '/api/v1/dreamengine/health',
            '/api/v1/dreamengine/process',
            '/api/v1/dreamengine/validate',
            '/api/v1/dreamengine/stream'
        ];
       
        endpoints.forEach(endpoint => {
            fetch(endpoint, {
                method: endpoint.includes('health') ? 'GET' : 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: endpoint.includes('health') ? undefined : JSON.stringify({
                    test: true
                })
            })
                .then(response => {
                    console.log(`📡 ${endpoint} - Status: ${response.status}`);
                    if (response.status === 404) {
                        console.error(`❌ ${endpoint} - Endpoint not found`);
                    } else if (response.status >= 500) {
                        console.error(`❌ ${endpoint} - Server error`);
                    } else {
                        console.log(`✅ ${endpoint} - Responding`);
                    }
                })
                .catch(error => {
                    console.error(`❌ ${endpoint} - Network Error:`, error.message);
                });
        });
    }
   
    // 3. Check environment variables (client-side detection)
    function checkEnvironment() {
        console.log('\n🔧 Environment Check:');
       
        // Check if we can detect the environment from responses
        fetch('/api/v1/dreamengine/health')
            .then(response => response.json())
            .then(data => {
                console.log('📊 Health Response:', data);
               
                if (data.environment) {
                    console.log(`🌍 Environment: ${data.environment}`);
                }
               
                if (data.llm_providers) {
                    console.log('🤖 Available LLM Providers:', data.llm_providers);
                } else {
                    console.warn('⚠️ No LLM providers reported in health check');
                }
            })
            .catch(error => {
                console.error('❌ Could not get health data:', error);
            });
    }
   
    // 4. Test basic functionality
    function testBasicFunctionality() {
        console.log('\n🧪 Testing Basic Functionality:');
       
        // Test DOM elements
        const elementsToCheck = [
            'dream-input',
            'dream-generate-button',
            'dream-validate-button',
            'dream-streaming-button'
        ];
       
        elementsToCheck.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                console.log(`✅ Element found: ${id}`);
            } else {
                console.error(`❌ Element missing: ${id}`);
            }
        });
       
        // Test if event listeners are attached
        const generateBtn = document.getElementById('dream-generate-button');
        if (generateBtn) {
            const hasListeners = generateBtn.onclick ||
                               generateBtn.addEventListener ||
                               generateBtn.hasAttribute('onclick');
           
            if (hasListeners) {
                console.log('✅ Generate button has event listeners');
            } else {
                console.error('❌ Generate button has no event listeners');
            }
        }
    }
   
    // 5. Test API with minimal request
    function testAPICall() {
        console.log('\n🚀 Testing API Call:');
       
        const testRequest = {
            id: 'test_' + Date.now(),
            user_id: 'diagnostic_user',
            input_text: 'Create a simple hello world FastAPI application',
            options: {
                model_provider: 'auto',
                project_type: 'web_api',
                programming_language: 'python'
            }
        };
       
        fetch('/api/v1/dreamengine/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(testRequest)
        })
            .then(response => {
                console.log(`📡 Validate API Response Status: ${response.status}`);
               
                if (response.ok) {
                    return response.json();
                } else {
                    return response.text().then(text => {
                        throw new Error(`${response.status}: ${text}`);
                    });
                }
            })
            .then(data => {
                console.log('✅ Validate API Success:', data);
            })
            .catch(error => {
                console.error('❌ Validate API Error:', error.message);
            });
    }
   
    // 6. Check for JavaScript errors
    function checkJavaScriptErrors() {
        console.log('\n🐛 JavaScript Error Monitoring:');
       
        window.addEventListener('error', function(e) {
            console.error('❌ JavaScript Error Detected:');
            console.error('  Message:', e.message);
            console.error('  File:', e.filename);
            console.error('  Line:', e.lineno, 'Column:', e.colno);
            console.error('  Stack:', e.error?.stack);
        });
       
        window.addEventListener('unhandledrejection', function(e) {
            console.error('❌ Unhandled Promise Rejection:');
            console.error('  Reason:', e.reason);
        });
       
        console.log('✅ Error monitoring enabled');
    }

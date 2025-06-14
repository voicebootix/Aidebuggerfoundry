
/**
 * DreamEngine - Apple-Inspired Main JavaScript
 * Enhanced interactions with smooth animations and delightful micro-interactions
 */

class DreamEngineUI {
    constructor() {
        this.activeSection = 'build';
        this.optionsExpanded = false;
        this.charCount = 0;
        this.isGenerating = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupCharacterCounter();
        this.setupSmoothScrolling();
        this.setupKeyboardShortcuts();
        this.checkSystemStatus();
        
        console.log('🚀 DreamEngine UI initialized with Apple-inspired interactions');
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
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
        
        // Update active section
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}-section`).classList.add('active');
        
        this.activeSection = sectionName;
        
        // Smooth scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Add subtle haptic feedback simulation
        this.simulateHapticFeedback();
    }
    
    setupInputInteractions() {
        const dreamInput = document.getElementById('dream-input');
        const inputArea = document.querySelector('.input-area');
        
        if (dreamInput) {
            // Focus effects
            dreamInput.addEventListener('focus', () => {
                inputArea.style.transform = 'scale(1.01)';
                inputArea.style.transition = 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)';
            });
            
            dreamInput.addEventListener('blur', () => {
                inputArea.style.transform = 'scale(1)';
            });
            
            // Auto-resize textarea
            dreamInput.addEventListener('input', () => {
                this.autoResizeTextarea(dreamInput);
                this.updateCharacterCount();
            });
            
            // Smooth typing animation
            dreamInput.addEventListener('keydown', () => {
                this.addTypingEffect();
            });
        }
    }
    
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        const newHeight = Math.min(textarea.scrollHeight, 300); // Max height
        textarea.style.height = newHeight + 'px';
        
        // Smooth height transition
        textarea.style.transition = 'height 0.2s ease-out';
    }
    
    addTypingEffect() {
        const inputArea = document.querySelector('.input-area');
        inputArea.style.boxShadow = '0 0 0 4px rgba(0, 122, 255, 0.1)';
        
        setTimeout(() => {
            inputArea.style.boxShadow = '';
        }, 150);
    }
    
    setupCharacterCounter() {
        const dreamInput = document.getElementById('dream-input');
        const charCountElement = document.getElementById('char-count');
        
        if (dreamInput && charCountElement) {
            dreamInput.addEventListener('input', () => {
                this.updateCharacterCount();
            });
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
            if (this.charCount < 50) {
                inputMeta.style.color = 'var(--warning)';
            } else if (this.charCount > 5000) {
                inputMeta.style.color = 'var(--danger)';
            } else {
                inputMeta.style.color = 'var(--label-tertiary)';
            }
            
            // Animate counter
            charCountElement.style.transform = 'scale(1.1)';
            setTimeout(() => {
                charCountElement.style.transform = 'scale(1)';
            }, 150);
        }
    }
    
    setupOptionsPanel() {
        const optionsToggle = document.getElementById('options-toggle');
        const optionsPanel = document.getElementById('options-panel');
        const chevron = document.querySelector('.options-chevron');
        
        if (optionsToggle && optionsPanel) {
            optionsToggle.addEventListener('click', () => {
                this.toggleOptionsPanel();
            });
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
            optionsPanel.style.transform = 'translateY(-10px)';
            
            requestAnimationFrame(() => {
                optionsPanel.style.transition = 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)';
                optionsPanel.style.maxHeight = '500px';
                optionsPanel.style.opacity = '1';
                optionsPanel.style.transform = 'translateY(0)';
            });
        } else {
            optionsPanel.style.transition = 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)';
            optionsPanel.style.maxHeight = '0px';
            optionsPanel.style.opacity = '0';
            optionsPanel.style.transform = 'translateY(-10px)';
            optionsToggle.setAttribute('aria-expanded', 'false');
            
            setTimeout(() => {
                optionsPanel.style.display = 'none';
                optionsPanel.classList.remove('active');
            }, 300);
        }
        
        // Animate chevron
        chevron.style.transform = this.optionsExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
        
        this.simulateHapticFeedback();
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
        
        // Add button hover effects
        this.setupButtonHoverEffects();
    }
    
    setupButtonHoverEffects() {
        const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
        
        buttons.forEach(button => {
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'translateY(-2px)';
                button.style.transition = 'all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1)';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.transform = 'translateY(0)';
            });
            
            button.addEventListener('mousedown', () => {
                button.style.transform = 'translateY(0) scale(0.98)';
            });
            
            button.addEventListener('mouseup', () => {
                button.style.transform = 'translateY(-2px) scale(1)';
            });
        });
    }
    
    async handleValidate() {
        const input = this.getInputText();
        if (!this.validateInput(input)) return;
        
        this.showLoading('Validating your idea...');
        
        try {
            const response = await this.callDreamEngineAPI('/validate', {
                id: this.generateUUID(),
                user_id: 'user_' + Date.now(),
                input_text: input,
                options: this.getGenerationOptions()
            });
            
            this.hideLoading();
            this.showValidationResults(response);
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
            const response = await this.callDreamEngineAPI('/process', {
                id: this.generateUUID(),
                user_id: 'user_' + Date.now(),
                input_text: input,
                options: this.getGenerationOptions()
            });
            
            this.stopGeneration();
            this.showGenerationResults(response);
            this.showNotification('Code generated successfully!', 'success');
        } catch (error) {
            this.stopGeneration();
            this.showNotification('Generation failed: ' + error.message, 'error');
        }
    }
    
    async handleStreaming() {
        const input = this.getInputText();
        if (!this.validateInput(input)) return;
        
        this.startGeneration();
        
        try {
            await this.streamGeneration({
                id: this.generateUUID(),
                user_id: 'user_' + Date.now(),
                input_text: input,
                options: this.getGenerationOptions()
            });
        } catch (error) {
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
    
    async callDreamEngineAPI(endpoint, data) {
        const response = await fetch(`/api/v1/dreamengine${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || 'API request failed');
        }
        
        return await response.json();
    }
    
    async streamGeneration(data) {
        const streamData = { ...data, options: { ...data.options, streaming: true } };
        
        const response = await fetch('/api/v1/dreamengine/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(streamData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to start streaming');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line in buffer
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            this.stopGeneration();
                            return;
                        }
                        
                        try {
                            const chunk = JSON.parse(data);
                            this.handleStreamChunk(chunk);
                        } catch (e) {
                            console.warn('Failed to parse stream chunk:', data);
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }
    
    handleStreamChunk(chunk) {
        if (chunk.is_final) {
            this.stopGeneration();
            this.showNotification('Streaming completed!', 'success');
        } else {
            this.updateProgress(chunk.chunk_index * 10); // Simulated progress
            this.appendStreamContent(chunk.content);
        }
    }
    
    appendStreamContent(content) {
        const codeDisplay = document.getElementById('dream-code-display');
        if (codeDisplay) {
            codeDisplay.textContent += content;
            this.showResults();
        }
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
    
    showResults() {
        const resultsSection = document.getElementById('dream-result-container');
        if (resultsSection) {
            resultsSection.classList.add('active');
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    showValidationResults(data) {
        // Implementation depends on your validation result structure
        console.log('Validation results:', data);
        this.showNotification('Validation completed successfully!', 'success');
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
        // Simple markdown conversion - replace with a proper library if needed
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
                copyBtn.style.color = 'var(--secondary)';
                
                setTimeout(() => {
                    copyBtn.innerHTML = originalContent;
                    copyBtn.style.color = '';
                }, 2000);
            }
        } catch (error) {
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
                
                this.simulateHapticFeedback();
            });
        });
    }
    
    setupVoiceInput() {
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
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.startVoiceRecording(stream);
        } catch (error) {
            this.showNotification('Microphone access denied', 'error');
        }
    }
    
    startVoiceRecording(stream) {
        const mediaRecorder = new MediaRecorder(stream);
        const chunks = [];
        
        mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
        mediaRecorder.onstop = () => this.processVoiceRecording(chunks);
        
        mediaRecorder.start();
        this.showVoiceRecordingUI(mediaRecorder);
    }
    
    showVoiceRecordingUI(mediaRecorder) {
        // Create and show voice recording modal
        const modal = this.createVoiceModal(mediaRecorder);
        document.body.appendChild(modal);
        
        // Auto-stop after 30 seconds
        setTimeout(() => {
            if (mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
        }, 30000);
    }
    
    createVoiceModal(mediaRecorder) {
        const modal = document.createElement('div');
        modal.className = 'voice-modal';
        modal.innerHTML = `
            <div class="voice-modal-content">
                <div class="voice-animation">
                    <div class="voice-pulse"></div>
                </div>
                <h3>Listening...</h3>
                <p>Describe your project idea</p>
                <button class="btn-primary voice-stop-btn">Stop Recording</button>
            </div>
        `;
        
        // Style the modal
        Object.assign(modal.style, {
            position: 'fixed',
            top: '0',
            left: '0',
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: '10000'
        });
        
        Object.assign(modalContent.style, {
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-xl)',
            padding: 'var(--spacing-8)',
            maxWidth: '600px',
            maxHeight: '80vh',
            overflow: 'auto',
            boxShadow: 'var(--shadow-xl)'
        });
        
        // Event handlers
        modal.querySelector('.draft-close-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.querySelectorAll('.draft-load-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => {
                this.loadDraft(drafts[index]);
                document.body.removeChild(modal);
            });
        });
        
        modal.querySelectorAll('.draft-delete-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => {
                this.deleteDraft(index);
                document.body.removeChild(modal);
                // Refresh the modal
                setTimeout(() => this.handleLoadDraft(), 100);
            });
        });
        
        return modal;
    }
    
    loadDraft(draft) {
        const dreamInput = document.getElementById('dream-input');
        if (dreamInput) {
            dreamInput.value = draft.content;
            this.updateCharacterCount();
            this.autoResizeTextarea(dreamInput);
            dreamInput.focus();
            
            // Load options if available
            if (draft.options) {
                this.loadDraftOptions(draft.options);
            }
            
            this.showNotification(`Draft "${draft.title}" loaded`, 'success');
        }
    }
    
    loadDraftOptions(options) {
        // Load generation options from draft
        const selects = {
            'dream-project-type-select': options.project_type,
            'dream-language-select': options.programming_language,
            'dream-database-select': options.database_type,
            'dream-security-select': options.security_level
        };
        
        Object.entries(selects).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element && value) {
                element.value = value;
            }
        });
        
        const checkboxes = {
            'dream-include-tests-checkbox': options.include_tests,
            'dream-include-docs-checkbox': options.include_documentation,
            'dream-include-docker-checkbox': options.include_docker,
            'dream-include-cicd-checkbox': options.include_ci_cd
        };
        
        Object.entries(checkboxes).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element && typeof value === 'boolean') {
                element.checked = value;
            }
        });
    }
    
    deleteDraft(index) {
        const drafts = JSON.parse(localStorage.getItem('dreamengine_drafts') || '[]');
        const deleted = drafts.splice(index, 1)[0];
        localStorage.setItem('dreamengine_drafts', JSON.stringify(drafts));
        this.showNotification(`Draft "${deleted.title}" deleted`, 'success');
    }
    
    setupSmoothScrolling() {
        // Add smooth scrolling for internal links
        document.addEventListener('click', (e) => {
            if (e.target.matches('a[href^="#"]')) {
                e.preventDefault();
                const target = document.querySelector(e.target.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
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
            
            // Command/Ctrl + O to load draft
            if ((e.metaKey || e.ctrlKey) && e.key === 'o') {
                e.preventDefault();
                this.handleLoadDraft();
            }
            
            // Escape to close modals
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.template-modal, .draft-modal, .voice-modal');
                modals.forEach(modal => {
                    if (modal.parentNode) {
                        modal.parentNode.removeChild(modal);
                    }
                });
            }
        });
    }
    
    async checkSystemStatus() {
        try {
            const response = await fetch('/api/v1/dreamengine/health');
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.updateStatusIndicator('online', 'System Online');
            } else {
                this.updateStatusIndicator('offline', 'System Offline');
            }
        } catch (error) {
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
            statusDot.style.backgroundColor = status === 'online' ? 'var(--secondary)' : 'var(--danger)';
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
        const toast = document.getElementById('dream-error');
        if (!toast) return;
        
        toast.textContent = message;
        toast.className = `error-toast ${type}`;
        toast.classList.add('show');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
        
        // Remove on click
        toast.addEventListener('click', () => {
            toast.classList.remove('show');
        });
    }
    
    simulateHapticFeedback() {
        // Simulate haptic feedback for supported devices
        if (navigator.vibrate) {
            navigator.vibrate(10);
        }
    }
    
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
}

// Initialize the UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dreamEngineUI = new DreamEngineUI();
    
    // Add some CSS for modals and animations
    const additionalStyles = document.createElement('style');
    additionalStyles.textContent = `
        .template-modal, .draft-modal, .voice-modal {
            backdrop-filter: blur(10px);
            animation: fadeIn 0.3s ease-out;
        }
        
        .template-modal-content, .draft-modal-content {
            animation: slideUp 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        
        .template-card, .draft-card {
            padding: var(--spacing-6);
            border: 1px solid var(--gray-3);
            border-radius: var(--radius-large);
            margin-bottom: var(--spacing-4);
            transition: all var(--transition-fast);
        }
        
        .template-card:hover, .draft-card:hover {
            border-color: var(--primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
        }
        
        .template-card h3, .draft-card h3 {
            margin-bottom: var(--spacing-2);
            color: var(--label-primary);
        }
        
        .template-card p, .draft-preview {
            color: var(--label-secondary);
            margin-bottom: var(--spacing-4);
        }
        
        .draft-date {
            font-size: var(--font-size-footnote);
            color: var(--label-tertiary);
            margin-bottom: var(--spacing-4);
        }
        
        .draft-actions {
            display: flex;
            gap: var(--spacing-3);
        }
        
        .template-close-btn, .draft-close-btn {
            position: absolute;
            top: var(--spacing-4);
            right: var(--spacing-4);
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: var(--label-secondary);
            width: 32px;
            height: 32px;
            border-radius: var(--radius-small);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .template-close-btn:hover, .draft-close-btn:hover {
            background-color: var(--gray-2);
            color: var(--label-primary);
        }
        
        .voice-modal-content {
            background: var(--bg-primary);
            border-radius: var(--radius-xl);
            padding: var(--spacing-12);
            text-align: center;
            box-shadow: var(--shadow-xl);
        }
        
        .voice-animation {
            width: 100px;
            height: 100px;
            margin: 0 auto var(--spacing-6);
            position: relative;
        }
        
        .voice-pulse {
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, var(--primary), var(--purple));
            border-radius: 50%;
            animation: pulse 2s infinite ease-in-out;
        }
        
        .deployment-step {
            padding: var(--spacing-6);
            background: var(--bg-secondary);
            border-radius: var(--radius-large);
            margin-bottom: var(--spacing-6);
        }
        
        .deployment-step h4 {
            color: var(--label-primary);
            margin-bottom: var(--spacing-4);
        }
        
        .deployment-command {
            display: block;
            background: var(--bg-primary);
            border: 1px solid var(--gray-3);
            border-radius: var(--radius-medium);
            padding: var(--spacing-4);
            font-family: var(--font-mono);
            font-size: var(--font-size-footnote);
            margin: var(--spacing-4) 0;
            overflow-x: auto;
        }
        
        .deployment-verification {
            font-style: italic;
            color: var(--label-secondary);
            margin: var(--spacing-3) 0 0 0;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideUp {
            from { 
                opacity: 0;
                transform: translateY(30px);
            }
            to { 
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% { 
                transform: scale(1);
                opacity: 1;
            }
            50% { 
                transform: scale(1.1);
                opacity: 0.7;
            }
        }
        
        /* Responsive modal styles */
        @media (max-width: 768px) {
            .template-modal-content, .draft-modal-content {
                margin: var(--spacing-4);
                max-width: calc(100vw - var(--spacing-8));
                max-height: calc(100vh - var(--spacing-8));
            }
            
            .template-card, .draft-card {
                padding: var(--spacing-4);
            }
            
            .draft-actions {
                flex-direction: column;
            }
            
            .voice-modal-content {
                margin: var(--spacing-4);
                padding: var(--spacing-8);
            }
        }
    `;
    document.head.appendChild(additionalStyles);
});

// Export for global access
window.DreamEngineUI = DreamEngineUI;10000'
        });
        
        const stopBtn = modal.querySelector('.voice-stop-btn');
        stopBtn.addEventListener('click', () => {
            mediaRecorder.stop();
            document.body.removeChild(modal);
        });
        
        return modal;
    }
    
    async processVoiceRecording(chunks) {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.webm');
        
        this.showLoading('Processing voice input...');
        
        try {
            const response = await fetch('/api/v1/voice', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Voice processing failed');
            }
            
            const result = await response.json();
            this.hideLoading();
            
            // Update input with transcribed text
            const dreamInput = document.getElementById('dream-input');
            if (dreamInput && result.transcribed_text) {
                dreamInput.value = result.transcribed_text;
                this.updateCharacterCount();
                this.autoResizeTextarea(dreamInput);
                this.showNotification('Voice input processed successfully!', 'success');
            }
        } catch (error) {
            this.hideLoading();
            this.showNotification('Voice processing failed: ' + error.message, 'error');
        }
    }
    
    setupTemplates() {
        const templateBtn = document.getElementById('template-button');
        if (templateBtn) {
            templateBtn.addEventListener('click', () => this.showTemplateModal());
        }
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
   - Products with variants (size, color)
   - Categories and subcategories
   - Inventory tracking
   - Product search and filtering

2. User management
   - Customer registration and authentication
   - User profiles and addresses
   - Admin user roles

3. Shopping cart and checkout
   - Add/remove items from cart
   - Calculate totals with tax
   - Coupon and discount system

4. Order processing
   - Order creation and tracking
   - Order history
   - Email notifications

5. Payment integration (Stripe)
6. PostgreSQL database with optimized queries
7. Redis caching for performance`
            },
            {
                name: 'Blog Platform API',
                description: 'Content management system with social features',
                content: `Create a modern blog platform API featuring:

1. Content Management
   - Create, edit, delete blog posts
   - Rich text content with markdown support
   - Image upload and management
   - SEO-friendly URLs

2. User System
   - Author registration and profiles
   - Role-based permissions (author, editor, admin)
   - User authentication with social login options

3. Social Features
   - Comments system with moderation
   - Like and share functionality
   - Follow authors
   - Email subscriptions

4. Advanced Features
   - Full-text search
   - Tag and category system
   - Analytics and view tracking
   - RSS feed generation

Use FastAPI with PostgreSQL and implement proper caching strategies.`
            }
        ];
        
        const modal = this.createTemplateModal(templates);
        document.body.appendChild(modal);
    }
    
    createTemplateModal(templates) {
        const modal = document.createElement('div');
        modal.className = 'template-modal';
        
        const modalContent = document.createElement('div');
        modalContent.className = 'template-modal-content';
        
        modalContent.innerHTML = `
            <div class="template-modal-header">
                <h2>Choose a Template</h2>
                <button class="template-close-btn">×</button>
            </div>
            <div class="template-modal-body">
                ${templates.map((template, index) => `
                    <div class="template-card" data-template="${index}">
                        <h3>${template.name}</h3>
                        <p>${template.description}</p>
                        <button class="btn-primary template-select-btn">Use Template</button>
                    </div>
                `).join('')}
            </div>
        `;
        
        modal.appendChild(modalContent);
        
        // Style the modal
        Object.assign(modal.style, {
            position: 'fixed',
            top: '0',
            left: '0',
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: '10000'
        });
        
        Object.assign(modalContent.style, {
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-xl)',
            padding: 'var(--spacing-8)',
            maxWidth: '600px',
            maxHeight: '80vh',
            overflow: 'auto',
            boxShadow: 'var(--shadow-xl)'
        });
        
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
            
            // Smooth scroll to input
            dreamInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
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
        const draft = {
            id: this.generateUUID(),
            title,
            content: input,
            options: this.getGenerationOptions(),
            timestamp: new Date().toISOString()
        };
        
        const drafts = JSON.parse(localStorage.getItem('dreamengine_drafts') || '[]');
        drafts.push(draft);
        localStorage.setItem('dreamengine_drafts', JSON.stringify(drafts));
        
        this.showNotification(`Draft "${title}" saved`, 'success');
    }
    
    handleLoadDraft() {
        const drafts = JSON.parse(localStorage.getItem('dreamengine_drafts') || '[]');
        
        if (drafts.length === 0) {
            this.showNotification('No drafts found', 'error');
            return;
        }
        
        const draftModal = this.createDraftModal(drafts);
        document.body.appendChild(draftModal);
    }
    
    createDraftModal(drafts) {
        const modal = document.createElement('div');
        modal.className = 'draft-modal';
        
        const modalContent = document.createElement('div');
        modalContent.className = 'draft-modal-content';
        
        modalContent.innerHTML = `
            <div class="draft-modal-header">
                <h2>Load Draft</h2>
                <button class="draft-close-btn">×</button>
            </div>
            <div class="draft-modal-body">
                ${drafts.map((draft, index) => `
                    <div class="draft-card" data-draft="${index}">
                        <h3>${draft.title}</h3>
                        <p class="draft-preview">${draft.content.substring(0, 100)}...</p>
                        <p class="draft-date">${new Date(draft.timestamp).toLocaleString()}</p>
                        <div class="draft-actions">
                            <button class="btn-primary draft-load-btn">Load</button>
                            <button class="btn-secondary draft-delete-btn">Delete</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        modal.appendChild(modalContent);
        
        // Style the modal (similar to template modal)
        Object.assign(modal.style, {
            position: 'fixed',
            top: '0',
            left: '0',
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: '
Made with
1

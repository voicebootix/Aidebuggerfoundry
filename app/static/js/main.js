/**
 * DreamEngine Frontend - Working Implementation
 * This ensures all buttons and functions work properly
 */

console.log('🚀 DreamEngine JavaScript Loading...');

// Global state
let dreamEngine = {
    isGenerating: false,
    currentRequest: null,
    mediaRecorder: null,
    isRecording: false
};

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 DOM loaded, initializing DreamEngine...');
    initializeDreamEngine();
});

function initializeDreamEngine() {
    try {
        // Initialize all event listeners
        setupNavigation();
        setupInputHandlers();
        setupActionButtons();
        setupOptionsToggle();
        setupVoiceInput();
        setupTemplateButton();
        setupFileOperations();
        setupInfoTabs();
        setupDraftManagement();
       
        // Check health
        checkSystemHealth();
       
        console.log('✅ DreamEngine initialized successfully!');
        showNotification('DreamEngine ready!', 'success');
       
    } catch (error) {
        console.error('❌ Failed to initialize DreamEngine:', error);
        showNotification('Failed to initialize DreamEngine', 'error');
    }
}

// Navigation Functions
function setupNavigation() {
    const navPills = document.querySelectorAll('.nav-pill');
    navPills.forEach(pill => {
        pill.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.dataset.section;
            switchSection(section);
        });
    });
   
    // New Project button
    const newProjectBtn = document.getElementById('new-project-button');
    if (newProjectBtn) {
        newProjectBtn.addEventListener('click', handleNewProject);
    }
}

function switchSection(sectionName) {
    console.log(`🔄 Switching to ${sectionName} section`);
   
    // Update nav pills
    document.querySelectorAll('.nav-pill').forEach(pill => {
        pill.classList.remove('active');
    });
   
    const activeNav = document.querySelector(`[data-section="${sectionName}"]`);
    if (activeNav) {
        activeNav.classList.add('active');
    }
   
    // Update sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
   
    const activeSection = document.getElementById(`${sectionName}-section`);
    if (activeSection) {
        activeSection.classList.add('active');
    }
   
    showNotification(`Switched to ${sectionName.charAt(0).toUpperCase() + sectionName.slice(1)}`, 'info');
}

// Input Handlers
function setupInputHandlers() {
    const dreamInput = document.getElementById('dream-input');
    if (dreamInput) {
        dreamInput.addEventListener('input', function() {
            updateCharacterCount();
            autoResizeTextarea(this);
        });
       
        // Initialize character count
        updateCharacterCount();
    }
}

function updateCharacterCount() {
    const dreamInput = document.getElementById('dream-input');
    const charCount = document.getElementById('char-count');
   
    if (dreamInput && charCount) {
        const count = dreamInput.value.length;
        charCount.textContent = count;
       
        // Update color based on length
        const inputMeta = document.querySelector('.input-meta');
        if (inputMeta) {
            if (count < 50) {
                inputMeta.style.color = '#ff9500'; // Warning orange
            } else if (count > 5000) {
                inputMeta.style.color = '#ff3b30'; // Error red
            } else {
                inputMeta.style.color = '#8e8e93'; // Normal gray
            }
        }
    }
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 300);
    textarea.style.height = newHeight + 'px';
}

// Action Buttons
function setupActionButtons() {
    // Validate Idea button
    const validateBtn = document.getElementById('dream-validate-button');
    if (validateBtn) {
        validateBtn.addEventListener('click', handleValidateIdea);
    }
   
    // Generate Code button  
    const generateBtn = document.getElementById('dream-generate-button');
    if (generateBtn) {
        generateBtn.addEventListener('click', handleGenerateCode);
    }
   
    // Stream Generation button
    const streamBtn = document.getElementById('dream-streaming-button');
    if (streamBtn) {
        streamBtn.addEventListener('click', handleStreamGeneration);
    }
}

async function handleValidateIdea() {
    console.log('🔍 Validating idea...');
   
    const inputText = getInputText();
    if (!validateInput(inputText)) {
        return;
    }
   
    showLoading('Validating your idea...');
   
    try {
        const requestData = {
            id: generateUUID(),
            user_id: generateUserId(),
            input_text: inputText,
            options: getGenerationOptions()
        };
       
        const response = await fetch('/api/v1/dreamengine/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
       
        if (!response.ok) {
            throw new Error(`Validation failed: ${response.statusText}`);
        }
       
        const result = await response.json();
        hideLoading();
        showValidationResults(result);
        showNotification('Idea validated successfully!', 'success');
       
    } catch (error) {
        console.error('❌ Validation error:', error);
        hideLoading();
        showNotification(`Validation failed: ${error.message}`, 'error');
    }
}

async function handleGenerateCode() {
    console.log('⚡ Generating code...');
   
    const inputText = getInputText();
    if (!validateInput(inputText)) {
        return;
    }
   
    startGeneration();
   
    try {
        const requestData = {
            id: generateUUID(),
            user_id: generateUserId(),
            input_text: inputText,
            options: getGenerationOptions()
        };
       
        const response = await fetch('/api/v1/dreamengine/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
       
        if (!response.ok) {
            throw new Error(`Generation failed: ${response.statusText}`);
        }
       
        const result = await response.json();
        stopGeneration();
        showGenerationResults(result);
        showNotification('Code generated successfully!', 'success');
       
    } catch (error) {
        console.error('❌ Generation error:', error);
        stopGeneration();
        showNotification(`Generation failed: ${error.message}`, 'error');
    }
}

async function handleStreamGeneration() {
    console.log('🌊 Starting stream generation...');
   
    const inputText = getInputText();
    if (!validateInput(inputText)) {
        return;
    }
   
    startGeneration();
   
    try {
        const requestData = {
            id: generateUUID(),
            user_id: generateUserId(),
            input_text: inputText,
            options: getGenerationOptions()
        };
       
        const response = await fetch('/api/v1/dreamengine/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
       
        if (!response.ok) {
            throw new Error(`Streaming failed: ${response.statusText}`);
        }
       
        handleStreamResponse(response);
       
    } catch (error) {
        console.error('❌ Streaming error:', error);
        stopGeneration();
        showNotification(`Streaming failed: ${error.message}`, 'error');
    }
}

async function handleStreamResponse(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let accumulatedCode = '';
   
    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
           
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line
           
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        stopGeneration();
                        showNotification('Streaming completed!', 'success');
                        return;
                    }
                   
                    try {
                        const chunk = JSON.parse(data);
                        handleStreamChunk(chunk);
                    } catch (e) {
                        console.warn('Failed to parse chunk:', data);
                    }
                }
            }
        }
    } finally {
        reader.releaseLock();
        stopGeneration();
    }
}

function handleStreamChunk(chunk) {
    // Update progress
    if (chunk.progress !== undefined) {
        updateProgress(chunk.progress);
    }
   
    // Update status
    if (chunk.content_type === 'status') {
        updateProgressStatus(chunk.content);
    }
   
    // Accumulate code content
    if (chunk.content_type === 'file_content') {
        appendCodeContent(chunk.content);
    }
   
    // Handle final chunk
    if (chunk.is_final) {
        stopGeneration();
        showNotification('Streaming completed!', 'success');
    }
}

// Helper Functions
function getInputText() {
    const dreamInput = document.getElementById('dream-input');
    return dreamInput ? dreamInput.value.trim() : '';
}

function validateInput(inputText) {
    if (!inputText) {
        showNotification('Please enter your project description', 'error');
        const dreamInput = document.getElementById('dream-input');
        if (dreamInput) dreamInput.focus();
        return false;
    }
   
    if (inputText.length < 50) {
        showNotification('Please provide more details (minimum 50 characters)', 'error');
        const dreamInput = document.getElementById('dream-input');
        if (dreamInput) dreamInput.focus();
        return false;
    }
   
    return true;
}

function getGenerationOptions() {
    return {
        model_provider: 'auto',
        project_type: getSelectValue('dream-project-type-select'),
        programming_language: getSelectValue('dream-language-select'),
        database_type: getSelectValue('dream-database-select'),
        security_level: getSelectValue('dream-security-select') || 'standard',
        include_tests: getCheckboxValue('dream-include-tests-checkbox'),
        include_documentation: getCheckboxValue('dream-include-docs-checkbox'),
        include_docker: getCheckboxValue('dream-include-docker-checkbox'),
        include_ci_cd: getCheckboxValue('dream-include-cicd-checkbox'),
        temperature: 0.7
    };
}

function getSelectValue(id) {
    const element = document.getElementById(id);
    return element ? element.value : null;
}

function getCheckboxValue(id) {
    const element = document.getElementById(id);
    return element ? element.checked : false;
}

// Generation State Management
function startGeneration() {
    dreamEngine.isGenerating = true;
    showProgress();
    updateProgress(0);
    updateProgressStatus('Starting generation...');
   
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

function stopGeneration() {
    dreamEngine.isGenerating = false;
    hideProgress();
   
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

function showProgress() {
    const progressSection = document.getElementById('progress-section');
    if (progressSection) {
        progressSection.classList.add('active');
        progressSection.scrollIntoView({ behavior: 'smooth' });
    }
}

function hideProgress() {
    const progressSection = document.getElementById('progress-section');
    if (progressSection) {
        progressSection.classList.remove('active');
    }
}

function updateProgress(percentage) {
    const progressBar = document.getElementById('dream-progress-bar');
    if (progressBar) {
        progressBar.style.width = `${Math.min(percentage, 100)}%`;
    }
}

function updateProgressStatus(status) {
    const progressStatus = document.getElementById('dream-progress-status');
    if (progressStatus) {
        progressStatus.textContent = status;
    }
}

// Results Display
function showValidationResults(data) {
    console.log('📊 Validation results:', data);
   
    if (data.validation_result && data.validation_result.overall_score) {
        const score = data.validation_result.overall_score;
        const feasibility = data.validation_result.feasibility;
        showNotification(`Validation Score: ${score}/10 (${feasibility} feasibility)`, 'success');
    } else {
        showNotification('Idea validation completed', 'success');
    }
}

function showGenerationResults(data) {
    console.log('📁 Generation results:', data);
   
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
   
    // Display files
    if (data.files && data.files.length > 0) {
        populateFileSelector(data.files);
        displayFile(data.files[0]);
    }
   
    // Display explanation
    if (data.explanation) {
        const explanationPanel = document.getElementById('dream-explanation');
        if (explanationPanel) {
            explanationPanel.innerHTML = formatText(data.explanation);
        }
    }
   
    // Display architecture
    if (data.architecture) {
        const architecturePanel = document.getElementById('dream-architecture');
        if (architecturePanel) {
            architecturePanel.innerHTML = formatText(data.architecture);
        }
    }
   
    // Display deployment steps
    if (data.deployment_steps) {
        displayDeploymentSteps(data.deployment_steps);
    }
}

function populateFileSelector(files) {
    const fileSelector = document.getElementById('dream-file-selector');
    if (!fileSelector) return;
   
    fileSelector.innerHTML = '<option value="">Select a file...</option>';
   
    files.forEach((file, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = file.filename;
        fileSelector.appendChild(option);
    });
   
    // Add change listener
    fileSelector.addEventListener('change', function(e) {
        const index = parseInt(e.target.value);
        if (!isNaN(index) && files[index]) {
            displayFile(files[index]);
        }
    });
}

function displayFile(file) {
    const codeDisplay = document.getElementById('dream-code-display');
    const languageElement = document.getElementById('code-language');
   
    if (codeDisplay) {
        codeDisplay.textContent = file.content;
    }
   
    if (languageElement) {
        languageElement.textContent = file.language || 'Text';
    }
}

function appendCodeContent(content) {
    const codeDisplay = document.getElementById('dream-code-display');
    if (codeDisplay) {
        codeDisplay.textContent += content;
        showResults();
    }
}

function showResults() {
    const resultsSection = document.getElementById('dream-result-container');
    if (resultsSection) {
        resultsSection.classList.add('active');
    }
}

function displayDeploymentSteps(steps) {
    const container = document.getElementById('dream-deployment-steps');
    if (!container) return;
   
    container.innerHTML = steps.map(step => `
        <div class="deployment-step">
            <h4>Step ${step.step_number}: ${step.description}</h4>
            ${step.command ? `<code class="deployment-command">${step.command}</code>` : ''}
            ${step.verification ? `<p class="deployment-verification">${step.verification}</p>` : ''}
        </div>
    `).join('');
}

// Options Toggle
function setupOptionsToggle() {
    const optionsToggle = document.getElementById('options-toggle');
    if (optionsToggle) {
        optionsToggle.addEventListener('click', toggleOptions);
    }
}

function toggleOptions() {
    const optionsPanel = document.getElementById('options-panel');
    const optionsToggle = document.getElementById('options-toggle');
   
    if (!optionsPanel || !optionsToggle) return;
   
    const isExpanded = optionsPanel.classList.contains('active');
   
    if (isExpanded) {
        optionsPanel.classList.remove('active');
        optionsPanel.style.display = 'none';
        optionsToggle.setAttribute('aria-expanded', 'false');
    } else {
        optionsPanel.classList.add('active');
        optionsPanel.style.display = 'block';
        optionsToggle.setAttribute('aria-expanded', 'true');
    }
   
    showNotification(`Options ${isExpanded ? 'collapsed' : 'expanded'}`, 'info');
}

// Voice Input
function setupVoiceInput() {
    const voiceBtn = document.getElementById('voice-input-button');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', handleVoiceInput);
    }
}

async function handleVoiceInput() {
    console.log('🎤 Voice input requested');
   
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showNotification('Voice input not supported in this browser', 'error');
        return;
    }
   
    if (dreamEngine.isRecording) {
        stopRecording();
        return;
    }
   
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        startRecording(stream);
    } catch (error) {
        console.error('Microphone access denied:', error);
        showNotification('Microphone access denied', 'error');
    }
}

function startRecording(stream) {
    dreamEngine.mediaRecorder = new MediaRecorder(stream);
    const chunks = [];
   
    dreamEngine.mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
    dreamEngine.mediaRecorder.onstop = () => processVoiceRecording(chunks);
   
    dreamEngine.mediaRecorder.start();
    dreamEngine.isRecording = true;
   
    // Update UI
    const voiceBtn = document.getElementById('voice-input-button');
    if (voiceBtn) {
        voiceBtn.style.backgroundColor = '#ff3b30';
        voiceBtn.title = 'Stop Recording';
    }
   
    showNotification('Recording... Click again to stop', 'info');
   
    // Auto-stop after 30 seconds
    setTimeout(() => {
        if (dreamEngine.isRecording) {
            stopRecording();
        }
    }, 30000);
}

function stopRecording() {
    if (dreamEngine.mediaRecorder && dreamEngine.isRecording) {
        dreamEngine.mediaRecorder.stop();
        dreamEngine.isRecording = false;
       
        // Reset UI
        const voiceBtn = document.getElementById('voice-input-button');
        if (voiceBtn) {
            voiceBtn.style.backgroundColor = '';
            voiceBtn.title = 'Voice Input';
        }
    }
}

async function processVoiceRecording(chunks) {
    const audioBlob = new Blob(chunks, { type: 'audio/webm' });
   
    showLoading('Processing voice input...');
   
    try {
        const formData = new FormData();
        formData.append('audio_file', audioBlob);
       
        const response = await fetch('/api/v1/dreamengine/voice', {
            method: 'POST',
            body: formData
        });
       
        if (!response.ok) {
            throw new Error(`Voice processing failed: ${response.statusText}`);
        }
       
        const result = await response.json();
        hideLoading();
       
        if (result.transcribed_text) {
            const dreamInput = document.getElementById('dream-input');
            if (dreamInput) {
                dreamInput.value = result.transcribed_text;
                updateCharacterCount();
                autoResizeTextarea(dreamInput);
            }
            showNotification('Voice input processed successfully!', 'success');
        }
    } catch (error) {
        console.error('❌ Voice processing error:', error);
        hideLoading();
        showNotification(`Voice processing failed: ${error.message}`, 'error');
    }
}

// Template Button
function setupTemplateButton() {
    const templateBtn = document.getElementById('template-button');
    if (templateBtn) {
        templateBtn.addEventListener('click', showTemplateModal);
    }
}

function showTemplateModal() {
    const templates = [
        {
            name: 'Task Management App',
            content: `Build a to-do list web app with the following features: Users can add tasks, mark them as completed, and delete them. Display tasks in two sections: "Pending" and "Completed". Use HTML, CSS, and JavaScript. Data should be stored locally in the browser using localStorage. Include basic styling so it's mobile-friendly. Each task should have a checkbox and a delete button. Add a title at the top that says "My To-Do List". The input field and add button should be fixed at the top. No backend or authentication needed. Keep the code clean and well-commented.`
        },
        {
            name: 'E-commerce API',
            content: `Create a FastAPI backend for an e-commerce platform with user authentication, product catalog management, shopping cart functionality, order processing, and payment integration using Stripe. Include PostgreSQL database integration, comprehensive API documentation, and proper error handling.`
        },
        {
            name: 'Blog Platform',
            content: `Build a full-stack blog platform with user registration, content management system, comment functionality, and admin dashboard. Include features like post creation, editing, publishing, and social sharing capabilities.`
        }
    ];
   
    // Create modal
    const modal = createModal('Choose a Template',
        templates.map((template, index) => `
            <div class="template-item" data-index="${index}" style="padding: 20px; border: 1px solid #e0e0e0; border-radius: 12px; margin-bottom: 16px; cursor: pointer;">
                <h3 style="margin: 0 0 8px 0;">${template.name}</h3>
                <p style="margin: 0; color: #666; font-size: 14px;">${template.content.substring(0, 100)}...</p>
            </div>
        `).join('')
    );
   
    // Add click handlers
    modal.querySelectorAll('.template-item').forEach((item, index) => {
        item.addEventListener('click', () => {
            useTemplate(templates[index]);
            document.body.removeChild(modal);
        });
    });
}

function useTemplate(template) {
    const dreamInput = document.getElementById('dream-input');
    if (dreamInput) {
        dreamInput.value = template.content;
        updateCharacterCount();
        autoResizeTextarea(dreamInput);
        dreamInput.focus();
    }
   
    showNotification(`Template "${template.name}" loaded`, 'success');
}

// File Operations
function setupFileOperations() {
    const copyBtn = document.getElementById('dream-copy-code-button');
    if (copyBtn) {
        copyBtn.addEventListener('click', copyCode);
    }
   
    const downloadBtn = document.getElementById('dream-download-code-button');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadCode);
    }
}

async function copyCode() {
    const codeDisplay = document.getElementById('dream-code-display');
    if (!codeDisplay) return;
   
    try {
        await navigator.clipboard.writeText(codeDisplay.textContent);
        showNotification('Code copied to clipboard!', 'success');
    } catch (error) {
        showNotification('Failed to copy code', 'error');
    }
}

function downloadCode() {
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
   
    showNotification(`Downloaded ${filename}`, 'success');
}

// Info Tabs
function setupInfoTabs() {
    const tabs = document.querySelectorAll('.info-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
           
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
           
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

// Draft Management
function setupDraftManagement() {
    const saveDraftBtn = document.getElementById('dream-save-draft-button');
    if (saveDraftBtn) {
        saveDraftBtn.addEventListener('click', saveDraft);
    }
   
    const loadDraftBtn = document.getElementById('dream-load-draft-button');
    if (loadDraftBtn) {
        loadDraftBtn.addEventListener('click', loadDraft);
    }
}

function saveDraft() {
    const input = getInputText();
    if (!input) {
        showNotification('Nothing to save', 'error');
        return;
    }
   
    const title = prompt('Enter a title for this draft:') || `Draft ${new Date().toLocaleDateString()}`;
    const draft = {
        id: generateUUID(),
        title,
        content: input,
        options: getGenerationOptions(),
        timestamp: new Date().toISOString()
    };
   
    const drafts = JSON.parse(localStorage.getItem('dreamengine_drafts') || '[]');
    drafts.push(draft);
   
    // Limit to 10 drafts
    if (drafts.length > 10) {
        drafts.shift();
    }
   
    localStorage.setItem('dreamengine_drafts', JSON.stringify(drafts));
    showNotification(`Draft "${title}" saved`, 'success');
}

function loadDraft() {
    const drafts = JSON.parse(localStorage.getItem('dreamengine_drafts') || '[]');
   
    if (drafts.length === 0) {
        showNotification('No drafts found', 'error');
        return;
    }
   
    // Show draft selection modal
    const modal = createModal('Load Draft',
        drafts.map((draft, index) => `
            <div class="draft-item" data-index="${index}" style="padding: 16px; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 12px; cursor: pointer;">
                <h4 style="margin: 0 0 4px 0;">${draft.title}</h4>
                <p style="margin: 0 0 4px 0; color: #666; font-size: 13px;">${draft.content.substring(0, 80)}...</p>
                <small style="color: #999;">${new Date(draft.timestamp).toLocaleString()}</small>
            </div>
        `).join('')
    );
   
    // Add click handlers
    modal.querySelectorAll('.draft-item').forEach((item, index) => {
        item.addEventListener('click', () => {
            const draft = drafts[index];
            const dreamInput = document.getElementById('dream-input');
            if (dreamInput) {
                dreamInput.value = draft.content;
                updateCharacterCount();
                autoResizeTextarea(dreamInput);
            }
            showNotification(`Draft "${draft.title}" loaded`, 'success');
            document.body.removeChild(modal);
        });
    });
}

// Other Functions
function handleNewProject() {
    const dreamInput = document.getElementById('dream-input');
    if (dreamInput) {
        dreamInput.value = '';
        updateCharacterCount();
        autoResizeTextarea(dreamInput);
    }
   
    // Hide results
    const resultsSection = document.getElementById('dream-result-container');
    if (resultsSection) {
        resultsSection.classList.remove('active');
    }
   
    showNotification('New project started', 'success');
}

async function checkSystemHealth() {
    try {
        const response = await fetch('/api/v1/dreamengine/health');
        const data = await response.json();
       
        if (data.status === 'healthy') {
            updateStatusIndicator('online', 'System Online');
        } else {
            updateStatusIndicator('offline', 'System Issues');
        }
    } catch (error) {
        updateStatusIndicator('offline', 'API Unavailable');
        console.warn('Health check failed:', error.message);
    }
}

function updateStatusIndicator(status, text) {
    const indicator = document.getElementById('status-indicator');
    const statusText = indicator?.querySelector('.status-text');
    const statusDot = indicator?.querySelector('.status-dot');
   
    if (statusText) statusText.textContent = text;
    if (statusDot) {
        statusDot.style.backgroundColor = status === 'online' ? '#34c759' : '#ff3b30';
    }
}

// Utility Functions
function showLoading(text = 'Processing...') {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = overlay?.querySelector('.loading-text');
   
    if (loadingText) loadingText.textContent = text;
    if (overlay) overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
}

function showNotification(message, type = 'info') {
    console.log(`📢 ${type.toUpperCase()}: ${message}`);
   
    const toast = document.getElementById('dream-error');
    if (!toast) return;
   
    // Set message and type
    toast.textContent = message;
    toast.className = `error-toast ${type} show`;
   
    // Auto-hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function formatText(text) {
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>');
}

function createModal(title, content) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.5); display: flex; align-items: center;
        justify-content: center; z-index: 10000;
    `;
   
    modal.innerHTML = `
        <div style="background: white; border-radius: 16px; padding: 24px; max-width: 500px; max-height: 80vh; overflow: auto; margin: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0;">${title}</h2>
                <button class="close-btn" style="background: none; border: none; font-size: 24px; cursor: pointer;">×</button>
            </div>
            <div>${content}</div>
        </div>
    `;
   
    // Close handlers
    modal.querySelector('.close-btn').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
   
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
   
    document.body.appendChild(modal);
    return modal;
}

function generateUUID() {
    return 'xxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function generateUserId() {
    return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

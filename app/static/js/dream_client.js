class DreamClient {
    constructor() {
        this.activeGeneration = null;
        this.generatedFiles = {};
        this.contractMode = false;
        this.qualityLevel = 'production';
    }
    
    async generateWithContract(userPrompt, contractId = null) {
        console.log('🚀 Starting enhanced contract-bound generation...');
        
        this.contractMode = !!contractId;
        
        try {
            const response = await fetch('/api/v1/enhanced-generation/generate-with-contract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_prompt: userPrompt,
                    contract_id: contractId,
                    quality_level: this.qualityLevel
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
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
                            this.handleEnhancedGenerationData(parsed);
                        } catch (e) {
                            // Ignore parsing errors for malformed chunks
                        }
                    }
                }
            }
            
        } catch (error) {
            console.error('Enhanced generation failed:', error);
            this.displayGenerationError(error.message);
        }
    }
    
    handleEnhancedGenerationData(data) {
        switch (data.type) {
            case 'generation_started':
                this.displayGenerationStarted(data);
                break;
            case 'status_update':
                this.updateGenerationStatus(data);
                break;
            case 'component_completed':
                this.displayComponentCompleted(data);
                break;
            case 'auto_correction':
                this.displayAutoCorrection(data);
                break;
            case 'generation_completed':
                this.displayGenerationCompleted(data);
                break;
            case 'generation_incomplete':
                this.displayGenerationIncomplete(data);
                break;
            case 'generation_error':
                this.displayGenerationError(data.content);
                break;
        }
    }
    
    displayGenerationStarted(data) {
        const resultsContainer = document.getElementById('generation-results');
        
        resultsContainer.innerHTML = `
            <div class="enhanced-generation-container">
                <div class="generation-header">
                    <h3>⚡ Enhanced Code Generation</h3>
                    ${this.contractMode ? `
                        <div class="contract-mode-indicator">
                            📋 Contract-Bound Generation Active
                        </div>
                    ` : ''}
                </div>
                
                <div class="generation-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="generation-progress-fill" style="width: 0%"></div>
                    </div>
                    <div class="progress-text" id="generation-progress-text">
                        Starting generation...
                    </div>
                </div>
                
                <div class="generation-log" id="generation-log">
                    <div class="log-entry started">
                        <span class="log-time">${new Date().toLocaleTimeString()}</span>
                        <span class="log-message">🚀 Enhanced generation started</span>
                    </div>
                </div>
                
                <div class="generated-files" id="generated-files" style="display: none;">
                    <h4>📁 Generated Files</h4>
                    <div class="files-container" id="files-container"></div>
                </div>
                
                <div class="compliance-tracking" id="compliance-tracking" style="display: none;">
                    <h4>📋 Contract Compliance</h4>
                    <div class="compliance-score">
                        <span class="score-value" id="compliance-score-value">0%</span>
                        <span class="score-label">Contract Requirements Met</span>
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.style.display = 'block';
    }
    
    updateGenerationStatus(data) {
        const progressText = document.getElementById('generation-progress-text');
        const logContainer = document.getElementById('generation-log');
        
        if (progressText) {
            progressText.textContent = data.content;
        }
        
        if (logContainer) {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry status';
            logEntry.innerHTML = `
                <span class="log-time">${new Date().toLocaleTimeString()}</span>
                <span class="log-message">${data.content}</span>
            `;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // Update progress bar (estimate based on content)
        const progressFill = document.getElementById('generation-progress-fill');
        if (progressFill && data.current_component) {
            const components = ['backend_api', 'database', 'frontend', 'integrations'];
            const currentIndex = components.indexOf(data.current_component);
            if (currentIndex >= 0) {
                const progress = ((currentIndex + 1) / components.length) * 80; // Leave 20% for final validation
                progressFill.style.width = `${progress}%`;
            }
        }
    }
    
    displayComponentCompleted(data) {
        const logContainer = document.getElementById('generation-log');
        const filesContainer = document.getElementById('files-container');
        const complianceScore = document.getElementById('compliance-score-value');
        
        // Log completion
        if (logContainer) {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry completed';
            logEntry.innerHTML = `
                <span class="log-time">${new Date().toLocaleTimeString()}</span>
                <span class="log-message">${data.content}</span>
                <span class="compliance-indicator">📊 ${(data.compliance_score * 100).toFixed(1)}%</span>
            `;
            logContainer.appendChild(logEntry);
        }
        
        // Show generated files
        if (filesContainer && data.files) {
            document.getElementById('generated-files').style.display = 'block';
            
            data.files.forEach(filename => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <span class="file-icon">📄</span>
                    <span class="file-name">${filename}</span>
                    <span class="file-status">✅ Generated</span>
                `;
                filesContainer.appendChild(fileItem);
            });
        }
        
        // Update compliance score
        if (complianceScore && data.compliance_score) {
            document.getElementById('compliance-tracking').style.display = 'block';
            complianceScore.textContent = `${(data.compliance_score * 100).toFixed(1)}%`;
        }
    }
    
    displayAutoCorrection(data) {
        const logContainer = document.getElementById('generation-log');
        
        if (logContainer) {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry correction';
            logEntry.innerHTML = `
                <span class="log-time">${new Date().toLocaleTimeString()}</span>
                <span class="log-message">${data.content}</span>
                <span class="corrections-count">🔧 ${data.corrections_made} fixes</span>
            `;
            logContainer.appendChild(logEntry);
        }
    }
    
    displayGenerationCompleted(data) {
        const progressFill = document.getElementById('generation-progress-fill');
        const progressText = document.getElementById('generation-progress-text');
        const logContainer = document.getElementById('generation-log');
        const complianceScore = document.getElementById('compliance-score-value');
        
        // Complete progress bar
        if (progressFill) progressFill.style.width = '100%';
        if (progressText) progressText.textContent = 'Generation completed successfully!';
        
        // Log completion
        if (logContainer) {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry success';
            logEntry.innerHTML = `
                <span class="log-time">${new Date().toLocaleTimeString()}</span>
                <span class="log-message">🎉 Contract-compliant generation completed!</span>
            `;
            logContainer.appendChild(logEntry);
        }
        
        // Update final compliance
        if (complianceScore && data.compliance_report) {
            complianceScore.textContent = `${(data.compliance_report.overall_compliance * 100).toFixed(1)}%`;
        }
        
        // Store generated files
        this.generatedFiles = data.files;
        
        // Show download and deployment options
        this.showCompletionActions(data);
    }
    
    displayGenerationIncomplete(data) {
        const logContainer = document.getElementById('generation-log');
        
        if (logContainer) {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry warning';
            logEntry.innerHTML = `
                <span class="log-time">${new Date().toLocaleTimeString()}</span>
                <span class="log-message">⚠️ Generation needs manual review</span>
            `;
            logContainer.appendChild(logEntry);
        }
        
        // Show issues that need attention
        this.showComplianceIssues(data.compliance_issues);
    }
    
    showCompletionActions(data) {
        const resultsContainer = document.querySelector('.enhanced-generation-container');
        
        const actionsHTML = `
            <div class="completion-actions">
                <h4>🎉 Generation Complete!</h4>
                <div class="action-buttons">
                    <button class="btn-primary" onclick="DreamClient.downloadFiles()">
                        📥 Download All Files
                    </button>
                    <button class="btn-primary" onclick="DreamClient.deployToGitHub()">
                        🚀 Deploy to GitHub
                    </button>
                    <button class="btn-secondary" onclick="DreamClient.viewCode()">
                        👁️ Preview Code
                    </button>
                    ${this.contractMode ? `
                        <button class="btn-secondary" onclick="DreamClient.viewComplianceReport()">
                            📋 View Contract Report
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
        
        resultsContainer.insertAdjacentHTML('beforeend', actionsHTML);
    }
    
    showComplianceIssues(issues) {
        const resultsContainer = document.querySelector('.enhanced-generation-container');
        
        const issuesHTML = `
            <div class="compliance-issues">
                <h4>⚠️ Contract Compliance Issues</h4>
                <ul class="issues-list">
                    ${issues.map(issue => `
                        <li class="issue-item">
                            <strong>${issue.spec_name}:</strong> ${issue.violation_type}
                            ${issue.auto_correctable ? ' <span class="auto-correctable">🔧 Can be auto-fixed</span>' : ' <span class="manual-review">👥 Needs manual review</span>'}
                        </li>
                    `).join('')}
                </ul>
                <div class="issue-actions">
                    <button class="btn-primary" onclick="enhancedDreamClient.requestCorrections()">
                        🔧 Request Auto-Corrections
                    </button>
                    <button class="btn-secondary" onclick="enhancedDreamClient.proceedWithIssues()">
                        ⏭️ Proceed Anyway
                    </button>
                </div>
            </div>
        `;
        
        resultsContainer.insertAdjacentHTML('beforeend', issuesHTML);
    }
    
    displayGenerationError(message) {
        const resultsContainer = document.getElementById('generation-results');
        
        resultsContainer.innerHTML = `
            <div class="generation-error">
                <h3>❌ Generation Failed</h3>
                <p>${message}</p>
                <button class="btn-primary" onclick="enhancedDreamClient.retryGeneration()">
                    🔄 Retry Generation
                </button>
            </div>
        `;
        
        resultsContainer.style.display = 'block';
    }
    
    downloadFiles() {
        if (!this.generatedFiles || Object.keys(this.generatedFiles).length === 0) {
            alert('No files available for download');
            return;
        }
        
        // Create zip file with all generated files
        this.createAndDownloadZip(this.generatedFiles);
    }
    
    createAndDownloadZip(files) {
        // In a real implementation, you'd use a library like JSZip
        console.log('Would create ZIP with files:', Object.keys(files));
        alert('ZIP download would be implemented with JSZip library');
    }
    
    setQualityLevel(level) {
        this.qualityLevel = level;
        console.log(`Quality level set to: ${level}`);
    }
}

// Global instance
window.enhancedDreamClient = new EnhancedDreamClient();

// Integration with existing dream client
if (window.dreamClient) {
    window.dreamClient.generateWithContractConstraints = function(contract) {
        const ideaInput = document.getElementById('idea-input');
        if (ideaInput && ideaInput.value.trim()) {
            window.enhancedDreamClient.generateWithContract(
                ideaInput.value.trim(),
                contract.contract_id
            );
        }
    };
}

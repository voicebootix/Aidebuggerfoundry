class SmartContractClient {
    constructor() {
        this.activeContract = null;
        this.complianceMonitor = null;
    }
    
    async createContract(strategyOutput, founderInput) {
        console.log('📋 Creating technical specification contract...');
        
        try {
            const response = await fetch('/api/v1/smart-contracts/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    strategy_output: strategyOutput,
                    founder_input: founderInput
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.activeContract = result.contract;
                this.displayContractReview(result.contract);
            }
            
        } catch (error) {
            console.error('Contract creation failed:', error);
        }
    }
    
    displayContractReview(contract) {
        const contractModal = document.createElement('div');
        contractModal.className = 'smart-contract-modal';
        contractModal.id = 'smart-contract-modal';
        
        contractModal.innerHTML = `
            <div class="contract-content">
                <div class="contract-header">
                    <h2>📋 Technical Specification Contract</h2>
                    <p class="contract-subtitle">Review the AI's commitments for your project</p>
                </div>
                
                <div class="contract-sections">
                    <div class="platform-commitments">
                        <h3>🤖 What Our AI Will Do</h3>
                        <ul class="commitment-list">
                            ${contract.platform_commitments.map(commitment => 
                                `<li>✅ ${commitment}</li>`
                            ).join('')}
                        </ul>
                    </div>
                    
                    <div class="technical-specs">
                        <h3>⚙️ Technical Requirements</h3>
                        <div class="specs-grid">
                            ${contract.technical_specifications.map(spec => 
                                `<div class="spec-card">
                                    <h4>${spec.name}</h4>
                                    <p>${spec.description}</p>
                                    <div class="spec-priority ${spec.priority.toLowerCase()}">${spec.priority} Priority</div>
                                </div>`
                            ).join('')}
                        </div>
                    </div>
                    
                    <div class="quality-standards">
                        <h3>🎯 Quality Standards</h3>
                        <div class="quality-grid">
                            <div class="quality-item">
                                <strong>Code Style:</strong> Consistent, well-documented
                            </div>
                            <div class="quality-item">
                                <strong>Functionality:</strong> Working endpoints, error handling
                            </div>
                            <div class="quality-item">
                                <strong>Structure:</strong> Modular, scalable architecture
                            </div>
                        </div>
                    </div>
                    
                    <div class="limitations">
                        <h3>⚠️ Important Notes</h3>
                        <ul class="limitation-list">
                            ${contract.platform_limitations.map(limitation => 
                                `<li>${limitation}</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
                
                <div class="contract-actions">
                    <button class="btn-primary" onclick="smartContractClient.approveContract()">
                        ✅ Approve & Start Generation
                    </button>
                    <button class="btn-secondary" onclick="smartContractClient.modifyRequirements()">
                        📝 Modify Requirements
                    </button>
                    <button class="btn-secondary" onclick="smartContractClient.cancelContract()">
                        ❌ Cancel
                    </button>
                </div>
                
                <div class="contract-footer">
                    <p><small>📝 This is a technical specification agreement. Our AI will follow these requirements to the best of its ability.</small></p>
                </div>
            </div>
        `;
        
        document.body.appendChild(contractModal);
    }
    
    async approveContract() {
        if (!this.activeContract) return;
        
        try {
            const response = await fetch('/api/v1/smart-contracts/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contract_id: this.activeContract.contract_id,
                    founder_approval: true
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'approved') {
                this.hideContractModal();
                this.startComplianceMonitoring();
                this.triggerContractBoundGeneration();
            }
            
        } catch (error) {
            console.error('Contract approval failed:', error);
        }
    }
    
    triggerContractBoundGeneration() {
        console.log('🚀 Starting contract-bound code generation...');
        
        // Add compliance tracking to the generation interface
        this.addComplianceTracker();
        
        // Trigger the actual code generation with contract constraints
        if (window.dreamClient) {
            window.dreamClient.generateWithContractConstraints(this.activeContract);
        }
    }
    
    addComplianceTracker() {
        const generationArea = document.querySelector('.generation-container');
        
        if (generationArea) {
            const complianceTracker = document.createElement('div');
            complianceTracker.className = 'compliance-tracker';
            complianceTracker.id = 'compliance-tracker';
            
            complianceTracker.innerHTML = `
                <div class="compliance-header">
                    <h4>📋 Contract Compliance</h4>
                    <div class="compliance-score" id="compliance-score">
                        <span class="score-value">0%</span>
                        <span class="score-label">Specifications Met</span>
                    </div>
                </div>
                
                <div class="compliance-details">
                    <div class="compliance-item">
                        <span class="compliance-label">Technical Specs:</span>
                        <span class="compliance-status" id="tech-specs-status">Checking...</span>
                    </div>
                    <div class="compliance-item">
                        <span class="compliance-label">Quality Standards:</span>
                        <span class="compliance-status" id="quality-status">Checking...</span>
                    </div>
                    <div class="compliance-item">
                        <span class="compliance-label">Feature Implementation:</span>
                        <span class="compliance-status" id="features-status">Checking...</span>
                    </div>
                </div>
                
                <div class="compliance-violations" id="compliance-violations" style="display: none;">
                    <h5>⚠️ Issues Detected</h5>
                    <ul id="violations-list"></ul>
                </div>
            `;
            
            generationArea.insertBefore(complianceTracker, generationArea.firstChild);
        }
    }
    
    startComplianceMonitoring() {
        console.log('🔍 Starting real-time compliance monitoring...');
        
        this.complianceMonitor = setInterval(async () => {
            const compliance = await this.checkCompliance();
            this.updateComplianceDisplay(compliance);
        }, 3000);
    }
    
    async checkCompliance() {
        if (!this.activeContract) return null;
        
        try {
            const response = await fetch(`/api/v1/smart-contracts/${this.activeContract.contract_id}/compliance`);
            return await response.json();
        } catch (error) {
            console.error('Compliance check failed:', error);
            return null;
        }
    }
    
    updateComplianceDisplay(compliance) {
        if (!compliance) return;
        
        const scoreElement = document.querySelector('#compliance-score .score-value');
        if (scoreElement) {
            const percentage = (compliance.overall_compliance * 100).toFixed(1);
            scoreElement.textContent = `${percentage}%`;
        }
        
        // Update status indicators
        this.updateStatusIndicator('tech-specs-status', compliance.specifications_met, compliance.specifications_checked);
        
        // Show violations if any
        if (compliance.violations_detected && compliance.violations_detected.length > 0) {
            this.displayViolations(compliance.violations_detected);
        }
    }
    
    updateStatusIndicator(elementId, met, total) {
        const element = document.getElementById(elementId);
        if (element) {
            if (met === total) {
                element.textContent = '✅ All requirements met';
                element.className = 'compliance-status success';
            } else {
                element.textContent = `⚠️ ${met}/${total} requirements met`;
                element.className = 'compliance-status warning';
            }
        }
    }
    
    displayViolations(violations) {
        const violationsContainer = document.getElementById('compliance-violations');
        const violationsList = document.getElementById('violations-list');
        
        if (violationsContainer && violationsList) {
            violationsList.innerHTML = violations.map(violation => 
                `<li class="violation-item">
                    <strong>${violation.spec_name}:</strong> ${violation.violation_type}
                    ${violation.auto_correctable ? ' <span class="auto-fix">🔧 Auto-fixing...</span>' : ''}
                </li>`
            ).join('');
            
            violationsContainer.style.display = 'block';
        }
    }
    
    hideContractModal() {
        const modal = document.getElementById('smart-contract-modal');
        if (modal) {
            modal.remove();
        }
    }
}

// Global instance
window.smartContractClient = new SmartContractClient();

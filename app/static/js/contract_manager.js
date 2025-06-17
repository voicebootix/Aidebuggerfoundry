class ContractManager {
    constructor() {
        this.activeContract = null;
        this.contractHistory = [];
        this.complianceMonitor = null;
    }
    
    async createContract(strategyAnalysis, founderClarifications) {
        console.log('📋 Creating formal contract...');
        
        try {
            const response = await fetch('/api/v1/contracts/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    strategy_analysis: strategyAnalysis,
                    founder_clarifications: founderClarifications
                })
            });
            
            const contract = await response.json();
            
            if (contract.status === 'success') {
                this.activeContract = contract.contract;
                this.displayContractForApproval(contract.contract);
            }
            
        } catch (error) {
            console.error('Contract creation failed:', error);
        }
    }
    
    displayContractForApproval(contract) {
        const contractModal = document.createElement('div');
        contractModal.className = 'contract-approval-modal';
        
        contractModal.innerHTML = `
            <div class="contract-content">
                <div class="contract-header">
                    <h2>📋 Formal Development Contract</h2>
                    <p><strong>Contract ID:</strong> ${contract.contract_id}</p>
                </div>
                
                <div class="contract-sections">
                    <div class="guaranteed-deliverables">
                        <h3>✅ Platform Guarantees</h3>
                        <ul>
                            ${contract.platform_guarantees.map(guarantee => 
                                `<li>${guarantee}</li>`
                            ).join('')}
                        </ul>
                    </div>
                    
                    <div class="technical-specs">
                        <h3>⚙️ Technical Specifications</h3>
                        <p><strong>API Endpoints:</strong> ${Object.keys(contract.technical_specifications.api_endpoints).length}</p>
                        <p><strong>Database Tables:</strong> ${Object.keys(contract.technical_specifications.database_schemas).length}</p>
                        <p><strong>Frontend Components:</strong> ${Object.keys(contract.technical_specifications.frontend_components).length}</p>
                    </div>
                    
                    <div class="legal-terms">
                        <h3>⚖️ Legal Framework</h3>
                        <p><strong>Platform Liability:</strong> Covered up to $1M</p>
                        <p><strong>Response Times:</strong> Critical issues within 2 hours</p>
                        <p><strong>Code Ownership:</strong> You own 100% of generated code</p>
                    </div>
                    
                    <div class="founder-obligations">
                        <h3>👤 Your Responsibilities</h3>
                        <ul>
                            ${contract.founder_obligations.map(obligation => 
                                `<li>${obligation}</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
                
                <div class="contract-actions">
                    <button class="btn-primary" onclick="contractManager.approveContract()">
                        ✅ I Approve This Contract
                    </button>
                    <button class="btn-secondary" onclick="contractManager.requestChanges()">
                        📝 Request Changes
                    </button>
                    <button class="btn-secondary" onclick="contractManager.cancelContract()">
                        ❌ Cancel
                    </button>
                </div>
                
                <div class="contract-legal-notice">
                    <p><small>⚖️ This is a legally binding agreement. By approving, you agree to the terms and conditions outlined above.</small></p>
                </div>
            </div>
        `;
        
        document.body.appendChild(contractModal);
    }
    
    async approveContract() {
        if (!this.activeContract) return;
        
        try {
            const response = await fetch('/api/v1/contracts/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contract_id: this.activeContract.contract_id,
                    founder_signature: 'DIGITAL_SIGNATURE_' + Date.now()
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'approved') {
                this.startContractMonitoring();
                this.hideContractModal();
                this.triggerCodeGeneration();
            }
            
        } catch (error) {
            console.error('Contract approval failed:', error);
        }
    }
    
    startContractMonitoring() {
        console.log('🔍 Starting real-time contract monitoring...');
        
        this.complianceMonitor = setInterval(async () => {
            const compliance = await this.checkCompliance();
            this.updateComplianceDisplay(compliance);
        }, 2000);
    }
    
    async checkCompliance() {
        try {
            const response = await fetch(`/api/v1/contracts/${this.activeContract.contract_id}/compliance`);
            return await response.json();
        } catch (error) {
            console.error('Compliance check failed:', error);
            return { compliance_score: 0, violations: [] };
        }
    }
    
    updateComplianceDisplay(compliance) {
        const complianceIndicator = document.getElementById('contract-compliance');
        
        if (complianceIndicator) {
            const score = compliance.compliance_score * 100;
            complianceIndicator.innerHTML = `
                <div class="compliance-score">
                    <span class="score-value">${score.toFixed(1)}%</span>
                    <span class="score-label">Contract Compliance</span>
                </div>
                ${compliance.violations.length > 0 ? `
                    <div class="violations-alert">
                        ⚠️ ${compliance.violations.length} violations detected - auto-correcting...
                    </div>
                ` : ''}
            `;
        }
    }
}

// Global instance
window.contractManager = new ContractManager();

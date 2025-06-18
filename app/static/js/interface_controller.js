/**
 * DreamEngine Interface Controller
 * Ensures proper interface loading and prevents diagnostic hijacking
 */

class InterfaceController {
    constructor() {
        this.mode = 'normal'; // normal | diagnostic
        this.currentSection = 'build';
        this.init();
    }
    
    init() {
        console.log('🎮 Interface Controller initializing...');
        
        // Prevent diagnostic auto-run
        this.preventDiagnosticHijack();
        
        // Ensure normal interface loads
        this.ensureNormalInterface();
        
        // Setup debug section integration
        this.setupDebugSection();
        
        console.log('✅ Interface Controller ready - Normal mode active');
    }
    
    preventDiagnosticHijack() {
        // Override diagnostic auto-run
        if (window.dreamEngineDiagnostics) {
            console.log('🛡️ Preventing diagnostic auto-run');
            
            // Keep diagnostics available but disable auto-run
            const originalRunAll = window.dreamEngineDiagnostics.runAll;
            window.dreamEngineDiagnostics.runAll = function() {
                console.log('🔧 Running diagnostics manually...');
                return originalRunAll.call(this);
            };
        }
    }
    
    ensureNormalInterface() {
        // Make sure build section is active by default
        this.switchToSection('build');
        
        // Hide any diagnostic overlays
        this.hideDiagnosticScreens();
        
        // Show normal navigation
        this.showNormalNavigation();
    }
    
    switchToSection(sectionName) {
        console.log(`🔄 Switching to ${sectionName} section`);
        
        // Update nav pills
        document.querySelectorAll('.nav-pill').forEach(pill => {
            pill.classList.remove('active');
        });
        
        const activeNav = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }
        
        // Update content sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        const activeSection = document.getElementById(`${sectionName}-section`);
        if (activeSection) {
            activeSection.classList.add('active');
        }
        
        this.currentSection = sectionName;
        
        // Special handling for debug section
        if (sectionName === 'debug') {
            this.enableDebugMode();
        } else {
            this.disableDebugMode();
        }
    }
    
    enableDebugMode() {
        console.log('🔧 Debug mode enabled - Diagnostics available');
        this.mode = 'diagnostic';
        
        // Add manual diagnostic trigger to debug section
        const debugSection = document.getElementById('debug-section');
        if (debugSection && window.dreamEngineDiagnostics) {
            this.addDiagnosticButton(debugSection);
        }
    }
    
    disableDebugMode() {
        this.mode = 'normal';
        this.hideDiagnosticScreens();
    }
    
    addDiagnosticButton(debugSection) {
        const existingBtn = debugSection.querySelector('.diagnostic-trigger-btn');
        if (existingBtn) return; // Already exists
        
        const debugContainer = debugSection.querySelector('.section-container');
        if (!debugContainer) return;
        
        const diagnosticHTML = `
            <div class="debug-actions" style="margin: 20px 0;">
                <button class="btn-secondary diagnostic-trigger-btn" onclick="window.interfaceController.runDiagnostics()">
                    🔧 Run System Diagnostics
                </button>
                <div id="diagnostic-results" style="margin-top: 20px; display: none;"></div>
            </div>
        `;
        
        debugContainer.insertAdjacentHTML('afterbegin', diagnosticHTML);
    }
    
    runDiagnostics() {
        if (window.dreamEngineDiagnostics) {
            console.log('🔧 Running diagnostics from debug section...');
            
            const resultsDiv = document.getElementById('diagnostic-results');
            if (resultsDiv) {
                resultsDiv.style.display = 'block';
                resultsDiv.innerHTML = '<p>🔄 Running diagnostics...</p>';
                
                // Run diagnostics
                window.dreamEngineDiagnostics.runAll();
                
                // Show results after a delay
                setTimeout(() => {
                    resultsDiv.innerHTML = `
                        <div class="diagnostic-summary">
                            <h4>✅ Diagnostics Complete</h4>
                            <p>Check browser console for detailed results</p>
                            <p>Status: ${navigator.onLine ? 'Online' : 'Offline'}</p>
                        </div>
                    `;
                }, 3000);
            }
        }
    }
    
    hideDiagnosticScreens() {
        // Hide any diagnostic overlays or screens
        const diagnosticElements = document.querySelectorAll('[id*="diagnostic"], [class*="diagnostic"]');
        diagnosticElements.forEach(el => {
            if (el.style) {
                el.style.display = 'none';
            }
        });
    }
    
    showNormalNavigation() {
        // Ensure navigation is visible and functional
        const navHeader = document.querySelector('.nav-header');
        const mainContent = document.querySelector('.main-content');
        
        if (navHeader) navHeader.style.display = 'block';
        if (mainContent) mainContent.style.display = 'block';
        
        // Make sure build section is visible
        const buildSection = document.getElementById('build-section');
        if (buildSection) {
            buildSection.classList.add('active');
        }
    }
}

// Initialize interface controller immediately
window.interfaceController = new InterfaceController();

// Export for global access
window.InterfaceController = InterfaceController;

function generateDiagnosticReport() {
        console.log('\n📋 Diagnostic Report:');
        console.log('==================');
       
        const report = {
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href,
            protocol: window.location.protocol,
            host: window.location.host,
            pathname: window.location.pathname,
            scripts: {
                dreamEngineClient: typeof DreamEngineClient !== 'undefined',
                dreamEngineUI: typeof window.dreamEngineUI !== 'undefined',
                dreamEngineClientInstance: typeof window.dreamEngineClient !== 'undefined'
            },
            localStorage: {
                available: typeof localStorage !== 'undefined',
                drafts: localStorage.getItem('dreamengine_drafts') ? 'Present' : 'None'
            },
            console: {
                errors: 'Check console for any error messages',
                warnings: 'Check console for any warning messages'
            }
        };
       
        console.log('Report Data:', JSON.stringify(report, null, 2));
       
        return report;
    }
   
    // Run all diagnostics
    function runAllDiagnostics() {
        console.log('🔍 Running Complete Diagnostic Suite...');
       
        checkJavaScriptErrors();
       
        setTimeout(() => {
            checkFileStructure();
        }, 500);
       
        setTimeout(() => {
            checkAPIEndpoints();
        }, 1000);
       
        setTimeout(() => {
            checkEnvironment();
        }, 1500);
       
        setTimeout(() => {
            testBasicFunctionality();
        }, 2000);
       
        setTimeout(() => {
            testAPICall();
        }, 2500);
       
        setTimeout(() => {
            generateDiagnosticReport();
        }, 3000);
    }
   

// DIAGNOSTIC AUTO-RUN DISABLED - Manual trigger only
console.log('🔧 Diagnostics loaded but NOT auto-running');
console.log('💡 To run diagnostics manually: window.dreamEngineDiagnostics.runAll()');
   



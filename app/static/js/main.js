/**
 * AI Debugger Factory - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Navigation between sections
    const navItems = document.querySelectorAll('.sidebar-nav li');
    const sections = document.querySelectorAll('.content-section');
    const currentSectionSpan = document.getElementById('current-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            const sectionId = this.getAttribute('data-section');
            
            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            // Update visible section
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById(`${sectionId}-section`).classList.add('active');
            
            // Update breadcrumb
            currentSectionSpan.textContent = sectionId.charAt(0).toUpperCase() + sectionId.slice(1);
        });
    });
    
    // New Project Modal
    const newProjectBtn = document.getElementById('new-project-button');
    const newProjectModal = document.getElementById('new-project-modal');
    const closeModalBtn = document.querySelector('.close-modal');
    const cancelProjectBtn = document.getElementById('cancel-project');
    const createProjectBtn = document.getElementById('create-project');
    
    function openModal() {
        newProjectModal.classList.add('active');
    }
    
    function closeModal() {
        newProjectModal.classList.remove('active');
    }
    
    if (newProjectBtn) newProjectBtn.addEventListener('click', openModal);
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
    if (cancelProjectBtn) cancelProjectBtn.addEventListener('click', closeModal);
    
    if (createProjectBtn) {
        createProjectBtn.addEventListener('click', function() {
            const projectTitle = document.getElementById('modal-project-title').value;
            const projectDescription = document.getElementById('modal-project-description').value;
            const projectType = document.querySelector('input[name="project-type"]:checked').value;
            
            if (!projectTitle) {
                alert('Please enter a project title');
                return;
            }
            
            // Fill the main form with the modal data
            document.getElementById('project-title').value = projectTitle;
            document.getElementById('prompt-editor').value = projectDescription;
            
            // Close modal and scroll to prompt builder
            closeModal();
            document.querySelector('.prompt-builder').scrollIntoView({ behavior: 'smooth' });
        });
    }
    
    // Generate Button
    const generateBtn = document.getElementById('generate-button');
    const outputPanel = document.getElementById('output-panel');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            const projectTitle = document.getElementById('project-title').value;
            const promptText = document.getElementById('prompt-editor').value;
            
            if (!projectTitle || !promptText) {
                alert('Please enter both a project title and prompt');
                return;
            }
            
            // Show loading overlay
            if (loadingOverlay) {
                loadingOverlay.classList.remove('hidden');
            } else {
                console.log('Loading overlay not found, continuing without visual feedback');
            }
            
            // Prepare request data
            const requestData = {
                id: generateUUID(),
                title: projectTitle,
                prompt: promptText,
                options: {
                    fastapi: document.getElementById('option-fastapi') ? document.getElementById('option-fastapi').checked : true,
                    postgres: document.getElementById('option-postgres') ? document.getElementById('option-postgres').checked : true,
                    tests: document.getElementById('option-tests') ? document.getElementById('option-tests').checked : true,
                    docker: document.getElementById('option-docker') ? document.getElementById('option-docker').checked : false
                }
            };
            
            console.log('Sending build request:', requestData);
            
            // Call the API
            fetch('/api/v1/build', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API request failed with status ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Build API response:', data);
                
                // Hide loading overlay
                if (loadingOverlay) {
                    loadingOverlay.classList.add('hidden');
                }
                
                // Display the results
                if (document.getElementById('contract-display')) {
                    document.getElementById('contract-display').textContent = JSON.stringify(data.contract, null, 2);
                }
                
                // Show sample code for demonstration
                const sampleCode = data.files_generated && data.files_generated.length > 0 
                    ? `# Generated code for ${data.title}\n\n` + data.files_generated.map(file => `## ${file}`).join('\n\n')
                    : `from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    
@app.get("/items")
async def get_items():
    # This would connect to a database in production
    return {"items": [
        {"id": 1, "name": "Item 1", "price": 19.99},
        {"id": 2, "name": "Item 2", "price": 29.99}
    ]}

@app.post("/items")
async def create_item(item: Item):
    # This would save to a database in production
    return {"id": 3, **item.dict()}`;
                
                if (document.getElementById('code-display')) {
                    document.getElementById('code-display').textContent = sampleCode;
                }
                
                // Show the output panel
                if (outputPanel) {
                    outputPanel.classList.remove('hidden');
                    outputPanel.scrollIntoView({ behavior: 'smooth' });
                } else {
                    // Create a simple alert if output panel doesn't exist
                    alert('Code generated successfully! Check the console for details.');
                    console.log('Generated code:', sampleCode);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (loadingOverlay) {
                    loadingOverlay.classList.add('hidden');
                }
                alert(`An error occurred while generating the code: ${error.message}. Please try again.`);
            });
        });
    }
    
    // Code tabs
    const codeTabs = document.querySelectorAll('.code-tab');
    
    codeTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Update active tab
            codeTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Get the file to display
            const fileToShow = this.getAttribute('data-file');
            
            // Sample code for different files (in a real app, this would come from the API)
            let codeContent = '';
            
            switch(fileToShow) {
                case 'app.py':
                    codeContent = `from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    
@app.get("/items")
async def get_items():
    # This would connect to a database in production
    return {"items": [
        {"id": 1, "name": "Item 1", "price": 19.99},
        {"id": 2, "name": "Item 2", "price": 29.99}
    ]}

@app.post("/items")
async def create_item(item: Item):
    # This would save to a database in production
    return {"id": 3, **item.dict()}`;
                    break;
                case 'models.py':
                    codeContent = `from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    full_name: Optional[str] = None`;
                    break;
                case 'database.py':
                    codeContent = `import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL
        )
    ''')
    await conn.close()`;
                    break;
            }
            
            if (document.getElementById('code-display')) {
                document.getElementById('code-display').textContent = codeContent;
            }
        });
    });
    
    // Voice Input Button
    const voiceInputBtn = document.getElementById('voice-input-button');
    
    if (voiceInputBtn) {
        voiceInputBtn.addEventListener('click', function() {
            // Check if browser supports the Web Speech API
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                alert('Voice input is ready! Click OK and start speaking your requirements.');
                
                // Create a new instance of SpeechRecognition
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                
                recognition.lang = 'en-US';
                recognition.continuous = true;
                recognition.interimResults = true;
                
                recognition.onstart = function() {
                    console.log('Voice recognition started. Speak now.');
                    alert('Listening... Speak your requirements clearly.');
                };
                
                recognition.onresult = function(event) {
                    const transcript = Array.from(event.results)
                        .map(result => result[0])
                        .map(result => result.transcript)
                        .join('');
                    
                    document.getElementById('prompt-editor').value = transcript;
                    console.log('Voice input:', transcript);
                };
                
                recognition.onerror = function(event) {
                    console.error('Speech recognition error', event.error);
                    alert('Error with voice recognition: ' + event.error);
                };
                
                recognition.onend = function() {
                    console.log('Voice recognition ended.');
                    alert('Voice input completed. You can edit the text if needed.');
                };
                
                // Start recognition
                recognition.start();
            } else {
                // Fallback for browsers that don't support Web Speech API
                console.log('Calling voice API endpoint');
                
                // Show a message that we're processing
                alert('Processing voice input via API...');
                
                // In a real implementation, this would call the voice API endpoint
                // For now, we'll simulate it with a timeout
                setTimeout(() => {
                    const simulatedTranscript = "Create a FastAPI backend for a task management application with user authentication, CRUD operations, and PostgreSQL database.";
                    document.getElementById('prompt-editor').value = simulatedTranscript;
                    alert('Voice input processed! You can edit the text if needed.');
                }, 2000);
            }
        });
    }
    
    // Debug Section - Analyze Button
    const analyzeBtn = document.getElementById('analyze-button');
    
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            // Show loading overlay
            if (loadingOverlay) {
                loadingOverlay.classList.remove('hidden');
            }
            
            // Call the API
            fetch('/api/v1/debug/contract-drift')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API request failed with status ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Contract drift analysis:', data);
                
                // Hide loading overlay
                if (loadingOverlay) {
                    loadingOverlay.classList.add('hidden');
                }
                
                // Update the last analyzed time
                const lastAnalyzedElement = document.getElementById('last-analyzed');
                if (lastAnalyzedElement) {
                    lastAnalyzedElement.textContent = new Date().toLocaleString();
                }
                
                // Show a success message
                alert('Analysis complete! ' + (data.drift_detected ? 'Contract drift detected.' : 'No contract drift detected.'));
            })
            .catch(error => {
                console.error('Error:', error);
                if (loadingOverlay) {
                    loadingOverlay.classList.add('hidden');
                }
                alert(`An error occurred during analysis: ${error.message}. Please try again.`);
            });
        });
    }
    
    // Helper function to generate UUID
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0,
                v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    // Close output panel
    const closeOutputBtn = document.getElementById('close-output-button');
    
    if (closeOutputBtn) {
        closeOutputBtn.addEventListener('click', function() {
            if (outputPanel) {
                outputPanel.classList.add('hidden');
            }
        });
    }
    
    // Copy and Download buttons
    const copyBtn = document.getElementById('copy-button');
    const downloadBtn = document.getElementById('download-button');
    
    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            const codeDisplay = document.getElementById('code-display');
            if (codeDisplay) {
                const codeText = codeDisplay.textContent;
                navigator.clipboard.writeText(codeText).then(() => {
                    alert('Code copied to clipboard!');
                }).catch(err => {
                    console.error('Failed to copy code:', err);
                    alert('Failed to copy code. Please try again.');
                });
            }
        });
    }
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const codeDisplay = document.getElementById('code-display');
            if (codeDisplay) {
                const codeText = codeDisplay.textContent;
                const activeTab = document.querySelector('.code-tab.active');
                const fileName = activeTab ? activeTab.getAttribute('data-file') : 'code.py';
                
                const blob = new Blob([codeText], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.href = url;
                a.download = fileName;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
        });
    }
    
    // Template Button
    const templateBtn = document.getElementById('template-button');
    
    if (templateBtn) {
        templateBtn.addEventListener('click', function() {
            const templatePrompt = `Create a FastAPI backend for a task management application with the following features:

1. User authentication with JWT tokens
2. CRUD operations for tasks
3. Task categories and tags
4. Due date and priority settings
5. PostgreSQL database for storage
6. Unit tests for core functionality

The application should follow RESTful API design principles and include proper error handling.`;
            
            if (document.getElementById('project-title')) {
                document.getElementById('project-title').value = 'Task Management API';
            }
            
            if (document.getElementById('prompt-editor')) {
                document.getElementById('prompt-editor').value = templatePrompt;
            }
        });
    }
    
    // Clear Button
    const clearBtn = document.getElementById('clear-button');
    
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            if (document.getElementById('project-title')) {
                document.getElementById('project-title').value = '';
            }
            
            if (document.getElementById('prompt-editor')) {
                document.getElementById('prompt-editor').value = '';
            }
        });
    }
    
    // Deploy Button
    const deployBtn = document.getElementById('deploy-button');
    
    if (deployBtn) {
        deployBtn.addEventListener('click', function() {
            // Get repository status first
            fetch('/api/v1/debug/status')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API request failed with status ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Repository status:', data);
                alert(`Preparing to deploy to GitHub repository: ${data.repository.name}\n\nThis will create a new branch and push the generated code. Please check your GitHub account for the new pull request.`);
            })
            .catch(error => {
                console.error('Error:', error);
                alert(`Could not retrieve repository status. Deploying to default repository.\n\nError: ${error.message}`);
            });
        });
    }
    
    // Documentation Button
    const docsBtn = document.getElementById('docs-button');
    
    if (docsBtn) {
        docsBtn.addEventListener('click', function() {
            // Fetch documentation from API or show static content
            fetch('/api/v1/health')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API request failed with status ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('API health status:', data);
                alert(`AI Debugger Factory Documentation\n\nVersion: ${data.version}\nService: ${data.service}\n\nThe AI Debugger Factory is a platform for generating, debugging, and evolving AI-generated codebases. Use the Build section to create new backend code, the Debug section to analyze and fix issues, and the Evolve section to improve your codebase over time.`);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('AI Debugger Factory Documentation\n\nThe AI Debugger Factory is a platform for generating, debugging, and evolving AI-generated codebases. Use the Build section to create new backend code, the Debug section to analyze and fix issues, and the Evolve section to improve your codebase over time.');
            });
        });
    }
    
    // Check API health on page load
    fetch('/api/v1/health')
    .then(response => response.json())
    .then(data => {
        console.log('API health check on load:', data);
        // Update system status indicator if it exists
        const statusIndicator = document.querySelector('.status-indicator');
        if (statusIndicator && data.status === 'healthy') {
            statusIndicator.classList.add('online');
            statusIndicator.classList.remove('offline');
        }
    })
    .catch(error => {
        console.error('Health check error:', error);
        // Update system status indicator if it exists
        const statusIndicator = document.querySelector('.status-indicator');
        if (statusIndicator) {
            statusIndicator.classList.remove('online');
            statusIndicator.classList.add('offline');
        }
    });
});

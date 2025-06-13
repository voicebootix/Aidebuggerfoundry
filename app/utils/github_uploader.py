mport os
import requests
import base64
import logging

logger = logging.getLogger(__name__)

def upload_to_github(repo_name, github_token, files_content, commit_message="Initial Commit", branch="main"):
    """
    GitHub repository-க்கு files upload செய்யவும்
    
    Args:
        repo_name: GitHub repository name (e.g., "username/repo")
        github_token: GitHub personal access token
        files_content: {file_path: content} Dict அல்லது {filename, content} List
        commit_message: Commit message
        branch: Target branch
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # files_content list ஆக இருந்தால் dict format-க்கு convert செய்யவும்
    if isinstance(files_content, list):
        files_dict = {}
        for file_obj in files_content:
            if isinstance(file_obj, dict) and 'filename' in file_obj and 'content' in file_obj:
                files_dict[file_obj['filename']] = file_obj['content']
            elif hasattr(file_obj, 'filename') and hasattr(file_obj, 'content'):
                files_dict[file_obj.filename] = file_obj.content
        files_content = files_dict

    uploaded_files = []
    failed_files = []

    for file_path, content in files_content.items():
        try:
            # Content string ஆக இருந்தால் bytes-க்கு convert செய்யவும்
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            # Content-ஐ base64-ஆக encode செய்யவும்
            content_b64 = base64.b64encode(content_bytes).decode('utf-8')

            github_api_url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
            
            response = requests.put(
                github_api_url,
                headers=headers,
                json={
                    "message": commit_message,
                    "branch": branch,
                    "content": content_b64,
                },
            )

            if response.status_code in [200, 201]:
                uploaded_files.append(file_path)
                logger.info(f"வெற்றிகரமாக upload செய்யப்பட்டது {file_path}")
            else:
                failed_files.append({"file": file_path, "error": response.text})
                logger.error(f"{file_path} upload செய்வதில் தோல்வி: {response.text}")

        except Exception as e:
            failed_files.append({"file": file_path, "error": str(e)})
            logger.error(f"{file_path} upload செய்வதில் exception: {str(e)}")

    if failed_files:
        raise Exception(f"Files upload செய்வதில் தோல்வி: {failed_files}")
    
    return {
        "uploaded_files": uploaded_files,
        "total_files": len(uploaded_files)
    }


### *சரிசெய்தல் 2: Backend Endpoint புதுப்பிக்கவும்*

*main.py-ல் /upload-to-github endpoint-ஐ மாற்றுங்கள்:*

python
@app.post("/upload-to-github")
async def upload_to_github_api(
    request: Request,
    repo: str = Form(...),
    token: str = Form(...),
    commit_message: str = Form("Initial Commit"),
    project_id: str = Form(...)  # Generated files பெற project ID சேர்க்கவும்
):
    try:
        # இந்த project-க்கான மிக சமீபத்திய generated code பெறுங்கள்
        # இது simplified version - உங்கள் storage படி adjust செய்ய வேண்டும்
        
        # இப்போதைக்கு sample generated files பெறுவோம்
        # உண்மையான implementation-ல், database அல்லது session-ல் இருந்து retrieve செய்வீர்கள்
        sample_files = {
            "app/main.py": """from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Generated API")

class Item(BaseModel):
    id: int
    name: str
    description: str = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
""",
            "requirements.txt": """fastapi
uvicorn
pydantic
""",
            "README.md": f"""# Generated API

இந்த project AI Debugger Factory மூலம் generate செய்யப்பட்டது.

## Installation

bash
pip install -r requirements.txt


## Run

bash
uvicorn app.main:app --reload


“””
}


    # உண்மையான implementation-ல், நீங்கள் செய்வீர்கள்:
    # 1. project_id பயன்படுத்தி database-ல் generated files query செய்வீர்கள்
    # 2. அல்லது session/cache-ல் இருந்து files பெறுவீர்கள்
    # 3. GeneratedFile objects-ஐ dict format-க்கு convert செய்வீர்கள்
    
    result = upload_to_github(repo, token, sample_files, commit_message)
    return {
        "status": "success", 
        "message": f"{result['total_files']} file(s) {repo}-க்கு upload செய்யப்பட்டது",
        "files": result['uploaded_files']
    }
except Exception as e:
    logger.error(f"GitHub upload பிழை: {str(e)}")
    return {"status": "error", "message": str(e)}


```
### **சரிசெய்தல் 3: Frontend Integration மேம்படுத்தவும்**

**`main.js`-ல் deploy button handler-ஐ மாற்றுங்கள்:**

javascript
// Deploy Button (மேம்படுத்தப்பட்ட version)
const deployBtn = document.getElementById('deploy-button');

if (deployBtn) {
    deployBtn.addEventListener('click', function () {
        // Generated code உள்ளதா சரிபார்க்கவும்
        const codeDisplay = document.getElementById('code-display');
        const contractDisplay = document.getElementById('contract-display');
        
        if (!codeDisplay || !codeDisplay.textContent.trim()) {
            alert("⚠️ Generated code கண்டுபிடிக்கப்படவில்லை. முதலில் 'Generate Backend' button பயன்படுத்தி code generate செய்யுங்கள்.");
            return;
        }

        // Prompts-க்கு பதிலாக modal அல்லது சிறந்த form காட்டுங்கள்
        const modal = createGitHubUploadModal();
        document.body.appendChild(modal);
    });
}

function createGitHubUploadModal() {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>GitHub-க்கு Upload செய்யவும்</h3>
                <button class="close-modal" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="input-group">
                    <label for="github-repo">Repository (username/repo-name)</label>
                    <input type="text" id="github-repo" class="form-control" 
                           placeholder="உதாரணம்: john/my-api-project" required>
                    <small>இந்த repository உள்ளது மற்றும் empty ஆக இருப்பதை உறுதிப்படுத்துங்கள்</small>
                </div>
                <div class="input-group">
                    <label for="github-token">Personal Access Token</label>
                    <input type="password" id="github-token" class="form-control" 
                           placeholder="ghp_xxxxxxxxxxxx" required>
                    <small>
                        <a href="https://github.com/settings/tokens" target="_blank">
                            இங்கே token உருவாக்குங்கள்
                        </a> 'repo' permissions கொண்டு
                    </small>
                </div>
                <div class="input-group">
                    <label for="commit-message">Commit Message</label>
                    <input type="text" id="commit-message" class="form-control" 
                           value="AI Debugger Factory-யில் இருந்து Initial commit">
                </div>
                <div class="files-preview">
                    <h4>Upload செய்யப்படும் Files:</h4>
                    <ul id="files-list">
                        <li>app/main.py</li>
                        <li>requirements.txt</li>
                        <li>README.md</li>
                    </ul>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">
                    Cancel
                </button>
                <button class="btn btn-primary" onclick="performGitHubUpload()">
                    <i class="fas fa-upload"></i> GitHub-க்கு Upload செய்யவும்
                </button>
            </div>
        </div>
    `;
    return modal;
}

function performGitHubUpload() {
    const repo = document.getElementById('github-repo').value.trim();
    const token = document.getElementById('github-token').value.trim();
    const commitMessage = document.getElementById('commit-message').value.trim();

    // Validation
    if (!repo || !token) {
        alert("⚠️ தயவுசெய்து அனைத்து required fields-ஐயும் நிரப்புங்கள்.");
        return;
    }

    if (!repo.includes('/')) {
        alert("⚠️ Repository name 'username/repo-name' format-ல் இருக்க வேண்டும்");
        return;
    }

    // Loading காட்டுங்கள்
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.remove('hidden');
    }

    // தற்போதைய project ID பெறுங்கள் (code generate செய்யும்போது store செய்ய வேண்டும்)
    const projectId = document.getElementById('project-title').value || 'default-project';

    const formData = new FormData();
    formData.append("repo", repo);
    formData.append("token", token);
    formData.append("commit_message", commitMessage);
    formData.append("project_id", projectId);

    fetch("/upload-to-github", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (loadingOverlay) {
            loadingOverlay.classList.add("hidden");
        }

        if (data.status === "success") {
            alert(✅ வெற்றி! ${data.files.length} files ${repo}-க்கு upload செய்யப்பட்டது\n\nUpload செய்யப்பட்ட Files:\n${data.files.join('\n')});
            document.querySelector('.modal').remove();
        } else {
            alert("❌ Upload தோல்வி: " + data.message);
        }
    })
    .catch(error => {
        if (loadingOverlay) {
            loadingOverlay.classList.add("hidden");
        }
        console.error("Upload பிழை:", error);
        alert("❌ Upload பிழை: " + error.message);
    });
}


### **சரிசெய்தல் 4: Modal-க்கு CSS சேர்க்கவும்**

**உங்கள் `styles.css`-ல் இதை சேர்க்கவும்:**

css
.files-preview {
    background-color: var(--bg-dark);
    border-radius: var(--radius-md);
    padding: var(--space-md);
    margin-top: var(--space-md);
}

.files-preview h4 {
    margin-bottom: var(--space-sm);
    font-size: var(--font-size-md);
}

.files-preview ul {
    list-style: none;
    padding: 0;
}

.files-preview li {
    padding: var(--space-xs);
    border-bottom: 1px solid var(--border-color);
    font-family: monospace;
    font-size: var(--font-size-sm);
}

.files-preview li:last-child {
    border-bottom: none;
}

.input-group small {
    color: var(--text-muted);
    font-size: var(--font-size-xs);
    margin-top: var(--space-xs);
}

.input-group small a {
    color: var(--primary);
}


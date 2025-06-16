import asyncio
import base64
import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import aiohttp
import aiofiles
from fastapi import HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class GitHubDeployRequest(BaseModel):
    repo_name: str
    description: str
    files: List[Dict[str, str]]  # [{"filename": "main.py", "content": "code"}]
    github_token: str
    user_id: str = "anonymous"
    auto_deploy: bool = True
    deploy_platform: str = "render"  # render, railway, vercel

class GitHubDeployResponse(BaseModel):
    status: str
    repo_url: str
    deploy_url: Optional[str] = None
    setup_instructions: List[str]
    deployment_time_seconds: float

class GitHubAutoDeployer:
    """Production-ready GitHub integration with auto-deployment"""
    
    def __init__(self):
        self.github_api_base = "https://api.github.com"
        self.supported_platforms = {
            "render": self._setup_render_deployment,
            "railway": self._setup_railway_deployment,
            "vercel": self._setup_vercel_deployment
        }
        
    async def create_and_deploy(self, request: GitHubDeployRequest) -> GitHubDeployResponse:
        """Main method: Create repo, push code, setup deployment"""
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Starting GitHub auto-deploy for {request.repo_name}")
            
            # Step 1: Create GitHub repository
            repo_data = await self._create_github_repo(request)
            repo_url = repo_data["html_url"]
            
            # Step 2: Push code files
            await self._push_files_to_repo(request, repo_data)
            
            # Step 3: Setup deployment (if requested)
            deploy_url = None
            setup_instructions = []
            
            if request.auto_deploy and request.deploy_platform in self.supported_platforms:
                deploy_result = await self.supported_platforms[request.deploy_platform](
                    request, repo_data
                )
                deploy_url = deploy_result.get("url")
                setup_instructions = deploy_result.get("instructions", [])
            else:
                setup_instructions = self._get_manual_deployment_instructions(request.deploy_platform)
            
            deployment_time = time.time() - start_time
            
            logger.info(f"✅ GitHub deployment completed in {deployment_time:.2f}s")
            
            return GitHubDeployResponse(
                status="success",
                repo_url=repo_url,
                deploy_url=deploy_url,
                setup_instructions=setup_instructions,
                deployment_time_seconds=round(deployment_time, 2)
            )
            
        except Exception as e:
            logger.error(f"❌ GitHub deployment failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")
    
    async def _create_github_repo(self, request: GitHubDeployRequest) -> Dict:
        """Create a new GitHub repository"""
        try:
            headers = {
                "Authorization": f"token {request.github_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "DreamEngine-Deploy/1.0"
            }
            
            repo_data = {
                "name": request.repo_name,
                "description": request.description,
                "private": False,  # Can be made configurable
                "auto_init": True,
                "gitignore_template": "Python"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.github_api_base}/user/repos",
                    headers=headers,
                    json=repo_data
                ) as response:
                    
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"✅ GitHub repo created: {result['html_url']}")
                        return result
                    elif response.status == 422:
                        # Repository already exists
                        error_data = await response.json()
                        if "already exists" in str(error_data):
                            # Try to get existing repo
                            return await self._get_existing_repo(request.repo_name, headers)
                        else:
                            raise Exception(f"Repository creation failed: {error_data}")
                    else:
                        error_text = await response.text()
                        raise Exception(f"GitHub API error {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"❌ Failed to create GitHub repo: {str(e)}")
            raise
    
    async def _get_existing_repo(self, repo_name: str, headers: Dict) -> Dict:
        """Get existing repository data"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.github_api_base}/user",
                headers=headers
            ) as user_response:
                user_data = await user_response.json()
                username = user_data["login"]
                
            async with session.get(
                f"{self.github_api_base}/repos/{username}/{repo_name}",
                headers=headers
            ) as repo_response:
                if repo_response.status == 200:
                    return await repo_response.json()
                else:
                    raise Exception(f"Repository {repo_name} not accessible")
    
    async def _push_files_to_repo(self, request: GitHubDeployRequest, repo_data: Dict):
        """Push all generated files to the repository"""
        try:
            headers = {
                "Authorization": f"token {request.github_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "DreamEngine-Deploy/1.0"
            }
            
            repo_full_name = repo_data["full_name"]
            
            # Add deployment-specific files
            enhanced_files = request.files.copy()
            enhanced_files.extend(self._generate_deployment_files(request))
            
            async with aiohttp.ClientSession() as session:
                for file_data in enhanced_files:
                    await self._push_single_file(
                        session, headers, repo_full_name, 
                        file_data["filename"], file_data["content"]
                    )
                    
            logger.info(f"✅ Pushed {len(enhanced_files)} files to repository")
            
        except Exception as e:
            logger.error(f"❌ Failed to push files: {str(e)}")
            raise
    
    async def _push_single_file(
        self, session: aiohttp.ClientSession, headers: Dict, 
        repo_full_name: str, filename: str, content: str
    ):
        """Push a single file to repository"""
        try:
            # Encode content to base64
            content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            file_data = {
                "message": f"Add {filename} via DreamEngine",
                "content": content_encoded,
                "branch": "main"
            }
            
            # Check if file exists (for updates)
            try:
                async with session.get(
                    f"{self.github_api_base}/repos/{repo_full_name}/contents/{filename}",
                    headers=headers
                ) as check_response:
                    if check_response.status == 200:
                        existing_data = await check_response.json()
                        file_data["sha"] = existing_data["sha"]
                        file_data["message"] = f"Update {filename} via DreamEngine"
            except:
                pass  # File doesn't exist, which is fine for creation
            
            async with session.put(
                f"{self.github_api_base}/repos/{repo_full_name}/contents/{filename}",
                headers=headers,
                json=file_data
            ) as response:
                
                if response.status in [200, 201]:
                    logger.info(f"✅ Pushed {filename}")
                else:
                    error_text = await response.text()
                    logger.warning(f"⚠️ Failed to push {filename}: {error_text}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Error pushing {filename}: {str(e)}")
    
    def _generate_deployment_files(self, request: GitHubDeployRequest) -> List[Dict[str, str]]:
        """Generate deployment-specific configuration files"""
        deployment_files = []
        
        # Generate requirements.txt if not present
        if not any(f["filename"] == "requirements.txt" for f in request.files):
            requirements_content = self._generate_requirements_txt(request.files)
            deployment_files.append({
                "filename": "requirements.txt",
                "content": requirements_content
            })
        
        # Generate README.md with setup instructions
        readme_content = self._generate_readme(request)
        deployment_files.append({
            "filename": "README.md", 
            "content": readme_content
        })
        
        # Generate platform-specific config files
        if request.deploy_platform == "render":
            deployment_files.append({
                "filename": "render.yaml",
                "content": self._generate_render_config(request)
            })
        elif request.deploy_platform == "railway":
            deployment_files.append({
                "filename": "railway.json",
                "content": self._generate_railway_config(request)
            })
        elif request.deploy_platform == "vercel":
            deployment_files.append({
                "filename": "vercel.json",
                "content": self._generate_vercel_config(request)
            })
        
        return deployment_files
    
    def _generate_requirements_txt(self, files: List[Dict]) -> str:
        """Auto-generate requirements.txt based on code analysis"""
        common_imports = {
            "fastapi": "fastapi>=0.104.0",
            "uvicorn": "uvicorn>=0.24.0",
            "pydantic": "pydantic>=2.0.0", 
            "sqlalchemy": "sqlalchemy>=2.0.0",
            "psycopg2": "psycopg2-binary>=2.9.0",
            "requests": "requests>=2.31.0",
            "aiohttp": "aiohttp>=3.9.0",
            "python-multipart": "python-multipart>=0.0.6",
            "python-jose": "python-jose[cryptography]>=3.3.0",
            "passlib": "passlib[bcrypt]>=1.7.4",
            "asyncpg": "asyncpg>=0.29.0"
        }
        
        requirements = set()
        
        # Analyze code content for imports
        for file_data in files:
            content = file_data["content"].lower()
            for package, requirement in common_imports.items():
                if package in content or f"import {package}" in content or f"from {package}" in content:
                    requirements.add(requirement)
        
        # Always include FastAPI basics for web apps
        if not requirements:
            requirements.update([
                "fastapi>=0.104.0",
                "uvicorn>=0.24.0",
                "pydantic>=2.0.0"
            ])
        
        return "\n".join(sorted(requirements))
    
    def _generate_readme(self, request: GitHubDeployRequest) -> str:
        """Generate comprehensive README.md"""
        return f"""# {request.repo_name}

{request.description}

*Generated by DreamEngine - AI Debugger Factory*

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/{request.repo_name}.git
cd {request.repo_name}

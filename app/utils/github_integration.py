"""
GitHub Integration - Complete API Integration
Seamless Layer 1 → GitHub → Layer 2 workflow
Enhanced with real-time collaboration and deployment pipeline
"""

import asyncio
import json
import base64
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from github import Github
import tempfile
import zipfile

@dataclass
class GitHubRepository:
    repo_name: str
    repo_url: str
    clone_url: str
    default_branch: str
    private: bool

@dataclass
class GitHubDeployment:
    deployment_id: str
    repo_url: str
    environment: str
    status: str
    deployment_url: Optional[str]
    created_at: datetime

class GitHubIntegration:
    """Complete GitHub API integration system"""
    
    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self.user = self.github.get_user()
        
    async def create_repository(self, 
                              repo_name: str,
                              description: str = "",
                              private: bool = True) -> GitHubRepository:
        """Create new GitHub repository"""
        
        try:
            repo = self.user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=True,
                gitignore_template="Python"
            )
            
            return GitHubRepository(
                repo_name=repo.name,
                repo_url=repo.html_url,
                clone_url=repo.clone_url,
                default_branch=repo.default_branch,
                private=repo.private
            )
            
        except Exception as e:
            raise Exception(f"Failed to create repository: {str(e)}")
    
    async def upload_generated_code(self, 
                                  repo_name: str,
                                  generated_files: List[Dict],
                                  commit_message: str = "Initial AI-generated code") -> Dict:
        """Upload generated code files to GitHub repository"""
        
        try:
            repo = self.github.get_user().get_repo(repo_name)
            upload_results = []
            
            for file_data in generated_files:
                file_path = file_data["filename"]
                file_content = file_data["content"]
                
                # Create or update file
                try:
                    # Try to get existing file
                    existing_file = repo.get_contents(file_path)
                    
                    # Update existing file
                    repo.update_file(
                        path=file_path,
                        message=f"Update {file_path}",
                        content=file_content,
                        sha=existing_file.sha
                    )
                    upload_results.append({"file": file_path, "status": "updated"})
                    
                except:
                    # Create new file
                    repo.create_file(
                        path=file_path,
                        message=f"Add {file_path}",
                        content=file_content
                    )
                    upload_results.append({"file": file_path, "status": "created"})
            
            return {
                "success": True,
                "repository_url": repo.html_url,
                "files_uploaded": len(upload_results),
                "upload_results": upload_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "files_uploaded": 0
            }
    
    async def sync_project_changes(self, 
                                 repo_name: str,
                                 changed_files: Dict[str, str]) -> Dict:
        """Sync project changes to GitHub"""
        
        try:
            repo = self.github.get_user().get_repo(repo_name)
            sync_results = []
            
            for file_path, new_content in changed_files.items():
                try:
                    # Get current file
                    current_file = repo.get_contents(file_path)
                    
                    # Update file
                    repo.update_file(
                        path=file_path,
                        message=f"AI Debug: Update {file_path}",
                        content=new_content,
                        sha=current_file.sha
                    )
                    sync_results.append({"file": file_path, "status": "synced"})
                    
                except Exception as e:
                    sync_results.append({"file": file_path, "status": "error", "error": str(e)})
            
            return {
                "success": True,
                "synced_files": len([r for r in sync_results if r["status"] == "synced"]),
                "sync_results": sync_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
# Create the global instance that main.py expects
github_manager = GitHubIntegration(github_token=os.getenv("GITHUB_TOKEN", ""))


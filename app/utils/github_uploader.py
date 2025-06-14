import os
import requests
import base64
import logging

logger = logging.getLogger(__name__)

def upload_to_github(repo_name, github_token, files_content, commit_message="Initial Commit", branch="main"):
    """
    Upload files to GitHub repository
    
    Args:
        repo_name: GitHub repository name (e.g., "username/repo")
        github_token: GitHub personal access token
        files_content: {file_path: content} Dict or {filename, content} List
        commit_message: Commit message
        branch: Target branch
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Convert files_content list to dict format if needed
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
            # Convert content to bytes if it's a string
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            # Encode content as base64
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
                logger.info(f"Successfully uploaded {file_path}")
            else:
                failed_files.append({"file": file_path, "error": response.text})
                logger.error(f"Failed to upload {file_path}: {response.text}")

        except Exception as e:
            failed_files.append({"file": file_path, "error": str(e)})
            logger.error(f"Exception uploading {file_path}: {str(e)}")

    if failed_files:
        raise Exception(f"Failed to upload files: {failed_files}")
    
    return {
        "uploaded_files": uploaded_files,
        "total_files": len(uploaded_files)
    }

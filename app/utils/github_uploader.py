import os
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

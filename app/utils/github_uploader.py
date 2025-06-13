import os
import requests

def upload_to_github(repo_name, github_token, file_paths, commit_message="Initial Commit", branch="main"):
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    for file_path in file_paths:
        with open(file_path, "rb") as f:
            content = f.read()
        content_b64 = content.encode("base64") if hasattr(content, "encode") else content

        github_api_url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
        response = requests.put(github_api_url, headers=headers, json={
            "message": commit_message,
            "branch": branch,
            "content": content_b64.decode("utf-8")
        })

        if response.status_code not in [200, 201]:
            raise Exception(f"GitHub upload failed for {file_path}: {response.text}")

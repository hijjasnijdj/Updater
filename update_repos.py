import os
import tempfile
import subprocess
import requests

# Set up your GitHub access token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_repositories():
    """Get all repositories for the authenticated user."""
    repos_url = "https://api.github.com/user/repos"
    repos = []
    page = 1
    while True:
        response = requests.get(repos_url, headers=HEADERS, params={"page": page, "per_page": 100})
        if response.status_code != 200:
            print(f"Failed to fetch repositories: {response.status_code} {response.text}")
            break
        repo_data = response.json()
        if not repo_data:
            break
        repos.extend(repo['clone_url'] for repo in repo_data)
        page += 1
    return repos

def update_repository(repo_url):
    """Clone the repo, create an empty commit, and push it to GitHub."""
    # Insert the token into the repo URL for authentication
    repo_url_with_token = repo_url.replace("https://", f"https://{GITHUB_TOKEN}@")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone the repository
            subprocess.run(["git", "clone", repo_url_with_token, temp_dir], check=True)
            
            # Create an empty commit
            subprocess.run(["git", "-C", temp_dir, "commit", "--allow-empty", "-m", "Trigger update"], check=True)
            
            # Push the commit
            subprocess.run(["git", "-C", temp_dir, "push"], check=True)
            print(f"Updated repository: {repo_url}")
        
        except subprocess.CalledProcessError as e:
            print(f"Failed to update {repo_url}: {e}")

def main():
    repos = get_repositories()
    if not repos:
        print("No repositories found or failed to fetch repositories.")
        return

    for repo_url in repos:
        update_repository(repo_url)

if __name__ == "__main__":
    main()

import os
import stat
import shutil
from git import Repo

def handle_remove_readonly(func, path, exc_info):
    """
    Error handler for shutil.rmtree on Windows.
    Handles read-only files by changing permissions and retrying.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repo(github_url: str, base_dir: str = "repos") -> str:
    """
    Clones a public GitHub repo into a local directory.
    Returns the path to the cloned repo.
    """
    os.makedirs(base_dir, exist_ok=True)

    # Extract repo name from URL
    repo_name = github_url.rstrip("/").split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    repo_path = os.path.join(base_dir, repo_name)

    # If already cloned, delete and re-clone fresh
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=handle_remove_readonly)

    print(f"Cloning {github_url} into {repo_path}...")
    Repo.clone_from(github_url, repo_path)
    print(f"Clone complete: {repo_path}")

    return repo_path
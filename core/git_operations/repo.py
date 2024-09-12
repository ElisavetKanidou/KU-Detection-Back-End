import git
import os
from config.settings import CLONED_REPO_BASE_PATH
from datetime import datetime

def repo_exists(repo_name: str) -> bool:
    """Checks if a repository with the given name exists in the current working directory.

    :param repo_name: The name of the repository.
    :return: True if the repository exists, False otherwise."""
    return os.path.exists(os.path.join(CLONED_REPO_BASE_PATH, "fake_session_id", repo_name))


def clone_repo(url: str, path: str) -> dict:
    """Clones a repository from the given URL to the specified destination path.

    :param url: The URL of the repository to clone.
    :param path: The path to clone the repository to.
    """
    os.makedirs(path, exist_ok=True)

    try:
        git.Repo.clone_from(url, path)
        return {"status": "success", "message": "Repository cloned successfully."}
    except git.GitCommandError:
        return {"status": "error", "message": "Repository could not be cloned."}


def get_repo(path: str) -> git.Repo:
    """Gets a reference to the local repository at the specified path.

    :param path: The path to the local repository.
    :return: A reference to the local repository."""
    return git.Repo(path)


def get_local_branch_names(repo: git.Repo) -> list:
    """Gets a list of the names of all local branches in the given repository.

    :param repo: The repository to get the branch names from.
    :return: A list of the names of all local branches in the given repository."""
    # noinspection PyTypeChecker
    return [branch.name for branch in repo.branches]


def get_all_branch_names(repo: git.Repo) -> list:
    """Gets a list of the names of all branches in the given repository. Including remote branches.

    :param repo: The repository to get the branch names from.
    :return: A list of the names of all branches (local and remote) in the given repository."""
    # noinspection PyTypeChecker
    return [branch.name for branch in repo.remote().refs]


def pull_repo(repo_path: str) -> dict:
    """Forcefully pulls the latest changes from the remote repository for the local repository at the specified path.

    :param repo_path: The path to the local repository.
    :return: A dictionary with the status of the pull operation."""
    repo = get_repo(repo_path)
    try:
        origin = repo.remotes.origin

        # Fetch latest changes from remote
        origin.fetch()

        # Get the default branch (like 'main' or 'master')
        default_branch = origin.refs['HEAD'].reference.remote_head

        # Forcefully reset the local branch to match the remote default branch
        repo.git.reset('--hard', f'origin/{default_branch}')

        # Clean untracked files
        repo.git.clean('-fd')

        return {"status": "success", "message": f"Repository forcefully updated to match 'origin/{default_branch}'."}

    except git.GitCommandError as e:
        return {"status": "error", "message": f"Error forcefully updating repository: {e}"}

def get_history_repo(repo_url: str, repo_name: str, base_path: str) -> list:
    """Retrieves the commit history (timestamps) from the repository.
    Clones the repository if it doesn't exist, or pulls the latest changes if it does.

    :param repo_url: The URL of the repository.
    :param repo_name: The name of the repository.
    :param base_path: The base path where repositories are stored.
    :return: A list of commit timestamps (datetime objects).
    """
    repo_path = os.path.join(base_path, "fake_session_id", repo_name)

    # Ελέγξτε αν το repository υπάρχει
    if not repo_exists(repo_name):
        # Αν το repository δεν υπάρχει, κάντε clone
        clone_result = clone_repo(repo_url, repo_path)
        if clone_result["status"] == "error":
            raise Exception(clone_result["message"])
    else:
        # Αν υπάρχει, κάντε pull τις τελευταίες αλλαγές
        pull_result = pull_repo(repo_path)
        if pull_result["status"] == "error":
            raise Exception(pull_result["message"])

    # Τώρα, μπορούμε να ανοίξουμε το τοπικό repository και να πάρουμε τα commits
    repo = git.Repo(repo_path)
    commits = list(repo.iter_commits())

    # Εξαγωγή των timestamps από τα commits
    timestamps = [datetime.fromtimestamp(commit.committed_date) for commit in commits]
    return timestamps


import git
import os
from config.settings import CLONED_REPO_BASE_PATH


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

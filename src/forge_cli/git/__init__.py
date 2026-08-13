"""Git repository boundary for Forge CLI."""

from pathlib import Path
import subprocess


class GitUnavailableError(RuntimeError):
    """Raised when the Git executable is unavailable."""


class NotGitRepositoryError(RuntimeError):
    """Raised when a path is not contained in a Git repository."""


def resolve_project_root(start: Path) -> Path:
    """Resolve the top-level Git repository containing ``start``."""
    try:
        result = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise GitUnavailableError("Git executable is unavailable.") from error

    if result.returncode != 0:
        raise NotGitRepositoryError(str(start))

    return Path(result.stdout.strip()).resolve()

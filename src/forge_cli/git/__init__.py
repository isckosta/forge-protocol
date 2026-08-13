"""Git repository boundary for Forge CLI."""

from pathlib import Path
import subprocess


class NotGitRepositoryError(RuntimeError):
    """Raised when a path is not contained in a Git repository."""


def resolve_project_root(start: Path) -> Path:
    """Resolve the top-level Git repository containing ``start``."""
    result = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise NotGitRepositoryError(str(start))

    return Path(result.stdout.strip()).resolve()

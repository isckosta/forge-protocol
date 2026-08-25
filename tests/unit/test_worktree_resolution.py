"""CHG-0045 US-006/TDD-016: Adapter/doctor root resolution must resolve
the Git worktree actually being operated on, not silently assume the
primary checkout. Uses a real `git worktree add`, not a mock, because the
claim under test is about real `git rev-parse --show-toplevel` behavior."""

from pathlib import Path
import subprocess

from forge_cli.git import resolve_project_root


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def test_resolve_project_root_resolves_the_secondary_worktrees_own_root(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    primary.mkdir()
    _run(["git", "init"], cwd=primary)
    _run(["git", "config", "user.email", "test@example.com"], cwd=primary)
    _run(["git", "config", "user.name", "Test"], cwd=primary)
    (primary / "README.md").write_text("primary\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=primary)
    _run(["git", "commit", "-m", "initial"], cwd=primary)
    _run(["git", "branch", "secondary"], cwd=primary)

    secondary = tmp_path / "secondary-worktree"
    _run(["git", "worktree", "add", str(secondary), "secondary"], cwd=primary)

    assert resolve_project_root(primary) == primary.resolve()
    assert resolve_project_root(secondary) == secondary.resolve()
    assert resolve_project_root(secondary) != resolve_project_root(primary)


def test_resolve_project_root_from_a_nested_path_inside_the_secondary_worktree(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    primary.mkdir()
    _run(["git", "init"], cwd=primary)
    _run(["git", "config", "user.email", "test@example.com"], cwd=primary)
    _run(["git", "config", "user.name", "Test"], cwd=primary)
    (primary / "README.md").write_text("primary\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=primary)
    _run(["git", "commit", "-m", "initial"], cwd=primary)
    _run(["git", "branch", "secondary"], cwd=primary)

    secondary = tmp_path / "secondary-worktree"
    _run(["git", "worktree", "add", str(secondary), "secondary"], cwd=primary)
    nested = secondary / ".forge" / "changes"
    nested.mkdir(parents=True)

    assert resolve_project_root(nested) == secondary.resolve()

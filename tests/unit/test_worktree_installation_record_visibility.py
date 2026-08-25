"""CHG-0045 DEC-004/TDD-017: once `.forge/adapters/*/installation.yml` is
committed (DEC-004), a fresh Git worktree checked out from that commit
must see the same recorded digests as the primary checkout, without a
separate `forge adapter install` run in that worktree first."""

from pathlib import Path
import subprocess


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def test_committed_installation_record_is_identical_in_a_fresh_worktree(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    primary.mkdir()
    _run(["git", "init"], cwd=primary)
    _run(["git", "config", "user.email", "test@example.com"], cwd=primary)
    _run(["git", "config", "user.name", "Test"], cwd=primary)

    record_dir = primary / ".forge" / "adapters" / "claude-code"
    record_dir.mkdir(parents=True)
    record_path = record_dir / "installation.yml"
    record_path.write_text(
        "schema: forge/adapter-installation@2\n"
        "adapter: {id: claude-code, version: 0.1.0, harness: claude-code}\n"
        "generated_artifacts:\n"
        "- {path: .claude/skills/forge/SKILL.md, digest: deadbeef}\n",
        encoding="utf-8",
    )
    _run(["git", "add", "."], cwd=primary)
    _run(["git", "commit", "-m", "commit installation record"], cwd=primary)
    _run(["git", "branch", "secondary"], cwd=primary)

    secondary = tmp_path / "secondary-worktree"
    _run(["git", "worktree", "add", str(secondary), "secondary"], cwd=primary)

    secondary_record = secondary / ".forge" / "adapters" / "claude-code" / "installation.yml"
    assert secondary_record.is_file(), (
        "a committed installation.yml must exist in a freshly created worktree "
        "without any separate `forge adapter install` run there"
    )
    assert secondary_record.read_text(encoding="utf-8") == record_path.read_text(encoding="utf-8")

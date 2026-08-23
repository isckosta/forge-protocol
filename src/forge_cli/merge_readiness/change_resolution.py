from __future__ import annotations

import subprocess
from pathlib import Path

from .policy import classify_path, load_materiality_policy


class MergeReadinessOperationalError(RuntimeError):
    pass


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise MergeReadinessOperationalError(result.stderr.strip() or "Git operation failed")
    return result.stdout


def validate_revision(root: Path, revision: str) -> None:
    shallow = _git(root, "rev-parse", "--is-shallow-repository").strip()
    if shallow == "true":
        raise MergeReadinessOperationalError("Complete Git history is required; repository is shallow")
    _git(root, "cat-file", "-e", f"{revision}^{{commit}}")


def changed_paths(root: Path, base: str, head: str) -> tuple[str, ...]:
    validate_revision(root, base)
    validate_revision(root, head)
    raw = _git(root, "diff", "--name-status", "-z", "--find-renames", base, head, "--")
    parts = [part for part in raw.split("\0") if part]
    paths: set[str] = set()
    index = 0
    while index < len(parts):
        status = parts[index]
        index += 1
        count = 2 if status.startswith(("R", "C")) else 1
        if index + count > len(parts):
            raise MergeReadinessOperationalError("Malformed Git name-status output")
        paths.update(parts[index : index + count])
        index += count
    return tuple(sorted(paths))


def is_material(path: str) -> bool:
    return classify_path(path, load_materiality_policy()) == "material"


def affected_changes(root: Path, paths: tuple[str, ...]) -> tuple[str, ...]:
    result: set[str] = set()
    for path in paths:
        parts = Path(path).parts
        if len(parts) < 3 or parts[0] != ".forge" or parts[1] != "changes":
            continue
        directory = root / ".forge" / "changes" / parts[2]
        manifest = directory / "manifest.yml"
        if not directory.is_dir() or directory.is_symlink() or manifest.is_symlink():
            raise MergeReadinessOperationalError(f"Malformed Change directory: {parts[2]}")
        try:
            import yaml

            data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        except (OSError, UnicodeError, yaml.YAMLError) as error:
            raise MergeReadinessOperationalError(f"Cannot read Change manifest: {manifest}") from error
        change = data.get("change") if isinstance(data, dict) else None
        change_id = change.get("id") if isinstance(change, dict) else None
        if not isinstance(change_id, str) or not change_id.startswith("CHG-"):
            raise MergeReadinessOperationalError(f"Malformed Change identity: {manifest}")
        result.add(change_id)
    return tuple(sorted(result))

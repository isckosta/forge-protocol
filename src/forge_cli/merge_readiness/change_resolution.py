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


def tree_file(root: Path, revision: str, relative_path: str) -> str:
    listing = _git(root, "ls-tree", revision, "--", relative_path)
    if not listing:
        raise MergeReadinessOperationalError(f"Missing file in revision {revision}: {relative_path}")
    mode = listing.split(None, 1)[0]
    if mode == "120000":
        raise MergeReadinessOperationalError(f"Symlink is not admissible evidence: {relative_path}")
    return _git(root, "show", f"{revision}:{relative_path}")


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


def affected_changes(root: Path, paths: tuple[str, ...], head_revision: str) -> tuple[str, ...]:
    result: set[str] = set()
    for path in paths:
        parts = Path(path).parts
        if len(parts) < 3 or parts[0] != ".forge" or parts[1] != "changes":
            continue
        manifest_relative = f".forge/changes/{parts[2]}/manifest.yml"
        try:
            import yaml
            data = yaml.safe_load(tree_file(root, head_revision, manifest_relative)) or {}
        except (OSError, UnicodeError, yaml.YAMLError, MergeReadinessOperationalError) as error:
            raise MergeReadinessOperationalError(f"Cannot read Change manifest: {manifest_relative}") from error
        change = data.get("change") if isinstance(data, dict) else None
        change_id = change.get("id") if isinstance(change, dict) else None
        if not isinstance(change_id, str) or not change_id.startswith("CHG-"):
            raise MergeReadinessOperationalError(f"Malformed Change identity: {manifest_relative}")
        result.add(change_id)
    return tuple(sorted(result))

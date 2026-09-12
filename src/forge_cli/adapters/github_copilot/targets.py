from __future__ import annotations

from importlib.resources import files
from pathlib import PurePosixPath

import yaml


def _checked(path: str) -> str:
    if not path or path.startswith("~") or "\\" in path or ":" in path or "\0" in path:
        raise ValueError()
    item = PurePosixPath(path)
    if item.is_absolute() or ".." in item.parts:
        raise ValueError()
    value = item.as_posix()
    if value in {"", "."} or value != ".github":
        raise ValueError("GitHub Copilot publication root must be .github.")
    return value


def validate_publication_root(publication_root: str) -> None:
    _checked(publication_root)


def load_packaged_publication_target() -> str:
    resource = files("forge_cli.adapters.github_copilot").joinpath("resources", "publication.yml")
    data = yaml.safe_load(resource.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not str(data.get("source", "")).startswith("https://") or not data.get("observed_on"):
        raise ValueError("Invalid packaged GitHub Copilot publication evidence.")
    return _checked(str(data["target"]))

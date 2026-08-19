"""User-owned Harness Adapter configuration boundary."""

from __future__ import annotations

from dataclasses import dataclass
import errno
import json
import os
from pathlib import Path
import secrets

from jsonschema import ValidationError, validate
import yaml

from forge_cli.protocol_resources import resolve_protocol_root


class InvalidAdapterConfigurationError(RuntimeError):
    code = "E_FORGE_INVALID_ADAPTER_CONFIGURATION"


@dataclass(frozen=True)
class AdapterConfiguration:
    adapter_id: str
    target: str | None

    def __post_init__(self) -> None:
        _checked_adapter_id(self.adapter_id)
        if self.target is not None:
            _checked_target(self.target)


def _checked_adapter_id(adapter_id: str) -> str:
    if (
        not isinstance(adapter_id, str)
        or not adapter_id
        or adapter_id in {".", ".."}
        or any(character in adapter_id for character in ("/", "\\", ":", "\0"))
    ):
        raise InvalidAdapterConfigurationError("Adapter configuration requires a safe Adapter id.")
    return adapter_id


def _checked_target(target: str) -> str:
    if not isinstance(target, str) or not target:
        raise InvalidAdapterConfigurationError("Adapter configuration target must be non-empty.")
    if (
        target.startswith(("/", "~"))
        or "\\" in target
        or ":" in target
        or "\0" in target
    ):
        raise InvalidAdapterConfigurationError("Adapter configuration target must be repository-relative.")

    parts = target.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise InvalidAdapterConfigurationError("Adapter configuration target must be a normalized path.")
    return target


def adapter_configuration_path(project_root: Path, adapter_id: str) -> Path:
    """Derive the only user-owned Adapter configuration location in a project."""
    return Path(project_root) / ".forge" / "adapters" / _checked_adapter_id(adapter_id) / "config.yml"


def _checked_project_root(project_root: Path) -> Path:
    root = Path(project_root)
    if root.is_symlink() or not root.is_dir():
        raise InvalidAdapterConfigurationError("Adapter configuration requires a real project root directory.")
    return root


def _reject_symlinked_components(project_root: Path, config_path: Path) -> None:
    component = project_root
    for part in config_path.relative_to(project_root).parts:
        if component.is_symlink():
            raise InvalidAdapterConfigurationError(
                "Adapter configuration path must not contain a symlink."
            )
        component /= part
    if component.is_symlink():
        raise InvalidAdapterConfigurationError("Adapter configuration path must not contain a symlink.")


def _configuration_path(project_root: Path, adapter_id: str) -> Path:
    root = _checked_project_root(project_root)
    config_path = adapter_configuration_path(root, adapter_id)
    _reject_symlinked_components(root, config_path)
    return config_path


def _require_anchored_publication_primitives() -> None:
    if (
        os.name != "posix"
        or not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
    ):
        raise InvalidAdapterConfigurationError(
            "Adapter configuration publication requires POSIX directory-descriptor support."
        )


def _open_or_create_directory(parent_fd: int, name: str) -> int:
    try:
        os.mkdir(name, mode=0o700, dir_fd=parent_fd)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    return os.open(
        name,
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        dir_fd=parent_fd,
    )


def _open_configuration_parent(project_root: Path, adapter_id: str) -> int:
    root = _checked_project_root(project_root)
    _require_anchored_publication_primitives()
    directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for name in (".forge", "adapters", _checked_adapter_id(adapter_id)):
            next_fd = _open_or_create_directory(directory_fd, name)
            os.close(directory_fd)
            directory_fd = next_fd
        return directory_fd
    except BaseException:
        os.close(directory_fd)
        raise


def _write_all(file_fd: int, content: bytes) -> None:
    offset = 0
    while offset < len(content):
        offset += os.write(file_fd, content[offset:])


def _write_configuration_atomically(parent_fd: int, content: str) -> None:
    temporary_name = f".config.yml.{secrets.token_hex(16)}.tmp"
    temporary_fd = os.open(
        temporary_name,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
        dir_fd=parent_fd,
    )
    try:
        _write_all(temporary_fd, content.encode("utf-8"))
    finally:
        os.close(temporary_fd)

    try:
        os.replace(
            temporary_name,
            "config.yml",
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
        )
    except BaseException:
        try:
            os.unlink(temporary_name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        raise


def _schema() -> dict:
    path = resolve_protocol_root() / "schemas" / "adapter-configuration.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _payload(config: AdapterConfiguration) -> dict:
    payload = {
        "schema": "forge/adapter-configuration@1",
        "adapter": _checked_adapter_id(config.adapter_id),
    }
    if config.target is not None:
        payload["target"] = config.target
    return payload


def _validate_payload(payload: object) -> dict:
    validate(instance=payload, schema=_schema())
    if not isinstance(payload, dict):
        raise InvalidAdapterConfigurationError("Adapter configuration must be a mapping.")
    return payload


def load_adapter_configuration(project_root: Path, adapter_id: str) -> AdapterConfiguration | None:
    try:
        path = _configuration_path(project_root, adapter_id)
        payload = _validate_payload(yaml.safe_load(path.read_text(encoding="utf-8")))
        if payload["adapter"] != adapter_id:
            raise InvalidAdapterConfigurationError(
                f"Adapter configuration is for {payload['adapter']!r}, not {adapter_id!r}."
            )
        return AdapterConfiguration(adapter_id=payload["adapter"], target=payload.get("target"))
    except FileNotFoundError:
        return None
    except (OSError, TypeError, KeyError, ValidationError, yaml.YAMLError) as exc:
        message = exc.message if isinstance(exc, ValidationError) else str(exc)
        raise InvalidAdapterConfigurationError(message) from exc


def write_adapter_configuration(project_root: Path, config: AdapterConfiguration) -> None:
    try:
        payload = _validate_payload(_payload(config))
        contents = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    except (TypeError, KeyError, ValidationError, yaml.YAMLError) as exc:
        message = exc.message if isinstance(exc, ValidationError) else str(exc)
        raise InvalidAdapterConfigurationError(message) from exc

    try:
        _configuration_path(project_root, config.adapter_id)
        parent_fd = _open_configuration_parent(project_root, config.adapter_id)
        try:
            _write_configuration_atomically(parent_fd, contents)
        finally:
            os.close(parent_fd)
    except (OSError, TypeError, NotImplementedError) as exc:
        raise InvalidAdapterConfigurationError(str(exc)) from exc


def resolve_configured_target(
    explicit: str | None,
    config: AdapterConfiguration | None,
    evidence: str | None,
) -> str | None:
    if explicit is not None:
        return explicit
    if config is not None and config.target is not None:
        return config.target
    return evidence

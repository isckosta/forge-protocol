from __future__ import annotations

from pathlib import Path

import pytest

from forge_cli.adapters.configuration import (
    AdapterConfiguration,
    InvalidAdapterConfigurationError,
    load_adapter_configuration,
    resolve_configured_target,
    write_adapter_configuration,
)


def test_target_precedence_is_explicit_then_config_then_evidence() -> None:
    """Catch a resolver that skips an earlier configured source."""
    config = AdapterConfiguration(adapter_id="codex", target="configured/codex")

    assert (
        resolve_configured_target("explicit/codex", config, ".agents/skills/forge")
        == "explicit/codex"
    )
    assert resolve_configured_target(None, config, ".agents/skills/forge") == "configured/codex"
    assert resolve_configured_target(None, None, ".agents/skills/forge") == ".agents/skills/forge"


@pytest.mark.parametrize("target", ["/tmp/x", "../x", r"x\\y", "C:/x", ".codex/forge"])
def test_invalid_or_forbidden_target_is_rejected(target: str) -> None:
    """Catch unsafe, cross-platform, or global Codex target acceptance."""
    with pytest.raises(InvalidAdapterConfigurationError):
        AdapterConfiguration(adapter_id="codex", target=target)


def test_load_rejects_malformed_yaml_without_returning_configuration(tmp_path: Path) -> None:
    """Catch a loader that treats malformed user YAML as no configuration."""
    path = tmp_path / ".forge" / "adapters" / "codex" / "config.yml"
    path.parent.mkdir(parents=True)
    path.write_text("schema: [unterminated", encoding="utf-8")

    with pytest.raises(InvalidAdapterConfigurationError):
        load_adapter_configuration(path, "codex")


def test_load_rejects_unknown_keys(tmp_path: Path) -> None:
    """Catch a loader that admits non-schema configuration fields."""
    path = tmp_path / "config.yml"
    path.write_text(
        "schema: forge/adapter-configuration@1\nadapter: codex\ntarget: safe/path\ninvented: true\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidAdapterConfigurationError):
        load_adapter_configuration(path, "codex")


def test_load_rejects_configuration_for_a_different_adapter(tmp_path: Path) -> None:
    """Catch cross-Adapter configuration reuse at the loading boundary."""
    path = tmp_path / "config.yml"
    path.write_text(
        "schema: forge/adapter-configuration@1\nadapter: cursor\ntarget: safe/path\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidAdapterConfigurationError):
        load_adapter_configuration(path, "codex")


def test_write_validates_before_replacing_existing_configuration(tmp_path: Path) -> None:
    """Catch invalid writes that overwrite the last known-good user configuration."""
    path = tmp_path / ".forge" / "adapters" / "codex" / "config.yml"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"last-known-good\n")

    invalid = object.__new__(AdapterConfiguration)
    object.__setattr__(invalid, "adapter_id", "")
    object.__setattr__(invalid, "target", "safe/path")

    with pytest.raises(InvalidAdapterConfigurationError):
        write_adapter_configuration(path, invalid)

    assert path.read_bytes() == b"last-known-good\n"


def test_write_rejects_a_symlinked_configuration_path_without_mutation(tmp_path: Path) -> None:
    """Catch replacement through a configuration symlink into another user file."""
    target = tmp_path / "user-owned.yml"
    target.write_bytes(b"last-known-good\n")
    path = tmp_path / ".forge" / "adapters" / "codex" / "config.yml"
    path.parent.mkdir(parents=True)
    try:
        path.symlink_to(target)
    except OSError:
        pytest.skip("Symlinks are unavailable in this environment")

    with pytest.raises(InvalidAdapterConfigurationError):
        write_adapter_configuration(
            path, AdapterConfiguration(adapter_id="codex", target="safe/path")
        )

    assert target.read_bytes() == b"last-known-good\n"

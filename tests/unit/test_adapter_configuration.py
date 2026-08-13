from __future__ import annotations

from pathlib import Path

import pytest

from forge_cli.adapters.configuration import (
    AdapterConfiguration,
    InvalidAdapterConfigurationError,
    adapter_configuration_path,
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


def test_write_derives_the_only_configuration_path_from_the_project_root(tmp_path: Path) -> None:
    """Catch a writer that treats the project root as an arbitrary output filename."""
    project_root = tmp_path / "repository"
    project_root.mkdir()
    forge_config = project_root / ".forge" / "forge.yml"
    forge_config.parent.mkdir()
    forge_config.write_bytes(b"project-owned\n")

    write_adapter_configuration(
        project_root, AdapterConfiguration(adapter_id="codex", target="safe/path")
    )

    config_path = project_root / ".forge" / "adapters" / "codex" / "config.yml"
    assert adapter_configuration_path(project_root, "codex") == config_path
    assert load_adapter_configuration(project_root, "codex") == AdapterConfiguration(
        adapter_id="codex", target="safe/path"
    )
    assert config_path.is_file()
    assert forge_config.read_bytes() == b"project-owned\n"


def test_write_does_not_treat_a_project_file_as_an_arbitrary_configuration_destination(
    tmp_path: Path,
) -> None:
    """Catch a writer that can overwrite `.forge/forge.yml` when given that path."""
    project_root = tmp_path / "repository"
    project_root.mkdir()
    forge_config = project_root / ".forge" / "forge.yml"
    forge_config.parent.mkdir()
    forge_config.write_bytes(b"project-owned\n")

    with pytest.raises(InvalidAdapterConfigurationError):
        write_adapter_configuration(
            forge_config, AdapterConfiguration(adapter_id="codex", target="safe/path")
        )

    assert forge_config.read_bytes() == b"project-owned\n"


def test_write_rejects_an_ancestor_symlink_without_escaping_the_project_root(tmp_path: Path) -> None:
    """Catch a writer that follows `.forge` into an arbitrary outside directory."""
    project_root = tmp_path / "repository"
    project_root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (project_root / ".forge").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlinks are unavailable in this environment")

    with pytest.raises(InvalidAdapterConfigurationError):
        write_adapter_configuration(project_root, AdapterConfiguration(adapter_id="codex", target="safe/path"))

    assert not (outside / "adapters" / "codex" / "config.yml").exists()


@pytest.mark.parametrize("adapter_id", ["", ".", "..", "a/b", r"a\\b", "a:b", "a\0b"])
def test_unsafe_adapter_id_is_rejected(adapter_id: str) -> None:
    """Catch Adapter ids that escape or make the derived configuration path ambiguous."""
    with pytest.raises(InvalidAdapterConfigurationError):
        AdapterConfiguration(adapter_id=adapter_id, target="safe/path")


@pytest.mark.parametrize("target", ["/tmp/x", "../x", r"x\\y", "C:/x", ".codex/forge", "~/forge"])
def test_invalid_or_forbidden_target_is_rejected(target: str) -> None:
    """Catch unsafe, cross-platform, or global Codex target acceptance."""
    with pytest.raises(InvalidAdapterConfigurationError):
        AdapterConfiguration(adapter_id="codex", target=target)


def test_load_rejects_malformed_yaml_without_returning_configuration(tmp_path: Path) -> None:
    """Catch a loader that treats malformed user YAML as no configuration."""
    project_root = tmp_path
    path = project_root / ".forge" / "adapters" / "codex" / "config.yml"
    path.parent.mkdir(parents=True)
    path.write_text("schema: [unterminated", encoding="utf-8")

    with pytest.raises(InvalidAdapterConfigurationError):
        load_adapter_configuration(project_root, "codex")


def test_load_rejects_unknown_keys(tmp_path: Path) -> None:
    """Catch a loader that admits non-schema configuration fields."""
    project_root = tmp_path
    path = project_root / ".forge" / "adapters" / "codex" / "config.yml"
    path.parent.mkdir(parents=True)
    path.write_text(
        "schema: forge/adapter-configuration@1\nadapter: codex\ntarget: safe/path\ninvented: true\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidAdapterConfigurationError):
        load_adapter_configuration(project_root, "codex")


def test_load_rejects_configuration_for_a_different_adapter(tmp_path: Path) -> None:
    """Catch cross-Adapter configuration reuse at the loading boundary."""
    project_root = tmp_path
    path = project_root / ".forge" / "adapters" / "codex" / "config.yml"
    path.parent.mkdir(parents=True)
    path.write_text(
        "schema: forge/adapter-configuration@1\nadapter: cursor\ntarget: safe/path\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidAdapterConfigurationError):
        load_adapter_configuration(project_root, "codex")


def test_write_validates_before_replacing_existing_configuration(tmp_path: Path) -> None:
    """Catch invalid writes that overwrite the last known-good user configuration."""
    project_root = tmp_path
    path = project_root / ".forge" / "adapters" / "codex" / "config.yml"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"last-known-good\n")

    invalid = object.__new__(AdapterConfiguration)
    object.__setattr__(invalid, "adapter_id", "")
    object.__setattr__(invalid, "target", "safe/path")

    with pytest.raises(InvalidAdapterConfigurationError):
        write_adapter_configuration(project_root, invalid)

    assert path.read_bytes() == b"last-known-good\n"


def test_write_rejects_a_symlinked_configuration_path_without_mutation(tmp_path: Path) -> None:
    """Catch replacement through a configuration symlink into another user file."""
    target = tmp_path / "user-owned.yml"
    target.write_bytes(b"last-known-good\n")
    project_root = tmp_path
    path = project_root / ".forge" / "adapters" / "codex" / "config.yml"
    path.parent.mkdir(parents=True)
    try:
        path.symlink_to(target)
    except OSError:
        pytest.skip("Symlinks are unavailable in this environment")

    with pytest.raises(InvalidAdapterConfigurationError):
        write_adapter_configuration(project_root, AdapterConfiguration(adapter_id="codex", target="safe/path"))

    assert target.read_bytes() == b"last-known-good\n"

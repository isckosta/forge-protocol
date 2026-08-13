from pathlib import Path

from forge_cli.protocol_resources import resolve_protocol_root


def test_prefers_packaged_protocol_resources(tmp_path: Path) -> None:
    package_root = tmp_path / "forge_cli"
    packaged_protocol = package_root / "resources" / "protocol"
    source_protocol = tmp_path / "protocol"

    packaged_protocol.mkdir(parents=True)
    source_protocol.mkdir()

    assert resolve_protocol_root(package_root=package_root, source_protocol=source_protocol) == packaged_protocol


def test_falls_back_to_source_protocol_for_editable_development(tmp_path: Path) -> None:
    package_root = tmp_path / "forge_cli"
    source_protocol = tmp_path / "protocol"
    package_root.mkdir()
    source_protocol.mkdir()

    assert resolve_protocol_root(package_root=package_root, source_protocol=source_protocol) == source_protocol

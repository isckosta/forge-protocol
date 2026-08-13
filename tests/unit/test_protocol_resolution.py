from pathlib import Path

import pytest

from forge_cli import protocol_resolution


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_ROOT = REPOSITORY_ROOT / "protocol"


def test_resolves_effective_standard_flow_from_canonical_and_project_layers() -> None:
    effective = protocol_resolution.resolve_effective_flow(
        PROTOCOL_ROOT,
        REPOSITORY_ROOT,
        "standard",
    )

    assert effective["canonical"]["flow"]["id"] == "standard"
    assert effective["canonical"]["review"]["required"] is True
    assert effective["project"]["flow"]["canonical"] == "standard"
    assert effective["project"]["review"]["blocking"] == ["blocker", "major"]


def test_rejects_unknown_canonical_flow_reference(tmp_path: Path) -> None:
    project_root = tmp_path
    flow_dir = project_root / ".forge" / "flows"
    flow_dir.mkdir(parents=True)
    (flow_dir / "custom.yml").write_text(
        "schema: forge/project-flow@1\n"
        "flow:\n"
        "  canonical: imaginary\n"
        "  enabled: true\n",
        encoding="utf-8",
    )

    with pytest.raises(protocol_resolution.UnknownCanonicalFlowError):
        protocol_resolution.resolve_effective_flow(PROTOCOL_ROOT, project_root, "custom")


def test_project_flow_cannot_redefine_canonical_stages(tmp_path: Path) -> None:
    project_root = tmp_path
    flow_dir = project_root / ".forge" / "flows"
    flow_dir.mkdir(parents=True)
    (flow_dir / "standard.yml").write_text(
        "schema: forge/project-flow@1\n"
        "flow:\n"
        "  canonical: standard\n"
        "  enabled: true\n"
        "stages: []\n",
        encoding="utf-8",
    )

    with pytest.raises(protocol_resolution.InvalidProjectFlowConfigurationError):
        protocol_resolution.resolve_effective_flow(PROTOCOL_ROOT, project_root, "standard")


def test_effective_contract_is_canonical_contract_plus_project_extension() -> None:
    effective = protocol_resolution.resolve_effective_contract(PROTOCOL_ROOT, REPOSITORY_ROOT)

    assert "## C-001 — Explicit Intent" in effective.canonical
    assert "## F-001 — Forge dogfoods Forge" in effective.project_extension
    assert effective.text.index("## C-001 — Explicit Intent") < effective.text.index(
        "## F-001 — Forge dogfoods Forge"
    )


def test_project_contract_is_optional_but_canonical_contract_is_required(tmp_path: Path) -> None:
    effective = protocol_resolution.resolve_effective_contract(PROTOCOL_ROOT, tmp_path)

    assert "## C-001 — Explicit Intent" in effective.canonical
    assert effective.project_extension == ""
    assert effective.text == effective.canonical


def test_fails_when_canonical_contract_is_unavailable(tmp_path: Path) -> None:
    protocol_root = tmp_path / "protocol"
    protocol_root.mkdir()

    with pytest.raises(protocol_resolution.CanonicalContractUnavailableError):
        protocol_resolution.resolve_effective_contract(protocol_root, tmp_path)

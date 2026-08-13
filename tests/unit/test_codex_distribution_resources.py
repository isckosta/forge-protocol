from importlib.resources import files

import yaml

from forge_cli.adapters.codex import load_codex_adapter_descriptor


def _resources_root():
    return files("forge_cli.adapters.codex").joinpath("resources")


def test_codex_descriptor_and_evidence_are_packaged_resources() -> None:
    root = _resources_root()
    adapter = root.joinpath("adapter.yml")
    capabilities = root.joinpath("capabilities.yml")

    assert adapter.is_file()
    assert capabilities.is_file()

    adapter_data = yaml.safe_load(adapter.read_text(encoding="utf-8"))
    evidence_data = yaml.safe_load(capabilities.read_text(encoding="utf-8"))
    descriptor = load_codex_adapter_descriptor()

    assert adapter_data["adapter"]["id"] == descriptor.manifest.adapter_id == "codex"
    assert adapter_data["adapter"]["version"] == descriptor.manifest.version
    assert {item["capability"] for item in evidence_data["evidence"]} == {
        item.capability for item in descriptor.evidence
    }


def test_codex_workflow_skill_template_is_packaged() -> None:
    skill = _resources_root().joinpath("skills", "workflow.md")
    assert skill.is_file()
    content = skill.read_text(encoding="utf-8")
    assert "Forge Workflow Instructions" in content
    assert "not technical enforcement" in content


def test_capability_evidence_has_stable_staleness_metadata() -> None:
    capabilities = _resources_root().joinpath("capabilities.yml")
    data = yaml.safe_load(capabilities.read_text(encoding="utf-8"))

    assert data["evidence"]
    for item in data["evidence"]:
        assert item["source"]
        assert item["observed_on"]

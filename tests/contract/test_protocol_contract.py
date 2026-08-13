from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, ValidationError
import pytest


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "protocol" / "schemas"
CATALOG_PATH = SCHEMA_DIR / "catalog.yml"
CATALOG_SCHEMA_PATH = SCHEMA_DIR / "schema-catalog.schema.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def test_supported_schema_catalog_is_closed_and_valid() -> None:
    """Catch missing, invalid, unlisted, or identity-mismatched schemas."""
    assert CATALOG_PATH.is_file(), "Protocol schema catalog is missing"
    assert CATALOG_SCHEMA_PATH.is_file(), "Protocol schema catalog schema is missing"

    catalog_schema = _load_json(CATALOG_SCHEMA_PATH)
    Draft202012Validator.check_schema(catalog_schema)

    catalog = _load_yaml(CATALOG_PATH)
    Draft202012Validator(catalog_schema).validate(catalog)

    entries = catalog["schemas"]
    identifiers = [entry["id"] for entry in entries]
    files = [entry["file"] for entry in entries]
    assert len(identifiers) == len(set(identifiers)), "Schema IDs must be unique"
    assert len(files) == len(set(files)), "Schema files must be unique"
    assert set(files) == {path.name for path in SCHEMA_DIR.glob("*.schema.json")}

    for entry in entries:
        schema = _load_json(SCHEMA_DIR / entry["file"])
        Draft202012Validator.check_schema(schema)
        assert schema["properties"]["schema"]["const"] == entry["id"]


def _catalog_schemas() -> dict[str, dict]:
    catalog = _load_yaml(CATALOG_PATH)
    return {
        entry["id"]: _load_json(SCHEMA_DIR / entry["file"])
        for entry in catalog["schemas"]
    }


def _canonical_yaml_paths() -> list[Path]:
    patterns = (
        ".forge/forge.yml",
        ".forge/flows/*.yml",
        ".forge/changes/*/manifest.yml",
        ".forge/changes/*/traceability.yml",
        ".forge/changes/*/tdd-evidence.yml",
        "protocol/flows/*.yml",
        "protocol/policies/*.yml",
        "protocol/schemas/catalog.yml",
        "src/forge_cli/adapters/*/resources/adapter.yml",
    )
    return sorted(path for pattern in patterns for path in ROOT.glob(pattern))


def test_canonical_yaml_instances_satisfy_their_declared_schemas() -> None:
    """Catch canonical repository artifacts that drift from their schema."""
    schemas = _catalog_schemas()
    failures: list[str] = []

    for path in _canonical_yaml_paths():
        instance = _load_yaml(path)
        identifier = instance.get("schema")
        if identifier not in schemas:
            failures.append(f"{path.relative_to(ROOT)}: unsupported schema {identifier!r}")
            continue
        validator = Draft202012Validator(schemas[identifier])
        for error in validator.iter_errors(instance):
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            failures.append(f"{path.relative_to(ROOT)}:{location}: {error.message}")

        if identifier == "forge/tdd-evidence@1":
            if instance["cycle_count"] != len(instance["cycles"]):
                failures.append(
                    f"{path.relative_to(ROOT)}: cycle_count does not match cycles"
                )

    assert not failures, "\n" + "\n".join(failures)


def test_canonical_flows_preserve_common_quality_gates() -> None:
    """Catch a Flow that weakens shared RED or Completion obligations."""
    completion_requirements = {
        "verification_passed",
        "review_passed",
        "blocking_review_threads_resolved",
        "documentation_impact_evaluated",
        "tdd_compliant_or_explicitly_excepted",
    }
    red_checks = {"test_exists", "red_executed", "red_failed_for_expected_reason"}

    for path in sorted((ROOT / "protocol" / "flows").glob("*.yml")):
        flow = _load_yaml(path)
        assert completion_requirements <= set(
            flow["gates"]["before_completion"]["require"]
        ), path.name
        assert red_checks <= set(
            flow["gates"]["before_behavioral_implementation"]["checks"]
        ), path.name


def test_chg_0004_migration_preserves_acceptance_mappings() -> None:
    """Catch loss or reinterpretation of historical CHG-0004 traceability."""
    traceability = _load_yaml(
        ROOT / ".forge/changes/CHG-0004-codex-adapter/traceability.yml"
    )
    assert traceability["acceptance"] == {
        "AC-001": ["T-001"],
        "AC-002": ["T-001"],
        "AC-003": ["T-001"],
        "AC-004": ["T-002"],
        "AC-005": ["T-005"],
        "AC-006": ["T-003"],
        "AC-007": ["T-004"],
        "AC-008": ["T-004"],
        "AC-009": ["T-005", "T-006"],
        "AC-010": ["T-006"],
        "AC-011": ["T-007"],
        "AC-012": ["T-007"],
        "AC-013": ["T-006"],
        "AC-014": ["T-007"],
    }
    assert traceability["requirements"] == {
        f"FR-{number:03d}": {"tasks": tasks}
        for number, tasks in {
            1: ["T-001"], 2: ["T-001"], 3: ["T-001"], 4: ["T-001"],
            5: ["T-001"], 6: ["T-001"], 7: ["T-001"], 8: ["T-001"],
            9: ["T-002"], 10: ["T-002"], 11: ["T-006"], 12: ["T-006"],
            13: ["T-002", "T-003"], 14: ["T-003"], 15: ["T-003"],
            16: ["T-003", "T-004"], 17: ["T-003"],
            18: ["T-002", "T-005"], 19: ["T-006"], 20: ["T-006"],
            21: ["T-006"], 22: ["T-006"], 23: ["T-006"],
            24: ["T-004", "T-009"], 25: ["T-004"], 26: ["T-004"],
            27: ["T-004"], 28: ["T-007"], 29: ["T-007"],
            30: ["T-007"], 31: ["T-004", "T-009"], 32: ["T-006"],
            33: ["T-007"],
        }.items()
    }


def test_adapter_schema_rejects_non_protocol_bounds() -> None:
    """Catch Adapter intervals that use invalid Protocol identifiers."""
    schema = _catalog_schemas()["forge/adapter@1"]
    instance = _load_yaml(
        ROOT / "src/forge_cli/adapters/codex/resources/adapter.yml"
    )
    instance["protocol"] = {"min": 0, "max_exclusive": 1}

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(instance)


@pytest.mark.parametrize(
    ("identifier", "instance"),
    [
        (
            "forge/policy/architecture@1",
            {"schema": "forge/policy/architecture@1", "architecture": {"invented": True}},
        ),
        (
            "forge/policy/documentation@1",
            {"schema": "forge/policy/documentation@1", "documentation": {"invented": True}},
        ),
        (
            "forge/policy/security@1",
            {"schema": "forge/policy/security@1", "security": {"invented": True}},
        ),
        (
            "forge/tdd-evidence@1",
            {
                "schema": "forge/tdd-evidence@1",
                "change": "CHG-9999",
                "status": "complete",
                "cycle_count": 1,
                "cycles": [{"id": "TDD-001"}],
            },
        ),
    ],
)
def test_stable_schemas_reject_semantically_empty_or_contradictory_artifacts(
    identifier: str,
    instance: dict,
) -> None:
    """Catch stable schemas that validate artifacts with no promised semantics."""
    with pytest.raises(ValidationError):
        Draft202012Validator(_catalog_schemas()[identifier]).validate(instance)


def _canonical_full_flow() -> dict:
    return _load_yaml(ROOT / "protocol/flows/full.yml")


def test_flow_schema_rejects_mismatched_identity() -> None:
    """Catch a Flow whose machine ID and human name contradict each other."""
    instance = _canonical_full_flow()
    instance["flow"]["name"] = "FAST"

    with pytest.raises(ValidationError):
        Draft202012Validator(_catalog_schemas()["forge/flow@1"]).validate(instance)


def test_flow_schema_rejects_behavioral_gate_without_red_checks() -> None:
    """Catch a behavioral Gate that substitutes unrelated requirements for RED."""
    instance = _canonical_full_flow()
    instance["gates"]["before_behavioral_implementation"] = {
        "require": ["not_red"]
    }

    with pytest.raises(ValidationError):
        Draft202012Validator(_catalog_schemas()["forge/flow@1"]).validate(instance)


def test_flow_schema_rejects_completion_gate_without_completion_requirements() -> None:
    """Catch a Completion Gate that substitutes unrelated checks."""
    instance = _canonical_full_flow()
    instance["gates"]["before_completion"] = {"checks": ["not_completion"]}

    with pytest.raises(ValidationError):
        Draft202012Validator(_catalog_schemas()["forge/flow@1"]).validate(instance)


def test_flow_schema_rejects_full_flow_missing_full_planning_stages() -> None:
    """Catch FULL that omits its discovery, design, planning, or knowledge stages."""
    instance = _canonical_full_flow()
    retained = {"intent", "tdd_implementation", "verification", "strict_review", "completion"}
    instance["stages"] = [stage for stage in instance["stages"] if stage["id"] in retained]

    with pytest.raises(ValidationError):
        Draft202012Validator(_catalog_schemas()["forge/flow@1"]).validate(instance)


def test_change_schema_requires_reason_for_tdd_exception() -> None:
    """Catch a Change manifest that exempts TDD without an explicit reason."""
    instance = _load_yaml(
        ROOT / ".forge/changes/CHG-0007-protocol-v1-contract-freeze/manifest.yml"
    )
    instance["tdd"] = {"status": "exception", "cycles": 0}

    with pytest.raises(ValidationError):
        Draft202012Validator(_catalog_schemas()["forge/change@1"]).validate(instance)


@pytest.mark.parametrize(
    ("identifier", "path", "section", "field"),
    [
        ("forge/policy/architecture@1", "protocol/policies/architecture.yml", "architecture", "evaluate"),
        ("forge/policy/documentation@1", "protocol/policies/documentation.yml", "documentation", "update_required_when_change_affects"),
        ("forge/policy/review@1", "protocol/policies/review.yml", "review", "dimensions"),
        ("forge/policy/security@1", "protocol/policies/security.yml", "security", "review_dimensions"),
    ],
)
def test_policy_schemas_reject_loss_of_canonical_semantic_dimensions(
    identifier: str,
    path: str,
    section: str,
    field: str,
) -> None:
    """Catch a Policy list that remains nonempty after losing its core semantics."""
    instance = _load_yaml(ROOT / path)
    instance[section][field] = ["nothing"]

    with pytest.raises(ValidationError):
        Draft202012Validator(_catalog_schemas()[identifier]).validate(instance)

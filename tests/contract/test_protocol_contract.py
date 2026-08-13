from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


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

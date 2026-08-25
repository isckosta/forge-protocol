from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "protocol" / "schemas"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _validator(schema_name: str) -> Draft202012Validator:
    schema = _load_json(SCHEMA_DIR / schema_name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.mark.parametrize("profile", ["focused", "standard", "strict"])
def test_change_v2_review_iteration_accepts_profile(profile: str) -> None:
    validator = _validator("change-v2.schema.json")
    document = _minimal_change_v2_document()
    document["review"]["iterations"][0]["profile"] = profile

    validator.validate(document)


def test_change_v2_review_iteration_omitting_profile_still_validates() -> None:
    validator = _validator("change-v2.schema.json")
    document = _minimal_change_v2_document()

    validator.validate(document)


def test_change_v2_review_iteration_rejects_invalid_profile() -> None:
    validator = _validator("change-v2.schema.json")
    document = _minimal_change_v2_document()
    document["review"]["iterations"][0]["profile"] = "adversarial"

    with pytest.raises(ValidationError):
        validator.validate(document)


@pytest.mark.parametrize("profile", ["focused", "standard", "strict"])
def test_policy_review_v2_accepts_profile(profile: str) -> None:
    validator = _validator("policy-review-v2.schema.json")
    document = _minimal_policy_review_v2_document()
    document["review"]["profile"] = profile

    validator.validate(document)


def test_policy_review_v2_omitting_profile_still_validates() -> None:
    validator = _validator("policy-review-v2.schema.json")
    document = _minimal_policy_review_v2_document()

    validator.validate(document)


@pytest.mark.parametrize("profile", ["focused", "standard", "strict"])
def test_project_flow_accepts_profile(profile: str) -> None:
    validator = _validator("project-flow.schema.json")
    document = {
        "schema": "forge/project-flow@1",
        "flow": {"canonical": "fast", "enabled": True},
        "review": {"profile": profile},
    }

    validator.validate(document)


def test_project_flow_rejects_invalid_profile() -> None:
    validator = _validator("project-flow.schema.json")
    document = {
        "schema": "forge/project-flow@1",
        "flow": {"canonical": "fast", "enabled": True},
        "review": {"profile": "adversarial"},
    }

    with pytest.raises(ValidationError):
        validator.validate(document)


@pytest.mark.parametrize("profile,strict,adversarial", [("focused", False, False), ("strict", True, True)])
def test_flow_schema_accepts_profile_with_matching_booleans(profile: str, strict: bool, adversarial: bool) -> None:
    validator = _validator("flow.schema.json")
    document = yaml.safe_load((ROOT / "protocol" / "flows" / "full.yml").read_text())
    document["review"] = {"required": True, "profile": profile, "strict": strict, "adversarial": adversarial}

    validator.validate(document)


def test_flow_schema_requires_profile() -> None:
    validator = _validator("flow.schema.json")
    document = yaml.safe_load((ROOT / "protocol" / "flows" / "full.yml").read_text())
    document["review"] = {"required": True, "strict": True, "adversarial": True}

    with pytest.raises(ValidationError):
        validator.validate(document)


def test_canonical_flow_files_declare_the_expected_profile() -> None:
    expected = {"fast": "focused", "standard": "standard", "full": "strict"}
    for flow_id, profile in expected.items():
        document = yaml.safe_load((ROOT / "protocol" / "flows" / f"{flow_id}.yml").read_text())
        assert document["review"]["profile"] == profile


def _minimal_change_v2_document() -> dict:
    return {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": "CHG-9999", "title": "Fixture", "kind": "feature"},
        "flow": {"initial": "standard", "current": "standard", "escalations": []},
        "state": {"current": "intent"},
        "artifacts": {},
        "tdd": {"status": "pending"},
        "verification": {"status": "pending"},
        "review": {
            "status": "pending",
            "iteration": 1,
            "blockers": 0,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "iterations": [{"id": "review-001", "revision": "chg-9999-001", "status": "pending"}],
        },
        "documentation": {"impact_evaluated": False},
    }


def _minimal_policy_review_v2_document() -> dict:
    return {
        "schema": "forge/policy/review@2",
        "review": {
            "required": True,
            "strict": True,
            "adversarial": True,
            "objective": "Identify plausible reasons for rejection.",
            "severities": ["blocker", "major", "minor", "observation"],
            "blocking": ["blocker", "major"],
            "dimensions": ["correctness"],
            "evidence": {"required_for": ["blocker", "major"]},
            "reviewer_resolver_separation": {
                "independence": {"fast": "execution_context", "standard": "execution_context", "full": "execution_context"},
                "same_execution_forbidden": True,
                "same_context_forbidden": True,
                "provenance_required_for_review_passed": True,
                "minimum_assurance": "recorded",
                "logical_revision_binding_required": True,
                "immutable_revision_binding_required": True,
                "review_subject_freeze_required": True,
                "post_freeze_subject_mutation_invalidates_binding": True,
            },
            "diff_only_review": False,
            "passing_tests_are_sufficient": False,
            "re_review": {
                "required_after_blocking_resolution": True,
                "independent_from_resolution_execution": True,
                "target_resolution_revision": True,
                "target_concrete_immutable_revision": True,
            },
        },
    }


def test_no_historical_change_is_invalidated_by_the_review_profile_change() -> None:
    """CHG-0048 TDD-015 (FR-011): forge validate against this repository's
    own .forge/ (containing every historical Change manifest) must still
    report no findings after the Review Profile schema/Flow/Contract
    changes -- the additive fields default to strict for anything that
    predates them."""
    from forge_cli import validation

    result = validation.validate_project(ROOT, ROOT / "protocol")

    assert result.passed is True, result.findings

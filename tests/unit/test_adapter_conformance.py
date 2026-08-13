from forge_cli.adapters.capabilities import CapabilityLimitation


def test_conformance_rejects_missing_required_flow_stage_and_gate() -> None:
    from forge_cli.adapters import validation

    assert hasattr(validation, "validate_conformance"), "Adapter conformance validation is not implemented yet"

    requirements = validation.ConformanceRequirements(
        required_stages=("specification", "tdd_implementation", "strict_review"),
        required_gates=("red_gate", "review_gate"),
        required_invariants=("C-008", "C-022"),
        tdd_red_required=True,
        strict_review_required=True,
    )
    representation = validation.AdapterRepresentation(
        stages=("specification", "tdd_implementation"),
        gates=("red_gate",),
        represented_invariants=("C-008", "C-022"),
        enforced_invariants=("C-008", "C-022"),
        limitations=(),
        repository_authority_preserved=True,
    )

    findings = validation.validate_conformance(requirements, representation)

    assert {finding.code for finding in findings} >= {
        "E_FORGE_ADAPTER_STAGE_REMOVED",
        "E_FORGE_ADAPTER_GATE_REMOVED",
    }


def test_conformance_rejects_representation_that_authorizes_behavior_without_red() -> None:
    from forge_cli.adapters import validation

    requirements = validation.ConformanceRequirements(
        required_stages=("tdd_implementation",),
        required_gates=("red_gate",),
        required_invariants=("C-008", "C-009", "C-010"),
        tdd_red_required=True,
        strict_review_required=False,
    )
    representation = validation.AdapterRepresentation(
        stages=("tdd_implementation",),
        gates=("red_gate",),
        represented_invariants=("C-008", "C-009", "C-010"),
        enforced_invariants=("C-008", "C-009", "C-010"),
        limitations=(),
        repository_authority_preserved=True,
        red_before_behavior_preserved=False,
    )

    findings = validation.validate_conformance(requirements, representation)

    assert "E_FORGE_ADAPTER_TDD_RED_BYPASSED" in {finding.code for finding in findings}


def test_conformance_rejects_strict_review_bypass() -> None:
    from forge_cli.adapters import validation

    requirements = validation.ConformanceRequirements(
        required_stages=("strict_review",),
        required_gates=("review_gate",),
        required_invariants=("C-022", "C-023"),
        tdd_red_required=False,
        strict_review_required=True,
    )
    representation = validation.AdapterRepresentation(
        stages=("strict_review",),
        gates=("review_gate",),
        represented_invariants=("C-022", "C-023"),
        enforced_invariants=("C-022", "C-023"),
        limitations=(),
        repository_authority_preserved=True,
        strict_review_preserved=False,
    )

    findings = validation.validate_conformance(requirements, representation)

    assert "E_FORGE_ADAPTER_STRICT_REVIEW_BYPASSED" in {finding.code for finding in findings}


def test_unenforced_invariant_requires_explicit_limitation_but_must_remain_represented() -> None:
    from forge_cli.adapters import validation

    requirements = validation.ConformanceRequirements(
        required_stages=(),
        required_gates=(),
        required_invariants=("C-022",),
        tdd_red_required=False,
        strict_review_required=False,
    )
    limitation = CapabilityLimitation(
        requirement_id="C-022",
        capability="hooks",
        source_reference="C-022",
        enforced=False,
    )
    representation = validation.AdapterRepresentation(
        stages=(),
        gates=(),
        represented_invariants=("C-022",),
        enforced_invariants=(),
        limitations=(limitation,),
        repository_authority_preserved=True,
    )

    findings = validation.validate_conformance(requirements, representation)

    assert findings == ()


def test_missing_invariant_representation_is_never_excused_by_limitation() -> None:
    from forge_cli.adapters import validation

    requirements = validation.ConformanceRequirements(
        required_stages=(),
        required_gates=(),
        required_invariants=("C-022",),
        tdd_red_required=False,
        strict_review_required=False,
    )
    limitation = CapabilityLimitation(
        requirement_id="C-022",
        capability="hooks",
        source_reference="C-022",
        enforced=False,
    )
    representation = validation.AdapterRepresentation(
        stages=(),
        gates=(),
        represented_invariants=(),
        enforced_invariants=(),
        limitations=(limitation,),
        repository_authority_preserved=True,
    )

    findings = validation.validate_conformance(requirements, representation)

    assert "E_FORGE_ADAPTER_INVARIANT_REMOVED" in {finding.code for finding in findings}


def test_conformance_rejects_harness_representation_as_semantic_authority() -> None:
    from forge_cli.adapters import validation

    requirements = validation.ConformanceRequirements(
        required_stages=(),
        required_gates=(),
        required_invariants=(),
        tdd_red_required=False,
        strict_review_required=False,
    )
    representation = validation.AdapterRepresentation(
        stages=(),
        gates=(),
        represented_invariants=(),
        enforced_invariants=(),
        limitations=(),
        repository_authority_preserved=False,
    )

    findings = validation.validate_conformance(requirements, representation)

    assert "E_FORGE_ADAPTER_AUTHORITY_SHIFT" in {finding.code for finding in findings}

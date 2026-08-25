from forge_cli.adapters.codex.projection import (
    CodexProjectionInput,
    generate_codex_projection_bundle,
    generate_codex_skill_bundle,
)

FLOW = """flow:\n  id: full\nstages:\n  - id: specification_review\n  - id: tdd_implementation\n  - id: verification\n  - id: strict_review\n  - id: completion\ngates:\n  before_completion:\n    require: [verification_passed, review_passed, blocking_review_threads_resolved]\n  before_behavioral_implementation:\n    checks: [red_executed, red_failed_for_expected_reason]\n"""
BLOCKING_THREAD_INSTRUCTION = (
    "Completion requires all blocking review threads on any active external "
    "review surface to be resolved"
)
DOCUMENTATION_INSTRUCTION = "Completion requires Documentation Impact to be evaluated."
REQUIRED_DOCS_INSTRUCTION = "Completion requires required documentation to be updated."
TDD_EXCEPTION_INSTRUCTION = (
    "Completion requires TDD compliance or an explicit, recorded exception."
)
STANDARD_FLOW = (
    "flow:\n  id: standard\nstages:\n  - id: plan\n  - id: tdd_implementation\n"
    "gates:\n  before_implementation:\n    require: [intent_present, discovery_complete, "
    "specification_complete, specification_gate_passed, plan_complete]\n"
    "  before_completion:\n    require: [verification_passed, review_passed]\n"
)


def _content(flow_content: str = FLOW, protocol_id: int = 1) -> str:
    bundle = generate_codex_projection_bundle(CodexProjectionInput(
        flow_id="full",
        flow_content=flow_content,
        contract_content="Canonical Forge state is authoritative.\n",
        protocol_id=protocol_id,
    ))
    return "\n".join(item.content for item in bundle.resources)


def test_projection_keeps_required_stage_order_in_the_effective_flow_reference() -> None:
    content = _content()
    stages = ["specification_review", "tdd_implementation", "verification", "strict_review", "completion"]
    for stage in stages:
        assert stage in content
    positions = [content.index(stage) for stage in stages]
    assert positions == sorted(positions)


def test_projection_renders_understandable_red_gate_instructions() -> None:
    content = _content()
    assert "RED must be executed." in content
    assert "RED must fail for the expected reason." in content


def test_projection_renders_understandable_completion_gate_instructions() -> None:
    content = _content()
    assert "Completion requires Verification to pass." in content
    assert "Completion requires Strict Review to pass." in content


def test_projection_renders_understandable_blocking_review_thread_instruction() -> None:
    assert BLOCKING_THREAD_INSTRUCTION in _content()


def test_projection_does_not_invent_blocking_review_thread_gate() -> None:
    flow_without_gate = FLOW.replace(
        ", blocking_review_threads_resolved",
        "",
    )

    assert BLOCKING_THREAD_INSTRUCTION not in _content(flow_without_gate)


def test_projection_keeps_mixed_flow_gate_obligations_scoped_to_each_flow() -> None:
    """Checks split across Flows must not be rendered as one composite gate."""
    bundle = generate_codex_skill_bundle(
        contract_content="contract",
        flows=(
            ("zeta", """gates:
  before_behavioral_implementation:
    checks: [red_failed_for_expected_reason]
  before_completion:
    require: [review_passed]
"""),
            ("alpha", """gates:
  before_behavioral_implementation:
    checks: [red_executed]
  before_completion:
    require: [verification_passed]
"""),
    ),
    )
    skill = next(resource.content for resource in bundle.resources if resource.name == "SKILL.md")
    assert "### Flow `alpha` gate obligations" in skill
    assert "### Flow `zeta` gate obligations" in skill
    alpha = skill.index("### Flow `alpha` gate obligations")
    zeta = skill.index("### Flow `zeta` gate obligations")

    assert alpha < zeta
    alpha_section = skill[alpha:zeta]
    zeta_section = skill[zeta:]
    assert "RED must be executed." in alpha_section
    assert "RED must fail for the expected reason." not in alpha_section
    assert "Completion requires Verification to pass." in alpha_section
    assert "Completion requires Strict Review to pass." not in alpha_section
    assert "RED must fail for the expected reason." in zeta_section
    assert "RED must be executed." not in zeta_section
    assert "Completion requires Strict Review to pass." in zeta_section
    assert "Completion requires Verification to pass." not in zeta_section


def test_projection_marks_instructions_as_representation_not_enforcement() -> None:
    content = _content()
    assert "represent Forge requirements" in content
    assert "not technical enforcement" in content


def test_projection_renders_documentation_and_tdd_completion_gate_instructions() -> None:
    flow = FLOW.replace(
        "require: [verification_passed, review_passed, blocking_review_threads_resolved]",
        "require: [verification_passed, review_passed, blocking_review_threads_resolved, "
        "documentation_impact_evaluated, required_documentation_updated, "
        "tdd_compliant_or_explicitly_excepted]",
    )
    content = _content(flow)
    assert DOCUMENTATION_INSTRUCTION in content
    assert REQUIRED_DOCS_INSTRUCTION in content
    assert TDD_EXCEPTION_INSTRUCTION in content


def test_projection_does_not_invent_documentation_or_tdd_exception_gates() -> None:
    content = _content()
    assert DOCUMENTATION_INSTRUCTION not in content
    assert REQUIRED_DOCS_INSTRUCTION not in content
    assert TDD_EXCEPTION_INSTRUCTION not in content


def test_projection_renders_pre_implementation_boundary_instruction() -> None:
    bundle = generate_codex_skill_bundle(
        contract_content="contract",
        flows=(("standard", STANDARD_FLOW),),
    )
    skill = next(resource.content for resource in bundle.resources if resource.name == "SKILL.md")
    assert "Implementation MUST NOT begin until" in skill
    for check in (
        "intent_present",
        "discovery_complete",
        "specification_complete",
        "specification_gate_passed",
        "plan_complete",
    ):
        assert check in skill


def test_projection_does_not_invent_pre_implementation_boundary_for_flow_without_one() -> None:
    """FAST has no Plan stage and legitimately declares no `before_implementation` gate."""
    content = _content()
    assert "Implementation MUST NOT begin until" not in content


_REVIEW_GATE_FLOW = "gates:\n  before_completion:\n    require: [review_passed]\n"


def _flow_with_profile(profile: str) -> str:
    return f"review:\n  profile: {profile}\n" + _REVIEW_GATE_FLOW


def test_projection_renders_focused_profile_instruction_for_fast() -> None:
    """CHG-0048 TDD-011 (Codex parity with Claude Code TDD-010)."""
    content = _content(_flow_with_profile("focused"), protocol_id=2)
    assert "`focused` profile" in content
    assert "Completion requires Strict Review to pass." not in content


def test_projection_renders_standard_profile_instruction_for_standard() -> None:
    """CHG-0048 TDD-011."""
    content = _content(_flow_with_profile("standard"), protocol_id=2)
    assert "`standard` profile" in content
    assert "Completion requires Strict Review to pass." not in content


def test_projection_renders_unchanged_strict_instruction_for_full() -> None:
    """CHG-0048 TDD-011 / AC-004."""
    content = _content(_flow_with_profile("strict"), protocol_id=2)
    assert "Completion requires Strict Review to pass." in content


def test_projection_defaults_to_strict_when_flow_declares_no_profile() -> None:
    content = _content(_REVIEW_GATE_FLOW, protocol_id=2)
    assert "Completion requires Strict Review to pass." in content


def test_projection_matches_claude_code_profile_instruction_text() -> None:
    """CHG-0048 TDD-011: both Adapters must render the exact same per-profile
    instruction text, sourced from the same shared module, not independently
    authored copies."""
    from forge_cli.adapters.review_independence import REVIEW_PROFILE_INSTRUCTION as shared

    for profile in ("focused", "standard", "strict"):
        content = _content(_flow_with_profile(profile), protocol_id=2)
        assert shared[profile] in content


def test_projection_uses_fixed_strict_review_instruction_under_protocol_1_even_with_a_profile() -> None:
    """CHG-0048 Iteration 1 R-001 (Codex parity): Protocol 1 has no Review
    Profile concept -- a Protocol 1 project must never receive a scoped
    focused/standard instruction merely because the canonical Flow file
    happens to carry a profile field."""
    content = _content(_flow_with_profile("focused"), protocol_id=1)
    assert "Completion requires Strict Review to pass." in content
    assert "`focused` profile" not in content

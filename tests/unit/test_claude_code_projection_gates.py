from forge_cli.adapters.claude_code.projection import (
    ClaudeCodeProjectionInput,
    generate_claude_code_projection_bundle,
    generate_claude_code_skill_bundle,
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


def _content(flow_content: str = FLOW) -> str:
    bundle = generate_claude_code_projection_bundle(ClaudeCodeProjectionInput(
        flow_id="full",
        flow_content=flow_content,
        contract_content="Canonical Forge state is authoritative.\n",
    ))
    return "\n".join(item.content for item in bundle.resources)


def _skill_content(flows) -> str:
    bundle = generate_claude_code_skill_bundle(contract_content="contract", flows=flows)
    return next(resource.content for resource in bundle.resources if resource.name == "skills/forge/SKILL.md")


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


def test_projection_renders_reviewer_resolver_independence_guidance_under_protocol_2() -> None:
    """CHG-0018: this Protocol-level guidance is harness-neutral, not
    Codex-specific -- a Claude Code session under Protocol 2 needs the
    exact same independence instructions Codex sessions already get."""
    bundle = generate_claude_code_skill_bundle(
        contract_content="contract",
        flows=(("standard", STANDARD_FLOW),),
        protocol_id=2,
    )
    skill = next(resource.content for resource in bundle.resources if resource.name == "skills/forge/SKILL.md")
    assert "Reviewer/Resolver independence" in skill
    assert "self-review" in skill


def test_projection_omits_reviewer_resolver_independence_guidance_under_protocol_1() -> None:
    bundle = generate_claude_code_skill_bundle(
        contract_content="contract",
        flows=(("standard", STANDARD_FLOW),),
        protocol_id=1,
    )
    skill = next(resource.content for resource in bundle.resources if resource.name == "skills/forge/SKILL.md")
    assert "Reviewer/Resolver independence" not in skill


def test_projection_keeps_mixed_flow_gate_obligations_scoped_to_each_flow() -> None:
    """Checks split across Flows must not be rendered as one composite gate."""
    skill = _skill_content((
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
    ))
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
    skill = _skill_content((("standard", STANDARD_FLOW),))
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


_MINIMAL_GATE_FLOW = "gates:\n  before_completion:\n    require: [verification_passed]\n"


def _protocol_2_skill_content(flows) -> str:
    bundle = generate_claude_code_skill_bundle(
        contract_content="contract", flows=flows, protocol_id=2
    )
    return next(resource.content for resource in bundle.resources if resource.name == "skills/forge/SKILL.md")


def test_projection_renders_reviewer_resolver_independence_exactly_once_across_flows() -> None:
    """CHG-0045 TDD-001: the independence block must not be re-emitted per Flow."""
    skill = _protocol_2_skill_content((
        ("fast", _MINIMAL_GATE_FLOW),
        ("standard", _MINIMAL_GATE_FLOW),
        ("full", _MINIMAL_GATE_FLOW),
    ))
    assert skill.count("### Reviewer/Resolver independence") == 1


def test_projection_renders_the_plan_decision_sentence_exactly_once_across_flows() -> None:
    """CHG-0045 TDD-005: the CHG-0025/C-077 Plan Decision sentence must not be
    re-embedded per Flow inside gate-obligation rendering; it is sourced once
    from workflow.md."""
    skill = _protocol_2_skill_content((
        ("standard", _MINIMAL_GATE_FLOW),
        ("full", _MINIMAL_GATE_FLOW),
    ))
    assert skill.count("CHG-0025") == 1


def test_projection_points_every_applicable_flow_at_the_shared_independence_section() -> None:
    """CHG-0045 TDD-002: a Flow-scoped reader must still be told the requirement applies."""
    skill = _protocol_2_skill_content((
        ("fast", _MINIMAL_GATE_FLOW),
        ("standard", _MINIMAL_GATE_FLOW),
        ("full", _MINIMAL_GATE_FLOW),
    ))
    heading = "### Flow `{flow}` gate obligations"
    positions = {flow: skill.index(heading.format(flow=flow)) for flow in ("fast", "standard", "full")}
    ordered = sorted(positions.items(), key=lambda item: item[1])
    bounds = [start for _, start in ordered] + [len(skill)]
    for index, (flow, start) in enumerate(ordered):
        section = skill[start:bounds[index + 1]]
        assert "Reviewer/Resolver independence" in section, (
            f"Flow `{flow}` gate-obligations section has no pointer to the shared "
            "independence section"
        )


_REVIEW_GATE_FLOW = "gates:\n  before_completion:\n    require: [review_passed]\n"


def _flow_with_profile(profile: str) -> str:
    return f"review:\n  profile: {profile}\n" + _REVIEW_GATE_FLOW


def test_projection_renders_focused_profile_instruction_for_fast() -> None:
    """CHG-0048 TDD-010."""
    skill = _protocol_2_skill_content((("fast", _flow_with_profile("focused")),))
    assert "`focused` profile" in skill
    assert "Completion requires Strict Review to pass." not in skill


def test_projection_renders_standard_profile_instruction_for_standard() -> None:
    """CHG-0048 TDD-010."""
    skill = _protocol_2_skill_content((("standard", _flow_with_profile("standard")),))
    assert "`standard` profile" in skill
    assert "Completion requires Strict Review to pass." not in skill


def test_projection_renders_unchanged_strict_instruction_for_full() -> None:
    """CHG-0048 TDD-010 / AC-004: FULL's instruction is unchanged in substance."""
    skill = _protocol_2_skill_content((("full", _flow_with_profile("strict")),))
    assert "Completion requires Strict Review to pass." in skill


def test_projection_defaults_to_strict_when_flow_declares_no_profile() -> None:
    """Backward compatibility: a Flow document with no review.profile key
    (the pre-CHG-0048 shape) is treated as strict."""
    skill = _protocol_2_skill_content((("full", _REVIEW_GATE_FLOW),))
    assert "Completion requires Strict Review to pass." in skill


def test_projection_review_instructions_are_pairwise_distinct_across_profiles() -> None:
    """CHG-0048 TDD-010."""
    skill = _protocol_2_skill_content((
        ("fast", _flow_with_profile("focused")),
        ("standard", _flow_with_profile("standard")),
        ("full", _flow_with_profile("strict")),
    ))
    heading = "### Flow `{flow}` gate obligations"
    positions = {flow: skill.index(heading.format(flow=flow)) for flow in ("fast", "standard", "full")}
    ordered = sorted(positions.items(), key=lambda item: item[1])
    bounds = [start for _, start in ordered] + [len(skill)]
    sections = {}
    for index, (flow, start) in enumerate(ordered):
        sections[flow] = skill[start:bounds[index + 1]]
    lines = {flow: next(line for line in section.splitlines() if "Completion requires" in line and "Review" in line) for flow, section in sections.items()}
    assert len({lines["fast"], lines["standard"], lines["full"]}) == 3


def test_projection_reviewer_resolver_independence_block_is_unaffected_by_profile() -> None:
    """CHG-0048 TDD-012: independence block stays single, shared, unchanged."""
    skill = _protocol_2_skill_content((
        ("fast", _flow_with_profile("focused")),
        ("standard", _flow_with_profile("standard")),
        ("full", _flow_with_profile("strict")),
    ))
    assert skill.count("### Reviewer/Resolver independence") == 1


def test_projection_review_profile_is_derived_fresh_not_cached() -> None:
    """CHG-0048 TDD-014 (FR-012): simulates a C-005 escalation between two
    renders of the same Flow id -- the second render must reflect the new
    profile, proving there is no module-level cache keyed only on flow_id."""
    first = _protocol_2_skill_content((("full", _flow_with_profile("focused")),))
    second = _protocol_2_skill_content((("full", _flow_with_profile("strict")),))

    assert "`focused` profile" in first
    assert "Completion requires Strict Review to pass." in second
    assert "`focused` profile" not in second

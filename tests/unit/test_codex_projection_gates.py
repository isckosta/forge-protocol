from forge_cli.adapters.codex.projection import CodexProjectionInput, generate_codex_projection_bundle

FLOW = """flow:\n  id: full\nstages:\n  - id: specification_review\n  - id: tdd_implementation\n  - id: verification\n  - id: strict_review\n  - id: completion\ngates:\n  before_behavioral_implementation:\n    checks: [red_executed, red_failed_for_expected_reason]\n  before_completion:\n    require: [verification_passed, review_passed, blocking_review_threads_resolved]\n"""
BLOCKING_THREAD_INSTRUCTION = (
    "Completion requires all blocking review threads on any active external "
    "review surface to be resolved"
)


def _content(flow_content: str = FLOW) -> str:
    bundle = generate_codex_projection_bundle(CodexProjectionInput(
        flow_id="full",
        flow_content=flow_content,
        contract_content="Canonical Forge state is authoritative.\n",
    ))
    return "\n".join(item.content for item in bundle.resources)


def test_projection_presents_required_stage_order() -> None:
    content = _content()
    labels = ["Specification Review", "TDD Implementation", "Verification", "Strict Review", "Completion"]
    for label in labels:
        assert label in content
    positions = [content.index(label) for label in labels]
    assert positions == sorted(positions)


def test_projection_presents_red_gate() -> None:
    content = _content()
    assert "RED must be executed" in content
    assert "RED must fail for the expected reason" in content
    assert "Behavioral implementation requires valid RED" in content


def test_projection_presents_completion_gate() -> None:
    content = _content()
    assert "Completion requires Verification to pass" in content
    assert "Completion requires Strict Review to pass" in content


def test_projection_presents_blocking_review_thread_gate() -> None:
    assert BLOCKING_THREAD_INSTRUCTION in _content()


def test_projection_does_not_invent_blocking_review_thread_gate() -> None:
    flow_without_gate = FLOW.replace(
        ", blocking_review_threads_resolved",
        "",
    )

    assert BLOCKING_THREAD_INSTRUCTION not in _content(flow_without_gate)


def test_projection_marks_instructions_as_representation_not_enforcement() -> None:
    content = _content()
    assert "represent Forge requirements" in content
    assert "not technical enforcement" in content

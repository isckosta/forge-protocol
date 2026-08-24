"""CHG-0045: Reviewer/Resolver-independence text must have one shared
source consumed by every Harness Adapter, not one hand-maintained copy
per Adapter."""

from pathlib import Path

from forge_cli.adapters.review_independence import (
    REVIEWER_RESOLVER_INDEPENDENCE_LINES,
    render_reviewer_resolver_independence_section,
)
from forge_cli.adapters.claude_code import projection as claude_code_projection
from forge_cli.adapters.codex import projection as codex_projection
from forge_cli.protocol_resolution import resolve_effective_contract

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_claude_code_and_codex_import_the_same_shared_independence_source() -> None:
    """CHG-0045 TDD-003: both drivers must resolve to the same shared object,
    not two independently defined constants that could silently diverge."""
    assert claude_code_projection.REVIEWER_RESOLVER_INDEPENDENCE_LINES is REVIEWER_RESOLVER_INDEPENDENCE_LINES
    assert codex_projection.REVIEWER_RESOLVER_INDEPENDENCE_LINES is REVIEWER_RESOLVER_INDEPENDENCE_LINES


def test_shared_independence_text_agrees_with_the_effective_c026_paragraph() -> None:
    """CHG-0045 TDD-004: the shared rendering must not silently diverge from
    the actual Contract paragraph on the specific claims both make. This is
    an early-warning regression guard, not a proof of semantic equivalence
    (Specification NFR-001)."""
    effective = resolve_effective_contract(
        _REPO_ROOT / "protocol", _REPO_ROOT, protocol_id=2
    )
    contract_text = effective.canonical
    start = contract_text.index("## C-026")
    end = contract_text.index("## C-027")
    c026_text = contract_text[start:end]

    rendered = render_reviewer_resolver_independence_section()

    required_terms = (
        "Execution",
        "Execution Context",
        "claimed",
        "recorded",
        "verified",
        "Role",
    )
    for term in required_terms:
        assert term in c026_text, f"C-026 no longer mentions {term!r}; update the fixture"
        assert term in rendered, f"Shared independence text is missing {term!r} present in C-026"

"""Shared C-026 Reviewer/Resolver-independence text.

CHG-0045: this text was previously hand-maintained twice — once inside
each Harness Adapter's own `projection.py` — and, within the Claude Code
Adapter alone, re-emitted once per effective Flow. Every Adapter that
needs to render this guidance imports it from here instead of defining
its own copy, so a future wording change (or a future third Adapter)
never has to touch more than one file to stay in agreement with the
others.

This remains hand-authored English prose, not content mechanically
derived from `protocol/contract/engineering.md`'s C-026 paragraph — no
such derivation mechanism exists in this codebase, and building one would
be exactly the kind of hidden automation F-010 disfavors (Specification
NFR-001). `tests/unit/test_adapter_review_independence.py` instead keeps
this text and the effective C-026 paragraph from silently diverging on
the specific claims both make.
"""

from __future__ import annotations

REVIEWER_RESOLVER_INDEPENDENCE_LABEL = "Reviewer/Resolver independence"
REVIEWER_RESOLVER_INDEPENDENCE_HEADING = f"### {REVIEWER_RESOLVER_INDEPENDENCE_LABEL}"

REVIEWER_RESOLVER_INDEPENDENCE_LINES: tuple[str, ...] = (
    REVIEWER_RESOLVER_INDEPENDENCE_HEADING,
    "",
    "- Under Protocol 2, Strict Review must run in an Execution and Execution Context "
    "independent from the implementation or resolution that produced the revision under review.",
    "- Merely changing Role inside the same conversation, thread, session, or reasoning "
    "context is self-review and cannot satisfy Strict Review.",
    "- Finish the Implementation/Resolution and all reviewable evidence before freezing the "
    "review subject.",
    "- Before freezing, ensure the effective reviewable Git workspace is clean: no committed "
    "post-subject delta, staged reviewable changes, unstaged reviewable changes, or "
    "Git-visible untracked reviewable files.",
    "- Identify the concrete immutable subject revision. In Git, use the subject commit SHA; "
    "`revision.id` alone is not sufficient.",
    "- Record the frozen subject in `provenance.yml`; the Review Iteration references it "
    "through `subject_provenance`.",
    "- Only the exact Change-local `manifest.yml`, `provenance.yml`, and `review.md` paths are "
    "review-control metadata that may differ after the freeze; do not generalize that "
    "exception to the Change directory, matching basenames, symlinks, or rename targets.",
    "- Git-ignored cache/editor/temp files do not count as reviewable workspace mutations for "
    "the freeze invariant.",
    "- Re-check committed, staged, unstaged, and untracked reviewable deltas after recording "
    "review-control metadata.",
    "- Start Strict Review against the frozen subject, not an ambiguous later HEAD or dirty "
    "checkout.",
    "- Record the independent Reviewer execution through `reviewer_provenance`; it must bind "
    "to the exact same logical revision and immutable reference.",
    "- Reviewer Execution and Context must both differ from the subject. Distinct invented IDs "
    "are not evidence.",
    "- `claimed` is insufficient; `recorded` is repository-native self-recorded evidence and "
    "`verified` is stronger observer-backed evidence.",
    "- After blocking findings are resolved, freeze the new Resolution revision and re-review "
    "that concrete revision independently.",
)

REVIEWER_RESOLVER_INDEPENDENCE_POINTER = (
    f"- Strict Review for this Flow is subject to the single "
    f'"{REVIEWER_RESOLVER_INDEPENDENCE_LABEL}" section below; it is not restated per Flow.'
)

# CHG-0048: one shared per-profile review-instruction source for both
# Adapters, mirroring the independence block above -- a profile changes
# what a Reviewer is instructed to do (this text), never independence,
# evidence, severities, or convergence (Contract-invariant, unconditioned
# on profile).
REVIEW_PROFILE_INSTRUCTION: dict[str, str] = {
    "focused": (
        "- Completion requires Review to pass, at the `focused` profile: "
        "scoped to the actual diff, the regressions it could introduce, the "
        "Requirement(s) it targets, and any material Finding actually "
        "observed -- not an unrestricted search for any conceivable "
        "rejection ground."
    ),
    "standard": (
        "- Completion requires Review to pass, at the `standard` profile: "
        "genuine, evidence-based evaluation of Specification compliance, "
        "correctness, and implementation quality -- without the `strict` "
        "profile's added obligation to exhaustively search beyond the "
        "Change's own declared scope and evidence."
    ),
    "strict": "- Completion requires Strict Review to pass.",
}


def render_reviewer_resolver_independence_section() -> str:
    """Render the shared independence block as one standalone section."""
    return "\n".join(("", *REVIEWER_RESOLVER_INDEPENDENCE_LINES))

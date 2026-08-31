"""Shared CHG-0050/RFC-0008 Review Experience Mode text.

`_gate_instructions` in each Adapter's `projection.py` runs once per
canonical Flow at `forge adapter install` time, before any specific
Change exists -- it has no access to a particular Change's
`manifest.review.mode`/`current_phase`. What it *can* project,
per Flow, is the resolved-profile table for that Flow's own floor (a
pure function of the floor, not of any Change), plus one shared,
Flow-invariant block explaining the phase vocabulary and pointing the
Harness at `manifest.yml` and `forge change review-status` for a given
Change's live selection and phase. This mirrors
`review_independence.py`'s existing split between per-Flow lines and
one shared trailing section.
"""

from __future__ import annotations

from forge_cli.protocol_resolution import resolve_effective_review_profile

PHASE_LABELS: dict[str, str] = {
    "scanning": "Discovery",
    "findings_recorded": "Findings",
    "resolving": "Resolution",
    "re_reviewing": "Re-review",
    "converged": "Converged",
    "stopped": "Stopped",
}

REVIEW_EXPERIENCE_LABEL = "Review Experience Modes"
REVIEW_EXPERIENCE_HEADING = f"### {REVIEW_EXPERIENCE_LABEL}"

REVIEW_EXPERIENCE_LINES: tuple[str, ...] = (
    REVIEW_EXPERIENCE_HEADING,
    "",
    "- A Change MAY set `manifest.yml`'s `review.mode` "
    "(`recommended` | `fast` | `thorough`, default `recommended`) to "
    "select a developer-facing Review Experience Mode -- this never "
    "lowers the effective Review Profile below the Flow-derived floor "
    "shown above; `thorough` raises it by one rank instead.",
    "- A Change's Review phase (`manifest.yml`'s `review.current_phase`) "
    "is one of: `scanning` (Discovery), `findings_recorded` (Findings), "
    "`resolving` (Resolution), `re_reviewing` (Re-review), `converged` "
    "(Converged), or `stopped` (Stopped). `stopped` records that the "
    "developer ended further processing; it carries no Completion or "
    "approval authority.",
    "- Run `forge change review-status <slug>` for a given Change's "
    "live mode, resolved profile, current phase, and outstanding "
    "Finding counts.",
)


def render_review_experience_section() -> str:
    """Render the shared Review Experience Modes block as one standalone section."""
    return "\n".join(("", *REVIEW_EXPERIENCE_LINES))


def render_mode_resolution_line(floor: str) -> str:
    """Render the per-Flow mode-to-profile resolution table for this Flow's floor."""
    thorough = resolve_effective_review_profile(floor, "thorough")
    return (
        f"- This Flow's Review Profile floor is `{floor}`: `review.mode: "
        f"recommended` or `fast` resolves to `{floor}`; `thorough` "
        f"resolves to `{thorough}`."
    )

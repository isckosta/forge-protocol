# ADR-0011 — Review Convergence Boundary

Status: Accepted for CHG-0011 Implementation; independent Strict Review pending.

## Decision
A Strict Review Iteration MAY declare `kind`: `initial_review` or
`resolution_verification`. Absence of `kind` preserves exact current
Protocol 2 behavior — this is an additive, opt-in extension, not a new
mandatory obligation, and does not require a new integer Protocol or schema
suffix (`protocol/compatibility.md`).

A `resolution_verification` Iteration is bound to the Resolution it follows,
not an unrestricted re-audit. The Resolution's provenance record declares
`scope` (paths/globs) and `targets` (Finding IDs). Core computes the
Resolution Delta as the plain committed diff between the prior Iteration's
frozen subject and this Iteration's frozen subject — both already-immutable
historical commits, so this reuses only the committed-diff half of the
existing effective-workspace-freeze machinery, not its staged/unstaged/
untracked half (that remains a distinct, already-solved concern against the
*current* workspace).

Any Resolution Delta path outside declared scope is Out-of-Scope Mutation.
An Iteration that finds it MUST be `status: failed` with
`full_review_required: true` — never `passed`; approval can only come from a
subsequent, unrestricted `initial_review`. This rule is independent of, and
fires before, the separate Convergence Limit below: a *single*
`full_review_required: true` Iteration already forbids the next Iteration
from being another `resolution_verification`.

Convergence: Core derives `consecutive_unconverged_verifications` from
`iterations` — a Reviewer-declared, evidence-backed `new_material_findings`
count (class B/C findings only; an unresolved original finding recurring, or
an unrelated latent finding, does not count) on consecutive
`resolution_verification`/`failed` entries. Any manifest-declared value is
cross-checked, never trusted; disagreement is itself a finding (this closes
the specific "resettable/manipulable counter" risk flagged during Discovery
and confirmed by an adversarial-self-check bug found and fixed during
Implementation — see `verification.md`). At the limit (2), `review.status:
passed` is blocked and no further `resolution_verification` may legally
continue the cycle; a decision record (`option` + `reason`, four fixed
options) is required before a new `initial_review` may proceed. This check
scans the full historical `iterations` array for every point the limit was
ever reached, not only the current trailing state — otherwise appending a
later `initial_review` would silently erase an earlier, never-decided
episode.

New Contract rules (C-047–C-050,
`protocol/contract/engineering.md`) bind a Change only once it opts into the
`kind` vocabulary, following the C-045/C-046 precedent CHG-0008 set for the
same shared file.

## Consequences
Resolution Verification stays adversarial and independent (every Protocol 2
Execution/Context/freeze/provenance-authority invariant applies unchanged
regardless of `kind`) while gaining a mechanically bounded scope and a
deterministic stop condition, so a Resolution → Verification cycle cannot
loop unboundedly the way `CHG-0010`'s current 5-iteration history
demonstrates it can today. `CHG-0008` and `CHG-0010` themselves — real,
already-existing manifests that declare none of the new fields — continue to
validate with zero new findings, confirmed directly (`verification.md`), not
assumed. Non-Convergence returns authority to the engineer through a
deliberately minimal, fixed-shape decision record rather than a general
Decision Gate framework, which remains explicitly future work.

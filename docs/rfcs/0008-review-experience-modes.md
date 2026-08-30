# RFC-0008 — Review Experience Modes

Status: Proposed for Protocol 2

## Summary

This RFC proposes a developer-facing UX layer on top of RFC-0007's
Review Profile model (`focused | standard | strict`): three named
**Review Experience Modes** — `Recommended` (default), `Fast`, and
`Thorough` — selectable per Change and, optionally, as a persistent
project preference. Modes never define a new review mechanism; they
are a presentation and bounded-selection layer over the effective
Review Profile that Flow, the Engineering Contract, and project
configuration already determine (C-022/C-023, RFC-0007). This RFC also
adds a schema-tracked Review phase field so Discovery, Findings,
Resolution, and Re-review are each an observable, Core-validated
state, not only prose the Harness may or may not narrate correctly.

## Motivation

RFC-0007 gave Forge a real, mechanically-differentiated review posture
per Flow, but exposed it as Protocol vocabulary a developer must
understand to reason about their own Change: `focused`/`standard`/
`strict`, Flow identifiers, and gate names. Discovery for CHG-0050
confirmed there is today (a) no function that resolves an "effective"
profile from anything but the static Flow file
(`src/forge_cli/adapters/claude_code/projection.py:92`,
`codex/projection.py:71`), (b) no schema field anywhere for a
per-Change or persistent mode preference, and (c) no live channel for
Review progress — Adapter-projected instructions are static text
generated once at `forge adapter install` time, and the only
Review-aware CLI surface, `forge change merge-check`, is a post-hoc,
two-commit diff gate with no notion of a currently active phase
(`src/forge_cli/merge_readiness/evaluator.py`). A developer stuck in a
`review -> resolution -> review` cycle today has no standing way to
ask "what mode am I in, what profile does that actually resolve to,
what phase is active, and what is left" without reading Protocol
internals.

Separately, Discovery confirmed the invariants this Change must not
touch are already solid: targeted re-review after Resolution (escalating
to a full Initial Review only on out-of-scope mutation) is already
enforced by the "FR-010 Full Review Escalation" rule in
`_validate_resolution_verification`
(`src/forge_cli/validation/__init__.py`), and the Convergence Limit
(C-049, hardcoded at 2, Core-derived) already bounds every profile
identically. This RFC does not touch either mechanism; it only makes
their outcomes legible to a developer through named modes and observable
phases.

## Decision proposed

### 1. Mode vocabulary and default

Introduce an enum `recommended | fast | thorough`, default
`recommended`, as a new optional field `review.mode` on
`forge/change@2`'s `manifest.yml` schema
(`protocol/schemas/change-v2.schema.json`). A manifest that omits it is
interpreted as `recommended` — the historically universal behavior
(no existing manifest's effective profile changes), satisfying C-045.

### 2. Mode-to-profile resolution: bounded, never below the Flow floor

Define, in `src/forge_cli/protocol_resolution/` (co-located with
`resolve_effective_flow`, since it is the natural consumer of the
Flow's canonical profile), a new function
`resolve_effective_review_profile(flow, mode, project_flow_override=None)`
built directly on RFC-0007's existing `_PROFILE_RANK`
(`{"focused": 0, "standard": 1, "strict": 2}`,
`src/forge_cli/validation/__init__.py:773`):

- Compute `floor` exactly as today: the Flow's canonical `profile`,
  raised by a project-flow override per the existing
  `_validate_review_profile_floor` invariant (never lowered — that
  path already fails closed).
- `recommended` → `floor`. No behavior changes from today.
- `fast` → `floor`. A mode can never resolve below the Flow's
  canonical floor; `fast` cannot select `focused` for a Change whose
  Flow floor is `standard` or `strict`. This is the direct, structural
  answer to the Intent's "a UI choice MUST NOT silently reduce
  Flow/Contract-required assurance" requirement — there is no code
  path by which `fast` can rank below `floor`, because the function
  only ever returns `max(floor, mode_offset)` (see `thorough` below)
  and `fast`'s offset is `0`.
- `thorough` → `min(floor + 1, "strict")` — one profile step stricter
  than the Change's own floor, capped at `strict`. This reuses exactly
  the "project MAY require a more rigorous profile than canonical
  default" allowance RFC-0007 already authorized (§8, decision point
  12), scoped to a single Change via `manifest.review.mode` instead of
  a project-wide `.forge/flows/<flow>.yml` override. A FAST Change
  set to `thorough` runs at `standard`; a STANDARD Change set to
  `thorough` runs at `strict`; a FULL Change set to `thorough` stays
  at `strict` (already the ceiling — Thorough increases rigor within
  what a profile already means, e.g. Adapter projection instructing a
  more exhaustive pass within `strict`'s existing exhaustive-search
  mandate, not a fourth profile).
- `resolve_effective_review_profile` is profile-vocabulary-only: it
  does not touch the Convergence Limit, evidence requirements,
  independence, or Finding severities — all remain unconditioned on
  mode, exactly as RFC-0007 decision point 6 already establishes for
  profile itself.

### 3. Persistent preference

Add a new, independent, optional field `review.preferred_mode`
(same enum) to `.forge/forge.yml`'s schema
(`forge/project@1`, `protocol/schemas/project.schema.json`). This is
deliberately a **new** field, not a repurposing of the existing
`review.strict` (left exactly as RFC-0007 found it — `const: true`,
untouched, still not read by any CLI code): `review.strict` predates
this RFC's mode concept and repurposing a `const`-locked field would
be a meaning change to an existing field, which C-046 requires a new
Protocol identifier for. `review.preferred_mode` only supplies the
default for `manifest.review.mode` when a new Change scaffold is
created (`forge change new`); it never overrides an already-set
per-Change `review.mode`, and it is still bounded by the same
never-below-floor rule per Change in point 2 — a project cannot use
this field to weaken any Change's floor (C-042).

### 4. Review phase: schema-tracked, Core-validated

Add `review.current_phase` to `forge/change@2`'s `manifest.yml`
schema: enum `scanning | findings_recorded | resolving | re_reviewing
| converged | stopped`, optional, defaulting to absent/`null` before a
Change's first Review Iteration begins. These machine names are
deliberately distinct from the Change-lifecycle `Discovery` Artifact
identifier (`discovery.md`, `artifacts.discovery`) to avoid colliding
Review's internal "search for findings" moment with the Change's own
Discovery stage — the two are unrelated concepts that happen to share
a natural-language word. Harness-facing and developer-facing prose
MAY still use the human labels the original request specified
(Discovery/Findings/Resolution/Re-review) for these same states; the
schema enum is the machine identifier, exactly as Flow ids
(`fast`/`standard`/`full`) already differ from their UX labels
(`Recommended`/`Fast`/`Thorough`, this RFC's own point 1).

State transitions map onto data Core already possesses or computes:
`scanning` while a Reviewer Execution is open with no recorded
iteration outcome yet; `findings_recorded` once a Review Iteration is
recorded with `status: failed` and one or more Findings;
`resolving` once a Resolution provenance record exists for the
subject revision without a corresponding new Review Iteration yet;
`re_reviewing` while a `resolution_verification` Review Iteration is
open; `converged` once `review.status: passed`; `stopped` when a
developer ends further processing while `review.status` is not
`passed` (point 6). Core validates only enum membership and that
`current_phase` is consistent with the latest recorded
`review.iterations[]` entry and `review.status` — it does not
introduce a full state-machine transition validator, keeping the
validation blast radius minimal (RFC-0007's own F-010/F-011
proportionality precedent).

### 5. Harness/Adapter projection

Extend `src/forge_cli/adapters/claude_code/projection.py` and
`codex/projection.py` to read `manifest.review.mode` and
`manifest.review.current_phase` (when present) alongside the Flow's
static `profile`, and to project, per Flow, mode-aware instruction
text analogous to the existing shared
`REVIEW_PROFILE_INSTRUCTION` dict in
`src/forge_cli/adapters/review_independence.py`: what the resolved
mode/profile pairing means, what phase is current, and what a
"targeted re-review by default" outcome looks like versus a full
Initial Review escalation (reusing FR-010's existing trigger
condition verbatim — Adapter prose explains it, Core still decides
it). The independence and convergence instruction blocks remain
byte-for-byte shared and mode-invariant, per RFC-0007 decision point
6.

### 6. CLI surface

Add `forge change review-status {slug}` (new subcommand under
`change_cli.py`, alongside the existing `new`/`merge-check`): reads
the Change's `manifest.yml` and prints selected mode, resolved
effective profile, current phase, outstanding Finding counts by
severity, and the "next step" derived directly from the same data
`forge change merge-check` already reads (`ready`/`blocked` verdict,
`MR-xxx` diagnostics) plus the new `current_phase` field. This is a
read-only, local, Git-native command — no new remote dependency
(C-038).

### 7. Stopping without a false success claim

No new mechanism is introduced for this. Completion already cannot be
claimed while `review.status` is not `passed` (C-035); a developer who
stops mid-Review leaves `manifest.review.current_phase` at whatever
real state it last reached (`findings_recorded`, `resolving`, or
`stopped` if recorded explicitly) and `review.status` unresolved or
`failed`. This is already an honest representation under existing
Core invariants — CHG-0050's job (points 4-6 above) is to make that
state visible to the developer, not to invent a new terminal state.
`stopped` (point 4) is available for a developer to record explicitly
that they are ending further processing for now; it carries no
authority to mark `review.status: passed` and does not interact with
the Convergence Limit's own existing `abort_or_supersede` option
(C-049), which remains the correct choice specifically at the
Convergence Limit boundary.

### 8. Any Forge-enabled repository

Nothing in points 1-7 references `forge-protocol`'s own structure;
`resolve_effective_review_profile` takes `flow`/`mode`/override data
exactly as `resolve_effective_flow` already does today, parametrized
by `project_root`. No new capability is required for this to work in
a fresh Forge-enabled repository with only canonical Flow files and no
project overrides — `recommended` degrades to exactly today's
behavior in that case.

## Non-goals and safeguards

This RFC does not authorize:

- a fourth Review Profile, or any profile value outside
  `focused | standard | strict` (RFC-0007's own enum is unchanged);
- any path by which `manifest.review.mode` can resolve to a profile
  ranked below the Change's Flow-derived floor;
- weakening Reviewer/Resolver independence, evidence requirements,
  Finding severities, the Convergence Limit, or Resolution
  Verification scoping (C-026, C-025, C-027, C-047-C-050), for any
  mode;
- a `stopped` phase that satisfies Completion or substitutes for
  `review.status: passed`;
- a project's `review.preferred_mode` overriding an explicit
  per-Change `review.mode`, or lowering any Change's floor (C-042).

## Alternatives rejected

### Let mode directly set profile, unconstrained

Rejected: this would let `fast` select `focused` under a `strict`
floor, a silent reduction of Flow/Contract-required assurance by UI
choice — exactly what the originating request's own requirements
forbid, and what C-042 already forbids for project configuration in
general.

### Projection-only phase observability (no schema field)

Considered and rejected during Discovery (CHG-0050's Open Question
OQ-2, resolved with the human maintainer in the active chat session on
2026-08-30): narration-only observability cannot be verified by Core,
would need a new Harness-honesty Contract clause analogous to
C-072/C-073 to say so explicitly, and gives materially weaker
assurance than a schema-tracked field for comparable cost. Rejected in
favor of point 4.

### Repurpose `.forge/forge.yml`'s existing `review.strict` field

Rejected: it is `const: true`, and changing an existing required
field's meaning requires a new Protocol identifier under C-046. A new,
independent field (point 3) is additive and Protocol-2-compatible
under C-045.

## Compatibility and consequences

All schema changes are additive, optional, and defaulted:
`review.mode` defaults to `recommended` (today's behavior, unchanged),
`review.current_phase` defaults to absent, and `review.preferred_mode`
is a new optional project field with no effect unless set. No existing
`forge/change@2` manifest or `forge/project@1` project file becomes
invalid, and no historical Change's recorded Review is reinterpreted —
satisfying C-045. `protocol/schemas/policy-review.schema.json`
(Protocol 1) is untouched, consistent with RFC-0007's own scoping of
this vocabulary to Protocol 2. No Engineering Contract clause requires
new or amended text: the never-below-floor guarantee is a direct,
structural consequence of `resolve_effective_review_profile`'s own
definition (point 2), not a new invariant needing its own Contract
rule, and C-042 already covers a project preference never weakening a
Change's floor.

## Acceptance record

Proposed in this active chat session on 2026-08-30, following
CHG-0048/RFC-0007's precedent of proposal and acceptance as the human
maintainer's explicit act. The maintainer's resolution of Discovery's
OQ-2 (schema-tracked phase observability, point 4) is recorded here
and in `.forge/changes/CHG-0050-review-experience-modes/discovery.md`
as the RFC's own accepted design point, decided before this RFC's text
was finalized.

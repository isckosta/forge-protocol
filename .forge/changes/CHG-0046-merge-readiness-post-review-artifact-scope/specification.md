---
forge:
  artifact: specification
  schema: 1
change: CHG-0046
status: pending
---

# CHG-0046 · Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0046 |
| **Flow** | FULL |
| **Status** | Draft |

## Summary

`forge change merge-check` (the `forge-merge-readiness` CI gate) must stop
flagging MR-015 (`REVIEW SUBJECT STALE`) against a Change whose only
post-Review-freeze commits are Change-local artifacts belonging to Flow
stages that canonically run after `strict_review`, while continuing,
without regression, to flag MR-015 against any Change whose actual
implementation or pre-Review artifacts change after the freeze. Separately,
the materiality policy the gate loads must resolve the ten Agent
Adapter–generated paths identified in Discovery to a definite `material` or
`non_material` classification instead of `ambiguous` (MR-017), without
loosening the classifier's fail-closed default for any other path.

## Classification

**Flow: FULL.** This Change modifies `src/forge_cli/merge_readiness/evaluator.py`
and `protocol/policies/merge-readiness.yml` — the mechanical enforcement of
the Reviewer/Resolver independence invariant (C-026) that gates every
Change's mergeability in this repository, including this one's own.
CHG-0036, which originally built this gate, used FULL for the same reason;
this Change follows that precedent. A mistake here does not just affect one
Change's outcome, it can silently weaken (or wrongly tighten) the integrity
guarantee every future Change's merge depends on — the disqualifier profile
`fast.yml` describes (`security_model_change`, `significant_cross_module_change`)
applies directly, and STANDARD carries no explicit classification criteria
to justify a lower bar for security/integrity-adjacent tooling.

## Functional Requirements

### FR-001 · MR-015 tolerates post-freeze Change-local artifacts once the Change is Complete
Origin: Discovery, "MR-015: the CI gate and `forge validate` implement the
same invariant, and disagree"; corrected by Specification Review SR-001
(a per-Flow-stage artifact mapping cannot cover `tasks.md`, which is a
continuously-updated checklist not tied to one stage, or
`specification-drift.md`, which `protocol/artifact-structure.md:436-441`
documents as having no Flow stage or code representation at all).
Priority: must

#### Requirement
For a Change whose Review subject was frozen at commit `S`, MR-015 MUST NOT
report `REVIEW SUBJECT STALE` solely because commits after `S` modify
Change-local paths (inside the Change's own `.forge/changes/CHG-xxxx-*/`
directory) once that Change's `manifest.yml: state.current` is `complete`
at `head_revision`.

#### Expected Behavior
This mirrors `forge validate`'s own already-shipped implementation of the
same invariant (`validation/__init__.py:375`,
`st.get("current")!="complete"`): staleness is enforced continuously while
a Change is still in progress, and stops being re-checked once it has
reached its terminal `complete` state — which is only reachable after
MR-005 and MR-016 independently confirm `state.current == complete` and
that `verification.md`/`review.md`/`provenance.yml` actually exist as
committed evidence. `state.current` is not the sole guard; it is
corroborated by those checks (CON-002).

#### Boundary
This requirement governs only Change-local paths inside the Change's own
directory. It does not extend the tolerance to any path outside that
directory (AC-002), and it does not apply while the Change has not yet
reached `state.current: complete` (AC-003) — during that window, MR-015
must keep enforcing exactly as it does today.

#### Acceptance
AC-001
Given a Change whose Review subject is frozen at commit `S`, and whose
`manifest.yml: state.current` is `complete` at `head_revision`
When commits after `S` modify any Change-local path (e.g.
`knowledge-capture.md`, `specification-drift.md`, `tasks.md`, in addition
to the already-allowed `manifest.yml`/`provenance.yml`/`review.md`)
Then MR-015 does not fire.

AC-002
Given the same Change and frozen commit `S`
When a commit after `S` modifies a file outside the Change's own directory
(e.g. `src/forge_cli/...`), regardless of `state.current`
Then MR-015 still fires — no regression in the invariant CHG-0036 shipped
this check to enforce.

AC-003
Given a Change whose Review subject is frozen at commit `S`, whose
`manifest.yml: state.current` at `head_revision` is **not** `complete`
(e.g. still `review` or `documentation`)
When a commit after `S` modifies any Change-local path outside
`manifest.yml`/`provenance.yml`/`review.md`
Then MR-015 still fires — the tolerance in AC-001 is bounded by reaching
Completion, not granted unconditionally to every Change-local path at
every point in its lifecycle.

### FR-002 · Agent Adapter–generated paths resolve to a definite classification
Origin: Discovery, "MR-017: ten Adapter-generated paths have no
classification rule"
Priority: must

#### Requirement
`classify_path()` MUST resolve each of the ten paths identified in
Discovery — `.claude/CLAUDE.md`, `.claude/skills/forge/**`,
`.agents/skills/forge/**`, `.forge/adapters/*/installation.yml` — to
`material` or `non_material`, never `ambiguous`.

#### Expected Behavior
The classification chosen for each path family must be consistent with
what that path actually is: fully generated, digest-tracked Adapter output
whose drift is already independently detected by `forge doctor` /
`forge adapter doctor` is a different kind of change than hand-authored
source, and the policy's classification should say so explicitly rather
than defaulting to `ambiguous` for lack of a rule.

#### Boundary
This requirement resolves only the ten specific paths Discovery identified
as currently ambiguous and material to CHG-0045's PR. It does not require
auditing or reclassifying any path the policy already resolves to
`material`, `permitted`, or `change`.

#### Acceptance
AC-004
Given each of the ten paths identified in Discovery
When `classify_path()` evaluates it against the updated policy
Then it returns `material` or `non_material`, never `ambiguous`.

AC-005
Given a path not in the ten identified paths and not already matched by an
existing policy rule
When `classify_path()` evaluates it
Then it still returns `ambiguous` — the fix adds specific, scoped rules; it
does not loosen the classifier's fail-closed fallback for anything else.

## Non-functional Requirements

None. This Change alters gate logic and policy data only; it introduces no
new runtime behavior with performance, availability, or scalability
properties distinct from what `forge change merge-check` already does.

## Constraints

### CON-001
This Change MUST NOT alter the meaning of C-026 (Reviewer/Resolver
independence) or any other Engineering Contract invariant — only how
MR-015/MR-017 mechanically *detect* conformance to invariants that remain
exactly as defined in `protocol/contract/engineering.md`. No Contract edit
is in scope.

### CON-002
`state.current` MAY be consulted by MR-015 (FR-001 requires it), but it
MUST NOT become the *sole* safeguard: this Change must not remove or
weaken MR-005 (`COMPLETION NOT READY` unless `state.current == complete`)
or MR-016 (Completion requires `verification.md`/`review.md`/
`provenance.yml` to actually exist as committed evidence at
`head_revision`) — the checks that make `state.current: complete` a
corroborated claim rather than bare self-attestation. This is narrower
than this Constraint's original wording (revised by Specification Review
SR-002), which would have ruled out consulting `state.current` at all and,
with it, the only design SR-001 found to actually match Discovery's
evidence. This still honors the underlying concern in
[[project-merge-readiness-scoping-bug]] finding 6 — a status field trusted
with *no* corroboration anywhere — by requiring the corroboration to stay
in place, not by forbidding the field.

### CON-003
Both fixes apply identically across `fast`, `standard`, and `full` Flows —
this Change must not special-case FULL; the false positive Discovery found
is a property of every canonical Flow's stage ordering, not of FULL's
extra stages specifically.

## Traceability Matrix

| Requirement | Discovery Finding | Acceptance |
|---|---|---|
| FR-001 | MR-015 allowed-file set vs. Flow stage order (evaluator.py:132-146 vs. protocol/flows/*.yml) | AC-001, AC-002, AC-003 |
| FR-002 | MR-017 policy gap (policy.py:29-43, protocol/policies/merge-readiness.yml) | AC-004, AC-005 |

## Compatibility Statement

No Protocol version change (C-046 preserved — this is Adapter/CLI-internal
gate logic, not a Protocol-schema or Contract change). No change to any
`.forge/changes/*` artifact schema. Existing passing merge-readiness
behavior for every other MR-xxx check is unaffected; only MR-015's
allowed-file computation and the materiality policy's prefix/path tables
change. Changes already merged to `main` are unaffected retroactively —
this Change only affects future `forge change merge-check` evaluations,
including of CHG-0045's still-open PR #36.

## Specification Gate

Requirements are independently derived from Discovery's direct code and
Git evidence (file/line citations, reproduced CLI output, byte-identical
provenance excerpts), not from assumption. AC-001/AC-002/AC-003 together
specify both the fix (tolerate post-Review-stage artifacts) and its
regression boundary (implementation and pre-Review artifacts remain
protected) as equally load-bearing, verifiable conditions — this
Specification does not describe only the happy path. Ready for adversarial
Specification Review.

## Out of Scope

- MR-006 and MR-008: confirmed in Discovery as genuine CHG-0045 provenance
  gaps, not gate defects. Not addressed by any requirement here.
- Any other deferred merge-readiness finding on record
  ([[project-merge-readiness-scoping-bug]]).
- Redesigning the materiality policy's schema, or reclassifying any path
  the policy does not currently resolve to `ambiguous`.

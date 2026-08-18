---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0013
status: approved
---

# Test Strategy — CHG-0013

Test level: unit, against `_validate_unresolved_decisions` and
`validate_project`, following the existing style in
`tests/unit/test_validation.py` and `tests/cli/test_review_iteration_history.py`
(`tmp_path`-based fixture manifests; no live Git history dependency, unlike
CHG-0011's Resolution Delta machinery — this mechanism is manifest-shape-only
and does not need commit history, which keeps it simpler and fully covered
by pure-YAML fixtures).

## TDD-001 — legacy manifests are unaffected (regression baseline, RED first)

Load every real manifest in `.forge/changes/CHG-0001`..`CHG-0012` (none
declares `decisions`) through `_validate_unresolved_decisions` directly.
Expect zero findings from this function specifically, for all twelve. This
is the compatibility invariant as an executable test, not just an
architectural claim.

## TDD-002 — golden path: resolved material decision does not block

A `decisions[]` entry with `status: resolved`, `resolved_via: human_decision`,
`materiality: material`, `owning_artifact: specification`, alongside
`artifacts.specification_review: complete` and `review.status: passed`.
Expect zero findings.

## TDD-003 — Open-blocking status conflicts with an already-passed Gate (AC-010, INV-001)

Same shape as TDD-002 but `status: awaiting_decision`. Expect exactly one
finding naming the Gate/artifact conflict. Repeat for `status: open` and
`status: analyzing` (three sub-cases, one assertion each).

## TDD-004 — resolved and superseded entries never block (specification-review regression)

A `superseded` entry (the exact case Adversarial Specification Review
caught in `specification-review.md`) alongside the same passed-Gate state as
TDD-003. Expect zero findings — this is the regression test for the fix
that was made to FR-013/INV-001 before Architecture, so it must exist even
though the defect was caught before any code was written.

## TDD-005 — human-authority Decision cannot be resolved autonomously (AC-009, C-055)

`authority: human`, `status: resolved`, `resolved_via: autonomous_decision`.
Expect exactly one finding. Repeat with `resolved_via: evidence` — Evidence
Resolution is allowed for `human`-authority Decisions (INV-002 does not
depend on Authority), so this sub-case expects zero findings, contrasting
directly with the `autonomous_decision` sub-case to prove the check is
authority-specific, not blanket.

## TDD-006 — resolved without resolved_via, or resolved_via without resolved (FR-009)

Two sub-cases: `status: resolved` with `resolved_via: null`; and
`status: awaiting_decision` with `resolved_via: human_decision` set. Both
are findings — a Decision cannot be resolved by nothing, and cannot be
non-resolved while claiming a resolution method.

## TDD-007 — malformed enum values (shape validation)

Adversarial matrix, one assertion per malformed field: `class: "product "`
(trailing space), `class: "PRODUCT"` (wrong case), `materiality: true`
(boolean, not the string enum), `status: "done"` (not a Lifecycle state),
`authority: "ai"` (not an Authority value), `id: "DEC-1"` (fails the
`^DEC-[0-9]{3,}$` pattern). Each expects exactly one finding and MUST NOT
raise an unhandled exception — mirroring `_record_fields`'s defensive
`isinstance` style throughout `validation/__init__.py`.

## TDD-008 — duplicate Decision id

Two entries sharing `id: DEC-001`. Expect exactly one finding naming the
duplication (mirrors the existing duplicate-record-id check pattern already
used for provenance records in `_validate_protocol2_review_provenance`).

## TDD-009 — owning_artifact inconsistent with Class (INV-003)

`class: product`, `owning_artifact: tasks`. Expect exactly one finding
citing the static Class→Owning-Artifact table. Also cover the reverse
direction, `class: technical`, `owning_artifact: specification` (over-
escalating a technical question to look like a product one to obtain
`human` authority by misdirection) — same finding class, proving the check
is symmetric, not just "downstream too late."

## TDD-010 — invalidates referencing an artifact that never transitioned (C-057, AC-006)

`decisions[]` entry `resolved`, `invalidates: [tasks]`,
`artifacts.tasks: complete` (never moved through `invalidated`). Expect
exactly one finding. Positive counterpart: same shape but
`artifacts.tasks: invalidated` — expect zero findings from this specific
check (the artifact correctly reflects the pending revisit).

## TDD-011 — non-material entries never block or fail shape checks strictly (C-058)

A `materiality: non_material` entry with `status: open`,
`owning_artifact: specification`, alongside a passed
`specification_review`. Expect zero Gate-blocking findings — Materiality
gates whether an entry participates in blocking at all, independent of
status. (Shape validation, TDD-007/008, still applies regardless of
Materiality — a malformed non-material entry is still malformed.)

## TDD-012 — absence of `decisions` entirely (compatibility, distinct from TDD-001)

`manifest.get("decisions")` is `None`, and separately `[]` (empty list) —
both must short-circuit to zero findings without attempting field access on
any entry, proving the compatibility guard is a true early return, not an
accidental pass caused by an empty-iteration loop that would break the
moment a non-empty list appears with a genuine defect.

## Verification

`pytest -q`, `forge validate` from the repository root (must show only the
one pre-existing, unrelated finding — if any — that already exists on clean
`main`, exactly matching the CHG-0011 precedent for verifying no regression
was introduced), `forge doctor`.

---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0036
status: complete
---

# Test Strategy — CHG-0036 Merge Readiness Gate

## Objective

Demonstrate that Merge Readiness is a deterministic, fail-closed evaluation
of canonical evidence and is not equivalent to `forge validate`, manifest
claims, or generic CI success.

## Strategy

Use isolated temporary Git repositories with complete and intentionally
shallow histories, canonical Flow fixtures, and repository-native Change
artifacts. Test pure path/policy/result code independently, then exercise the
CLI and workflow contract. Every executable behavior begins with a real RED
test and records its expected failure before implementation.

## TDD-001 — Readiness verdict and exit codes

RED: a ready fixture has no evaluator or CLI command and the focused test
fails. GREEN: the evaluator returns ready and the CLI maps ready/blocked/
operational outcomes to 0/1/2. REFACTOR: preserve deterministic output and
existing `forge validate` exit behavior.

## TDD-002 — Diff-based Change resolution

Cover material diff with one Change, multiple Changes, no Change, rename,
deletion, malformed directory, contradictory manifest ID, ambiguous path,
explicit base/head, missing history, and shallow clone. Verify all affected
Changes are evaluated conjunctively.

## TDD-003 — Materiality policy

Cover Protocol, schema, runtime, Adapter, test, workflow, normative
documentation, permitted explanatory documentation, symlink, and ambiguous
policy paths. Verify no hard-coded path list is duplicated in evaluator or
CLI.

## TDD-004 — Evidence recomputation

Cover FAST, STANDARD, and FULL ready fixtures plus pending Verification,
failed Verification, incomplete TDD, invalid exception, missing artifacts,
open Decisions, and Completion claims contradicted by evidence.

## TDD-005 — Plan digest authority

Cover valid C-077 approval, changed Plan content, malformed digest, missing
historical approval, duplicate/ambiguous approval, self-observed evidence,
and historical compatibility. Editing only `manifest.yml` must never create
readiness.

## TDD-006 — Review, Resolution, and subject binding

Cover pending/failed Review, stale Review subject, unavailable subject,
shared execution/context, fake reviewer provenance, unresolved BLOCKER and
MAJOR, permitted MINOR/OBSERVATION behavior, invalid Resolution Verification,
missing re-review, and material post-review changes.

## TDD-007 — CI and diagnostics

Cover explicit PR base/head environment, full-history checkout, deterministic
diagnostic ordering, stable `MR-xxx` codes, human output, and independent
release provenance workflow behavior.

## Non-mechanical Validation

Review the materiality policy and branch-protection documentation for honest
scope. Confirm Harness guidance says to run the check but does not claim to
enforce it. Confirm the RFC, Protocol 1 compatibility statement, and release
provenance boundary remain consistent.

## Completion Criteria

All TDD cases pass, the full repository suite passes, `forge validate` passes,
the required CI workflow runs with complete history, and independent Strict
Review verifies the frozen implementation subject and all review-control
metadata boundaries.

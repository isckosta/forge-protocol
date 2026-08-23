---
forge:
  artifact: plan
  schema: 1
change: CHG-0036
status: approved
---

# Plan — CHG-0036 Merge Readiness Gate

1. Record and validate the accepted RFC-0006 content-digest decision in the
   Protocol Contract, Protocol 2 resources, schemas, and compatibility
   documentation; preserve Protocol 1 historical validity.
2. Add the centralized materiality policy and its deterministic loader under
   the canonical Protocol resources; test material, permitted, and ambiguous
   path categories.
3. Create the reusable `src/forge_cli/merge_readiness/` models, diagnostics,
   Change-resolution, policy, evidence, and evaluator modules. Reuse
   `protocol_resolution` and existing validation authorities rather than
   duplicating Flow semantics.
4. Add RED-first unit and integration tests covering all TDD-001 through
   TDD-007 cases, including multiple Changes, stale Plan digests, review
   subjects, malformed provenance, shallow history, symlinks, deletions, and
   manifest-only tampering.
5. Add `forge change merge-check` with explicit `--base` and `--head`,
   deterministic human/structured diagnostics, and exit codes 0 ready, 1
   blocked, and 2 operational/configuration failure without changing
   `forge validate`.
6. Add the GitHub workflow required-check wiring with `fetch-depth: 0` and
   explicit Pull Request base/head SHAs; document required branch protection
   and the external enforcement boundary.
7. Update only affected README, contributor, releasing, and Codex/Claude
   guidance; keep release provenance checks separate and label Harness advice
   as guidance.
8. Run focused tests, full pytest, `forge validate`, `forge doctor`, CI
   workflow checks, Verification, independent Strict Review, Resolution if
   needed, and Completion evidence after freezing the final subject.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

The accepted RFC and Architecture constrain implementation to an immutable
content-digest Plan binding, a separate readiness evaluator, and the existing
effective Flow/validation authorities. Implementation-time discoveries must
be recorded in Verification, a Decision, or a documented re-Plan rather than
silently changing this list.

## Human Plan Authorization

This Plan is prepared but not authorized. The C-077 human Decision,
`forge:plan-approval-confirmation`, `forge:plan-approval-record`, and
corresponding provenance record must be added only after an explicit human
confirmation. Until then, no Implementation or TDD GREEN work may begin.

<!-- forge:plan-approval-confirmation -->

This Plan is explicitly authorized by the human maintainer to proceed to
Implementation.

<!-- forge:plan-approval-record -->

**Approval record.** Explicit human approval was received from the user as
“Sim” in the active session on 2026-08-23. This confirmation authorizes the
recorded Plan decision and continuation under C-077.

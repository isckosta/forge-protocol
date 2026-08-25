---
forge:
  artifact: intent
  schema: 1
change: CHG-0046
status: complete
---

# CHG-0046 · Merge Readiness Post Review Artifact Scope

> **Change Intent**
>
> Fix two real defects in the `forge-merge-readiness` gate (`src/forge_cli/merge_readiness/evaluator.py`): the post-Review-freeze allowed-file set for MR-015/MR-006 does not account for canonical Flow stages (`documentation`, `knowledge_capture`, `completion`) that legitimately run and write Change-local artifacts *after* `strict_review` in every Flow's own stage order, and the materiality policy classifies a fixed set of Agent Adapter–generated paths as `ambiguous` (MR-017), permanently blocking any PR that touches them.

## Overview
| | |
|---|---|
| **Change** | CHG-0046 |
| **Flow** | FULL |
| **Status** | Complete |

## Problem

CHG-0045's PR (#36) legitimately passed Strict Review (iteration 3, 0
blockers/majors/minors) and reached `state.current: complete`, yet the
`forge-merge-readiness` CI gate reports `MERGE BLOCKED` against it. Reproducing
`forge change merge-check` locally isolates two independent, pre-existing
defects in the gate itself, not in CHG-0045:

1. **MR-015 (`REVIEW SUBJECT STALE`) / MR-006 (verification not bound).**
   `_check_change()` (`evaluator.py:132-146`) diffs `subject_commit..head_revision`
   scoped to the Change's own directory and only tolerates
   `manifest.yml`/`provenance.yml`/`review.md` differing after the frozen
   subject commit. But every canonical Flow (`protocol/flows/*.yml`) places
   `documentation`, `knowledge_capture`, and `completion` *after*
   `strict_review` in its own `stages` list — meaning the Change-local
   artifacts those stages legitimately produce (`documentation.md` /
   `specification-drift.md`, `knowledge-capture.md`, and any Completion-time
   corrections to `verification.md`/`tasks.md`) are written, by design, after
   the Review subject is frozen. The gate currently treats every one of those
   as post-freeze contamination of the reviewed subject, which is a false
   positive baked into the check's own allowed-file set, not a violation of
   the actual Reviewer/Resolver independence invariant (C-026) the freeze
   exists to protect — that invariant is about the *implementation* under
   review, not about downstream bookkeeping stages the Flow itself schedules
   after Review.
2. **MR-017 (ambiguous materiality classification).** Ten paths generated or
   maintained by the Claude Code / Codex Agent Adapters (`.claude/CLAUDE.md`,
   `.agents/skills/forge/**`, `.claude/skills/forge/**`,
   `.forge/adapters/*/installation.yml`) are classified `ambiguous` by the
   materiality policy the gate loads (`load_materiality_policy()`). Any PR
   that touches them — which any Adapter-projection Change, including
   CHG-0045, necessarily does — is unconditionally blocked by MR-017
   regardless of Review or Verification status.

Both defects mean a Change can do everything the Engineering Contract asks
of it — pass Strict Review, pass Verification, complete Documentation
Impact and Knowledge Capture in the order the Flow itself prescribes — and
still be mechanically unable to merge. That is the opposite of what a merge
readiness gate is for.

## Goal

1. `_check_change()`'s post-freeze allowed-file computation for MR-015 must be
   derived from which canonical Flow stages are defined to run after
   `strict_review` (per the Change's own effective Flow), not from a fixed
   three-file literal — so a Change that writes `documentation`/
   `knowledge_capture`/`completion`-stage artifacts after its Review subject
   is frozen is not flagged as stale for doing exactly what its Flow
   requires.
2. MR-006's verification-binding check must keep working against whichever
   commit the gate now accepts as the frozen subject once (1) is fixed — a
   Change must still be rejected if its actual implementation changed after
   Review, only no longer rejected for legitimate post-Review bookkeeping.
3. The materiality policy must stop classifying the ten currently-ambiguous
   Adapter-generated paths as `ambiguous`; each must resolve to a definite
   `material` or `non_material` classification consistent with how the rest
   of the policy already treats generated, drift-checked Adapter output.
4. Preserve, without weakening, the actual invariant MR-015/MR-006 exist to
   enforce: a Change whose *implementation* changes after its Review subject
   is frozen (not just its Documentation/Knowledge Capture/Completion
   artifacts) must still be flagged stale.

## Scope

- The `forge-merge-readiness` gate's evaluation logic
  (`src/forge_cli/merge_readiness/evaluator.py`), specifically the MR-015,
  MR-006, and MR-017 checks.
- The materiality policy the gate loads (`load_materiality_policy()` and its
  backing configuration) to the extent needed to resolve the ten currently
  `ambiguous` Adapter-generated paths.
- Test coverage for both fixes, including a regression test reproducing the
  exact CHG-0045/PR-#36 false-positive scenario (Review frozen, then
  Documentation/Knowledge Capture/Completion artifacts committed) and a
  regression test proving the freeze invariant still fires when the
  *implementation* changes post-freeze.

## Out of Scope

- CHG-0045's own missing `source.content_digest` on its
  `plan-approval-001` provenance record (MR-008). That is a genuine gap in
  CHG-0045's own bookkeeping, not a gate defect, and `provenance.yml` is
  already in the allowed post-freeze exception set — it is corrected
  directly on CHG-0045's own branch, independent of this Change.
  This Change does not merge CHG-0045's PR #36; it only removes the gate
  defects blocking it, so an accurate merge-readiness evaluation of
  CHG-0045 can be reached on its own subsequent merits.
- Any other deferred merge-readiness finding already on record
  ([[project-merge-readiness-scoping-bug]]): TDD evidence trusted from the
  manifest without checking `tdd-evidence.yml`'s actual cycles; the Plan
  digest check only running when `artifacts.plan == "approved"`; and
  deleted/renamed Change directories breaking manifest resolution. None of
  these block CHG-0045 today; they are not touched here.
- Redesigning the materiality policy's schema or classification model in
  general — only resolving the ten specific ambiguous paths this Change
  found.

## Success Criteria

- `forge change merge-check` run against CHG-0045's actual PR #36
  base/head commits reports `MERGE READY` (modulo the separately-fixed
  MR-008 provenance gap, out of scope here) once this Change lands and
  CHG-0045's branch is rebased onto it.
- A Change that legitimately writes Documentation/Knowledge Capture/
  Completion artifacts after its Review subject is frozen is never flagged
  MR-015/MR-006-stale for that alone.
- A Change whose implementation genuinely changes after its Review subject
  is frozen is still, correctly, flagged MR-015-stale — no regression in
  the invariant CHG-0036 originally shipped this check to enforce.
- None of the ten currently-ambiguous Adapter-generated paths trigger
  MR-017 anymore.

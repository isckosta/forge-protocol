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
> Fix two real defects in the `forge-merge-readiness` gate (`src/forge_cli/merge_readiness/evaluator.py`): the MR-015 post-Review-freeze allowed-file set does not account for canonical Flow stages (`documentation`, `knowledge_capture`, `completion`) that legitimately run and write Change-local artifacts *after* `strict_review` in every Flow's own stage order, and the materiality policy classifies a fixed set of Agent Adapter–generated paths as `ambiguous` (MR-017), permanently blocking any PR that touches them.

## Overview
| | |
|---|---|
| **Change** | CHG-0046 |
| **Flow** | FULL |
| **Status** | Complete |

## Problem

CHG-0045's PR (#36) legitimately passed Strict Review (iteration 3, 0
blockers/majors/minors) and reached `state.current: complete`, yet the
`forge-merge-readiness` CI gate reports `MERGE BLOCKED` against it.
Reproducing `forge change merge-check` locally against PR #36's actual
base/head commits surfaces four findings. Two are real, pre-existing
defects in the gate itself; two are genuine, unrelated gaps in CHG-0045's
own provenance bookkeeping that the gate is correctly catching. This
Change addresses only the former.

1. **MR-015 (`REVIEW SUBJECT STALE`) — gate defect.** `_check_change()`
   (`evaluator.py:132-146`) diffs `subject_commit..head_revision` scoped to
   the Change's own directory and only tolerates `manifest.yml` /
   `provenance.yml` / `review.md` differing after the frozen subject
   commit. But every canonical Flow (`protocol/flows/*.yml`) places
   `documentation`, `knowledge_capture`, and `completion` *after*
   `strict_review` in its own `stages` list — meaning the Change-local
   artifacts those stages legitimately produce (`specification-drift.md`,
   `knowledge-capture.md`, and Completion-time updates to `tasks.md`) are
   written, by design, after the Review subject is frozen. CHG-0045's own
   `tasks.md` (T-023) independently rediscovered a neighboring instance of
   this same mechanism firing — for `.claude/CLAUDE.md` and
   `.playwright-mcp/`, paths genuinely outside the Change directory — and,
   reasonably, read that as "mechanical protection working as designed."
   It is, for those two paths. It is not for the four Change-local,
   stage-scheduled artifacts the same freeze diff also flags. `forge
   validate`'s own local implementation of the same invariant
   (`validation/__init__.py:375`, `_changed()`) already encodes this
   distinction by only checking staleness `and st.get("current")!="complete"`
   — it stops enforcing once a Change reaches `state.current: complete`,
   which is exactly when Documentation/Knowledge Capture/Completion-stage
   writes are expected to have already landed. `evaluator.py`'s MR-015 has
   no equivalent carve-out, so the CI gate and the local validator now
   disagree about the same invariant on the same repository state — CI's
   own "Validate Forge repository" step passes ("Forge project is valid")
   on the exact commit its own next step, "Evaluate Forge Merge Readiness,"
   rejects as stale.
2. **MR-017 (ambiguous materiality classification) — gate defect.** Ten
   paths generated or maintained by the Claude Code / Codex Agent Adapters
   (`.claude/CLAUDE.md`, `.agents/skills/forge/**`,
   `.claude/skills/forge/**`, `.forge/adapters/*/installation.yml`) fall
   through every rule in `classify_path()` (`policy.py:29-43`) — they match
   none of `protocol/policies/merge-readiness.yml`'s `material_prefixes`
   (`.github/workflows/`, `protocol/`, `src/`, `tests/`, `adapters/`) or
   `permitted_prefixes` (`docs/`, `examples/`) — and land on the function's
   final, unconditional `return "ambiguous"`. Any PR that touches them,
   which any Adapter-projection Change (including CHG-0045) necessarily
   does, is unconditionally blocked by MR-017 regardless of Review or
   Verification status.
3. **MR-006 (verification not bound to immutable subject) — genuine
   CHG-0045 gap, not a gate defect.** The only `role: implementation,
   source.reference: verification.md` provenance record CHG-0045 recorded
   (`implementation-subject-001`) is bound to `23d763b`, the *original*
   pre-Resolution implementation commit — never to `95b521e`
   (resolution-002), the commit the final passed Review iteration actually
   reviewed. CHG-0043's own provenance.yml (`verification-001`,
   `-002`, `-003`, each re-bound to its own Resolution's subject commit) is
   the established, working precedent for re-recording verification
   provenance after every Resolution; CHG-0045 did not follow it. Fixing
   MR-015 does not fix this — MR-006 is independent of the allowed-file-set
   bug and is correctly flagging a real absence of evidence.
4. **MR-008 (`PLAN AUTHORIZATION STALE`) — genuine CHG-0045 gap, not a
   gate defect.** `plan-approval-001`'s `source` never recorded a
   `content_digest` for `plan.md`, so `digest` never resolves to a string
   and the check fails closed (`evaluator.py:289`). This is a missing field
   in one provenance record, not gate logic.

Findings 1-2 mean a Change can do everything the Engineering Contract asks
of it — pass Strict Review, pass Verification, complete Documentation
Impact and Knowledge Capture in the order the Flow itself prescribes — and
still be mechanically unable to merge. That is the opposite of what a merge
readiness gate is for. Findings 3-4 are real defects too, just not in this
gate — they belong to CHG-0045's own bookkeeping, correctable directly on
its branch since `provenance.yml` is already in the allowed post-freeze
set.

## Goal

1. `_check_change()`'s post-freeze allowed-file computation for MR-015 must
   be derived from which canonical Flow stages are defined to run after
   `strict_review` (per the Change's own effective Flow), not from a fixed
   three-file literal — so a Change that writes `documentation` /
   `knowledge_capture` / `completion`-stage artifacts after its Review
   subject is frozen is not flagged as stale for doing exactly what its
   Flow requires.
2. Preserve, without weakening, the actual invariant MR-015 exists to
   enforce: a Change whose *implementation* changes after its Review
   subject is frozen must still be flagged stale. Resolve, deliberately, how
   (1) and (2) coexist — e.g. whether to mirror `forge validate`'s existing
   `state.current != "complete"` carve-out, derive an explicit allowed-path
   set from stage-to-artifact mapping, or another approach — as an
   Architecture decision, not an implicit side effect.
3. The materiality policy must stop classifying the ten currently-ambiguous
   Adapter-generated paths as `ambiguous`; each must resolve to a definite
   `material` or `non_material` classification consistent with how the rest
   of the policy already treats generated, drift-checked Adapter output.

## Scope

- The `forge-merge-readiness` gate's MR-015 check
  (`src/forge_cli/merge_readiness/evaluator.py`).
- The materiality policy the gate loads (`load_materiality_policy()` and its
  backing configuration, `protocol/policies/merge-readiness.yml`) to the
  extent needed to resolve the ten currently `ambiguous` Adapter-generated
  paths.
- Test coverage for both fixes, including a regression test reproducing the
  exact CHG-0045/PR-#36 false-positive scenario (Review frozen, then
  Documentation/Knowledge Capture/Completion artifacts committed while
  `state.current` reaches `complete`) and a regression test proving MR-015
  still fires for the same kind of Change-local, pre-Completion edit it
  flags today when the Change has *not yet* reached `state.current:
  complete`.

## Out of Scope

- **MR-006 and MR-008 are not touched by this Change.** Both are genuine
  gaps in CHG-0045's own provenance bookkeeping (a missing re-verification
  record bound to its final Resolution subject; a missing `content_digest`
  on its Plan-approval record) that the gate is correctly flagging, per the
  Problem section's findings 3-4. They are corrected directly on CHG-0045's
  own branch — `provenance.yml` is already in the allowed post-freeze
  exception set — independent of this Change. This Change does not merge
  CHG-0045's PR #36; it removes the two gate defects blocking an accurate
  evaluation, so CHG-0045 can be judged on its own remaining, real merits.
- **MR-015 provides no protection today against a completed Change's
  implementation changing outside its own `change_root` directory** —
  found while investigating this Change, confirmed by direct reproduction,
  real and already live on `main`, independent of CHG-0045. Closing it
  means resolving the same repo-wide-vs-per-Change tension CHG-0036 already
  fought once, for the completed state specifically — materially larger
  than either fix here. Named explicitly (Discovery, Specification's Out
  of Scope) rather than left an implicit, false assumption.
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
  base/head commits no longer reports MR-015 or MR-017 (MR-006 and MR-008
  are expected to still fire until CHG-0045's own branch is separately
  corrected — that is not this Change's success condition).
- A Change that legitimately writes Documentation/Knowledge Capture/
  Completion artifacts after its Review subject is frozen is never flagged
  MR-015-stale for that alone.
- A Change that has *not yet* reached `state.current: complete` is still
  flagged MR-015-stale for exactly the Change-local edits it is flagged for
  today — no regression in that part of the check's existing behavior. (No
  claim is made about `change_root`-external implementation changes: MR-015
  provides no such protection today, in either direction, independent of
  this Change — see Out of Scope.)
- None of the ten currently-ambiguous Adapter-generated paths trigger
  MR-017 anymore.

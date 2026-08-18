---
forge:
  artifact: intent
  schema: 1
change: CHG-0011
status: complete
---

# Intent — Review Convergence Boundary

## Problem

Protocol 2 (CHG-0008) modeled Strict Review as an ordered array of `iterations`
bound to revision-scoped provenance, but it did not distinguish *why* a given
iteration exists. Every re-review after a blocking Resolution is, today,
structurally identical to the Initial Review: it carries no scope boundary,
no relationship to the findings it exists to verify, and no limit on how many
times the cycle may repeat.

This is empirically observed in this repository. `CHG-0010-adapter-cli-codex-ux`
(`.forge/changes/CHG-0010-adapter-cli-codex-ux/manifest.yml`) is currently at
Strict Review iteration 5, `status: pending`, with no repository-native
boundary preventing a 6th, 7th, or Nth unrestricted re-audit. Each re-review
under the current model is free to re-open the entire review surface, so a
Resolution that correctly fixes the findings it was given can still be met
with an unbounded set of newly discovered, unrelated findings. Reviewer rigor
and process termination are currently in tension: the only way to stop the
loop today is for the agent to unilaterally decide "good enough," which is
exactly the outcome Strict Review (C-022, C-023) exists to prevent.

## Goal

Introduce the smallest normative and mechanical boundary sufficient to make
the Resolution → Verification cycle convergent, without weakening adversarial
review authority for a genuine Initial Review, and without building the
general Decision Gate / Decision-Aware Resolution framework planned for a
later Change.

Concretely:

1. Define **Initial Review** and **Resolution Verification** as distinct
   kinds of Strict Review Iteration, with Resolution Verification scoped to
   the Resolution it follows rather than an unrestricted re-audit.
2. Define a verifiable **Resolution Scope** and **Resolution Delta**, and
   detect **Out-of-Scope Mutation** mechanically from repository-native
   provenance and Git history already established by Protocol 2.
3. Define a taxonomy that lets a Resolution Verification block on findings it
   is responsible for (unresolved findings, resolution regressions,
   out-of-scope mutation) without silently discarding an unrelated
   pre-existing defect, and without turning that defect into an unbounded
   re-audit by itself.
4. Define deterministic convergence/non-convergence semantics: after a bounded
   number of consecutive Resolution Verifications that each produce new
   material findings independent of the cycle's originating findings,
   progression MUST stop automatically and require an explicit engineering
   decision — without implementing a general Decision Gate framework.

## Required outcomes

1. `forge/change@2` manifests MAY classify a Review Iteration's `kind`
   (`initial_review` | `resolution_verification`); absence of `kind` preserves
   exact current (legacy) Protocol 2 behavior.
2. A Resolution's provenance record MAY declare `scope` (paths) and `targets`
   (finding IDs); a Resolution Verification against it MUST be checked against
   that declared scope using the same Git-history mechanism Protocol 2 already
   uses for the review-subject freeze.
3. Material mutation outside declared Resolution Scope MUST NOT be silently
   approved by a scoped Resolution Verification; it requires explicit Full
   Review Escalation to a new Initial Review.
4. A deterministic, Core-computed (not self-declared/resettable) convergence
   counter MUST exist; reaching its limit MUST produce an explicit
   `review_convergence_failed` state that blocks further automatic Resolution
   and blocks `review.status: passed`, until an explicit decision record with
   a recognized option and reason is present.
5. None of the above may retroactively invalidate an existing Protocol 1 or
   Protocol 2 Change (including `CHG-0008` and the in-flight `CHG-0010`, both
   of which classify no iteration and declare no scope).
6. This Change ships within Protocol 2 as an additive, opt-in extension: no
   new integer Protocol identifier, no forced migration.

## Non-goals

- No general Decision Gate / Decision Analysis framework.
- No `forge/decision@1` schema or reusable Decision Gate primitive for
  Specification/Architecture stages.
- No delegated/automatic decision authority — non-convergence returns
  authority to the engineer.
- No change to Reviewer/Resolver independence invariants (Execution/Context
  separation, freeze, provenance authority) already established by CHG-0008;
  this Change narrows *scope and purpose*, not *independence*.
- No retroactive reclassification of historical Review Iterations belonging
  to completed or in-flight Changes.
- No CLI subcommands for review/resolution execution (C-031 CLI boundary is
  unaffected: enforcement remains inside `forge validate`).

## Flow

FULL. This Change alters canonical Protocol 2 Contract obligations, Protocol
2 Specification sections, review policy, two normative Schemas, and the Core
`forge validate` mechanical boundary that other Changes' Completion depends
on.

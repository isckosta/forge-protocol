# Forge Engineering Contract

Status: Canonical Protocol 2 Contract

Protocol 2 inherits C-001 through C-025 and C-027 through C-046 from Protocol 1 without weakening them. The only intentional breaking strengthening introduced by Protocol 2 is the C-026 review-independence obligation defined below. Where this file repeats an inherited invariant, its meaning is unchanged from Protocol 1.

## C-001 — Explicit Intent
Every Change MUST have explicit Intent before Implementation.

## C-002 — Classification before Implementation
Every Change MUST receive a Flow before Implementation begins.

## C-003 — Semantic classification
Classification MUST primarily use semantic impact.

## C-004 — No silent downgrade
A Change MUST NOT automatically downgrade to a weaker Flow.

## C-005 — Required escalation
A Change MUST escalate when discovered impact exceeds its current Flow.

## C-006 — No silent Requirement mutation
Requirements MUST NOT be silently changed to fit an Implementation.

## C-007 — Specification precedes behavioral Implementation
Where formal Specification is required, behavioral Implementation MUST NOT precede the relevant Specification.

## C-008 — TDD-first
Reasonably testable executable behavioral Changes MUST follow TDD.

## C-009 — RED before production behavior
The relevant behavioral test MUST exist before the production Implementation intended to satisfy it.

## C-010 — RED must be observed
The test MUST be executed and MUST fail for the expected reason.

## C-011 — Invalid RED is not evidence
Syntax, fixture, environment, dependency, or unrelated failures MUST NOT count as valid RED.

## C-012 — GREEN follows RED
Production behavior intended to satisfy a test MUST follow valid RED.

## C-013 — Minimal GREEN
Implementation SHOULD introduce the minimum relevant behavior required to reach GREEN.

## C-014 — Refactor preserves GREEN
Refactoring MUST preserve verified behavior.

## C-015 — New behavior requires a new cycle
Behavior introduced during refactoring MUST receive an appropriate new TDD cycle.

## C-016 — Coverage is not TDD
Post-hoc tests MUST NOT be represented as TDD evidence.

## C-017 — TDD exceptions are explicit
When TDD is not reasonably applicable, the reason MUST be recorded.

## C-018 — Bugfixes prove the defect first
Reasonably automatable bugfixes MUST establish a failing regression test before the fix.

## C-019 — Root cause over symptom suppression
Bugfixes SHOULD address root cause. Mitigation-only fixes MUST make unresolved root cause explicit when known.

## C-020 — Verification required
Every Change MUST undergo Verification.

## C-021 — Tests are evidence
Passing tests MUST NOT automatically be treated as proof of correctness.

## C-022 — Review required
Every Change MUST undergo Strict Review.

## C-023 — Review is adversarial
Strict Review MUST actively search for reasons to reject the Implementation.

## C-024 — TDD is reviewable
Reviewer SHOULD verify TDD evidence when TDD applies.

## C-025 — Findings require evidence
BLOCKER and MAJOR Findings MUST include sufficient evidence.

## C-026 — Verifiable Reviewer/Resolver independence
Strict Review MUST execute in an Execution and Execution Context independent from the Implementation or Resolution that produced the revision under review. Changing Role inside one Execution or transient conversational/reasoning context is self-review and MUST NOT satisfy Strict Review.

Every passed Review Iteration MUST reference repository-native provenance records for both the subject execution and the Reviewer execution, and both records MUST bind to the same revision identifier being reviewed. The subject record MUST represent `implementation` or `resolution`; the Reviewer record MUST represent `review`. Shared execution identifiers or shared context identifiers violate this invariant for FAST, STANDARD, and FULL.

Provenance assurance has three levels: `claimed`, `recorded`, and `verified`. A claim is an identifier declaration only and is insufficient for `review_passed`. Recorded provenance is durable repository-native execution evidence captured for the execution and is the minimum Core requirement for `review_passed`. Verified provenance is stronger evidence observed by a Harness, Adapter, operator, or equivalent mechanism. Core validation verifies record existence, revision linkage, role linkage, assurance level, and execution/context separation; it MUST NOT describe self-recorded identifiers as cryptographic or external proof.

For a Git-backed frozen subject, Core MUST validate the effective reviewable workspace rather than only committed history. Committed post-freeze deltas, staged deltas, unstaged deltas, tracked deletions/renames, and Git-visible untracked files MUST invalidate the subject when they affect reviewable material. Git-ignored files do not participate in this invariant. Only the exact repository-root-relative `manifest.yml`, `provenance.yml`, and `review.md` paths of the Change whose subject is frozen may differ as review-control metadata; the exception MUST NOT be broadened by basename, substring, directory membership, rename target, or symlink substitution.

After blocking Findings are resolved, acceptance MUST use a new Review Iteration referencing the Resolution provenance for the resolved revision and Reviewer provenance independent from that Resolution Execution and Context. A Resolver MUST NOT resolve blocking Findings in the Reviewer's Execution Context.

The same Harness, provider, model, or agent implementation MAY perform multiple Roles when real execution/context boundaries exist. Core MUST remain provider-independent and MUST NOT require remote infrastructure to establish the repository-native provenance ledger.

## C-027 — Blocking review evidence blocks Completion
Unresolved BLOCKER Findings MUST prevent Completion. When an active external review surface exists, unresolved threads containing findings classified as blocking MUST also prevent Completion. Without an external review surface, the thread condition is satisfied trivially.

## C-028 — Documentation Impact is mandatory
Every Change MUST evaluate Documentation Impact.

## C-029 — Repository reality is authoritative
Manifest state MUST reflect repository reality.

## C-030 — Durable knowledge belongs to the repository
Essential engineering information MUST NOT exist exclusively in chat history.

## C-031 — FAST reduces ceremony, not quality
FAST MUST NOT remove applicable TDD, Verification, Review, or Documentation Impact evaluation.

## C-032 — Existing Architecture must be inspected
Relevant existing Architecture SHOULD be inspected before new abstractions are introduced. For FULL Changes this is REQUIRED.

## C-033 — No parallel Architecture by convenience
Agents MUST NOT introduce competing architectural patterns merely because they are locally convenient.

## C-034 — Explicit skipping
SKIPPED stages or Gates MUST include a reason.

## C-035 — No false Completion
A Change MUST NOT be complete while known required work remains.

## C-036 — Protocol precedes Harness behavior
Harness conventions MUST NOT silently replace canonical Protocol semantics.

## C-037 — Provider independence
Forge Protocol MUST NOT depend on a specific AI provider.

## C-038 — Local Core operation
Canonical Forge operation MUST NOT require a Forge-hosted backend.

## C-039 — Proportional process
Forge SHOULD require only Artifacts that provide material engineering value for the selected Flow.

## C-040 — Explicit trade-offs
Intentional reductions in engineering confidence MUST be explicit.

## C-041 — Knowledge consistency
Material changes to durable system reality MUST update relevant durable knowledge.

## C-042 — Project configuration cannot weaken the Contract
Project configuration and project Contract extensions MUST NOT weaken canonical Contract invariants.

## C-043 — Adapters cannot redefine Forge
Harness Adapters MUST NOT redefine canonical or effective Forge semantics.

## C-044 — Forge dogfoods Forge
Material development of Forge itself MUST use Forge.

## C-045 — Compatible Protocol evolution
Changes that retain an integer Protocol identifier MUST preserve the meaning and minimum obligations of existing valid instances under that identifier.

## C-046 — Breaking changes require a new Protocol identifier
Removing or weakening an invariant, changing an existing required field or Gate meaning, or invalidating a previously valid conforming instance MUST require a new integer Protocol identifier.

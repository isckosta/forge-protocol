# Forge Engineering Contract

Status: Canonical Protocol 1 Contract

These rules are non-negotiable Forge engineering invariants. Projects may become stricter. They may not weaken these invariants while claiming canonical Forge compliance.

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

## C-026 — Reviewer/Resolver separation
Reviewer and Resolver MUST remain distinct conceptual Roles.

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
Changes that retain an integer Protocol identifier MUST preserve the meaning
and minimum obligations of existing valid instances under that identifier.

## C-046 — Breaking changes require a new Protocol identifier
Removing or weakening an invariant, changing an existing required field or Gate
meaning, or invalidating a previously valid conforming instance MUST require a
new integer Protocol identifier.

## C-047 — Resolution Verification is scoped
A Review Iteration classified as Resolution Verification MUST NOT be
conducted as an unrestricted re-audit of the review subject. Its authority is
bounded to the Findings it targets, defects within its Resolution Delta, and
Out-of-Scope Mutation. This rule binds a Change only once it opts into
Resolution Verification classification; it does not create a new obligation
for a Review Iteration that does not.

## C-048 — Material out-of-scope mutation requires Full Review Escalation
A Resolution that materially mutates the review subject outside its declared
Resolution Scope MUST NOT receive approval through a scoped Resolution
Verification. It MUST escalate to a new, unrestricted Initial Review.

## C-049 — Review convergence has deterministic termination semantics
A Resolution → Resolution Verification cycle MUST NOT be allowed to continue
automatically and indefinitely. Reaching the applicable Convergence Limit
MUST stop automatic progression, MUST NOT produce a passed Review, and MUST
require an explicit engineering decision before the cycle may continue.

## C-050 — Unrelated latent findings are recorded, not discarded or amplified
A Resolution Verification that discovers a Finding unrelated to the
Resolution under review MUST record it rather than silently discard it, and
MUST NOT treat that Finding alone as license to become an unrestricted
re-audit of unrelated pre-existing scope.

## C-051 — Material Unresolved Decisions block dependent Gates
A Gate MUST NOT be asserted passed while an Artifact within its dependency
set has a Material Unresolved Decision it owns in an Open-blocking
Lifecycle state (`open`, `analyzing`, or `awaiting_decision`).

## C-052 — Decisions are owned by the Artifact with subject-matter authority
An Unresolved Decision's owning Artifact MUST be the Artifact type with
semantic authority over its subject matter, regardless of which Artifact or
stage discovered it. A downstream Artifact MUST NOT resolve a Decision it
does not own.

## C-053 — Evidence and analysis precede escalation
Before an Unresolved Decision may reach a human-authority escalation,
available repository evidence and delegated engineering analysis MUST be
attempted and recorded, regardless of outcome.

## C-054 — Recommendation is not Decision
A Recommendation MUST NOT be recorded as a Decision unless the Decision's
Authority explicitly permits autonomous resolution of its Class.

## C-055 — Human-authority Decisions require an explicit human act
A Decision whose Authority is human MUST NOT reach `resolved` status
through an autonomous agent act. Recommendation Confidence MUST NOT
substitute for authorization.

## C-056 — Assumptions must not launder material decisions
A Material Assumption MUST be registered as an Unresolved Decision.
Declaring an Assumption MUST NOT substitute for creating or resolving the
Decision it is material to.

## C-057 — Backward invalidation is explicit
When a Decision resolves in a way that changes or supersedes an
already-complete Artifact, the Change MUST declare which downstream
Artifacts it invalidates, and those Artifacts MUST NOT remain complete or
approved until revisited.

## C-058 — Non-material questions require no Decision record
Forge MUST NOT require a recorded Unresolved Decision, escalation, or human
interruption for a Non-material question.

## C-059 — Reviewer discovering a missing material decision requests changes
A Reviewer that discovers a Material Unresolved Decision MUST record a
Finding and MUST NOT resolve it within the same Review.

## C-060 — Capability is not Authority
No Core validation, Gate, or documentation MAY treat evidence of technical
capability as evidence of Authority for a delegated Execution.

## C-061 — Delegated-Execution Out-of-Scope Mutation blocks silent validity
A delegated Execution's product MUST NOT be treated as validly produced
while an unresolved Out-of-Scope Mutation attributable to it exists.

## C-062 — No self-authorization
A delegated Execution MUST NOT use write access to an Authority-Defining
Artifact to declare or expand the Authority governing its own current
delegation beyond what was actually granted by its delegator.

## C-063 — Delegation Ceiling
A delegating Execution MUST NOT grant a delegate an Authorized Scope
exceeding its own current Authorized Scope, checked transitively at every
depth of a delegation chain.

## C-064 — Detection is the mandatory floor; Prevention is optional
Core MUST be able to verify a delegated Execution's Observed Effect against
its declared Authorized Scope using only local Git-native repository
state. Harness-enforced Prevention MAY additionally exist but MUST NOT be
required.

## C-065 — Fail-closed on indeterminate delegated-Execution authorization
When Core cannot reliably determine whether a delegated Execution's
Observed Effect was authorized, it MUST NOT default to treating that
Execution's product as authorized.

## C-066 — Harness honesty for delegated-Execution authority claims
No statement of delegated-Execution authority enforcement MAY represent
Detection as if it were Prevention.

C-060 through C-066 bind a Change only once it records a
`role: delegated_task` provenance entry. C-063 additionally binds only
where the delegate is itself a `role: delegated_task` record; a primary
Execution's own direct, undelegated work never triggers it.

## C-067 — Canonical Artifact Structure is guidance, not a Gate condition
`protocol/artifact-structure.md` defines canonical, non-binding guidance
for the information architecture of human Forge Artifacts. Agents SHOULD
follow it for their Artifact's type. Conformance to it MUST NOT be
treated as a Gate condition, and MUST NOT be validated by `forge
validate` beyond what a future Contract revision explicitly adds.

## C-068 — Verification and Review SHOULD present outcome before evidence
Verification SHOULD present its Result before supporting evidence. Review
SHOULD present an aggregate Verdict before per-iteration detail. Both
recommendations are defined in `protocol/artifact-structure.md`.

## C-069 — Approved Plans SHOULD NOT silently absorb Implementation history
An approved Plan SHOULD NOT be edited to silently absorb an
Implementation-time discovery. Such a discovery SHOULD be recorded in
Verification, a Decision record, or a documented re-Plan, per
`protocol/artifact-structure.md`.

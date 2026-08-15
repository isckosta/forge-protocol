# Specification Drift — CHG-0008

Date: 2026-08-15
Status: accepted before Resolution implementation

## Historical drift retained

The Laravel Forge stress test demonstrated that a single conversational context could implement a Change, switch its declared Role to Reviewer, issue findings, switch back to Resolver, and then switch again to Reviewer to approve its own remediation. The original session-shaped design therefore drifted to provider-independent **Execution** and **Execution Context** as the property at risk.

That historical finding remains valid, but Strict Review Iteration 1 identified that the first correction was still architecturally incomplete.

## Resolution drift — Strict Review Iteration 1

Strict Review findings CHG-0008-R001 through R004 require the specification to change before further production implementation.

### R001 — integer Protocol boundary

The stronger invariant is not a compatible clarification of Protocol 1. Protocol 1 historically required conceptual Reviewer/Resolver Role separation. Making independent Execution and independent Execution Context mandatory invalidates previously valid Protocol 1 instances and therefore crosses C-045/C-046.

Accepted correction:

- restore Protocol 1 C-026 and Specification review semantics to their pre-CHG-0008 meaning;
- introduce integer **Protocol 2** for the stronger Strict Review obligation;
- keep Protocol version and artifact schema version explicitly independent;
- do not retroactively migrate or reinterpret completed Protocol 1 Changes.

### R002 — provenance must pre-exist Review

`reviewer_identity` must not invent the Implementation/Resolution half of the evidence after the fact. Protocol 2 therefore uses a separate repository-native execution provenance ledger captured for Implementation, Resolution, and Review executions.

A provenance record binds a Role and provider-independent Execution/Context identifiers to a revision identifier and records when and how that evidence was captured. Harness/Adapter-native references are optional source metadata, not Core field names.

The implementation that originally produced CHG-0008 did not capture this evidence. That historical gap remains explicit and is not backfilled. This Resolution execution is the first CHG-0008 execution eligible to record new provenance prospectively.

### R004 — assurance levels and verification boundary

Pairwise-distinct strings are not evidence by themselves. Protocol 2 distinguishes:

1. `claimed` — identity declaration only;
2. `recorded` — durable repository-native provenance captured for the execution and linked to its revision;
3. `verified` — provenance additionally observed by a Harness, Adapter, operator, attestation mechanism, or equivalent source.

`review_passed` requires at least `recorded` provenance. Core validation resolves Review references against the ledger, checks Role and revision linkage, and checks execution/context separation. Core does **not** claim that a self-recorded ledger entry is cryptographic or external proof; `verified` is the stronger assurance level when a trustworthy observer exists.

No hosted Forge service is required.

### R003 — Flow and version semantics

Protocol 2 applies the new Strict Review independence invariant to FAST, STANDARD, and FULL. FAST reduces ceremony, not quality. Protocol 1 does not receive the Protocol 2 rule retroactively.

Validation must therefore resolve the project Protocol before applying C-026 provenance enforcement. An active Protocol 2 Change must not downgrade its Change schema to escape the Gate; completed historical Protocol 1 Change records may remain untouched.

## Review Iteration model

A single global Resolver identifier does not model repeated Review/Resolution cycles correctly. Protocol 2 Review is iteration-oriented:

Implementation Execution → revision A → Review Iteration 1

Resolution Execution → revision B → Review Iteration 2

Each passed Review Iteration references the subject provenance that produced the revision being reviewed and Reviewer provenance for the Review Execution evaluating that same revision. Re-review of revision B must be independent from the Resolution Execution/Context that produced B.

## Consequences for the prior CHG-0008 specification

The prior requirements that placed reviewer and resolver execution identifiers together inside `review.reviewer_identity` are superseded. `forge/change@2` becomes the Protocol 2 Change shape with explicit Review Iterations; execution evidence moves to `forge/execution-provenance@1`.

The original Strict Review Iteration 1 and its REQUEST CHANGES result remain historical evidence. This Resolution may mark findings resolved only with implementation and verification evidence; it must not replace Iteration 1 with PASS or perform the subsequent Strict Re-review.

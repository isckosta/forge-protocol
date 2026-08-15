# ADR-0008 — Verifiable Review Independence

Status: Proposed pending CHG-0008 independent Strict Re-review

## Context

Protocol 1 originally required Reviewer and Resolver to remain distinct conceptual Roles. A Forge stress test showed that Role switching inside one conversational context permits self-review, motivating a stronger Execution/Context boundary. The first CHG-0008 implementation incorrectly placed that stronger semantic obligation under Protocol 1 and represented both Reviewer and Resolver IDs inside one review object. Strict Review Iteration 1 rejected that design in R001-R004.

## Decision 1 — Protocol 2 owns the stronger invariant

Protocol 1 retains its historical C-026 meaning. Protocol 2 introduces mandatory Strict Review independence by concrete Execution and transient Execution Context. This is an integer Protocol break under C-045/C-046, not merely `forge/change@2` schema evolution.

Protocol 2 canonical resources live under `protocol/versions/2/`. The CLI supports Protocols 1 and 2 and resolves the configured Protocol before selecting version-specific Contract semantics. Completed Protocol 1 Changes are not rewritten.

## Decision 2 — Provenance is separate from Review state

Protocol 2 introduces repository-native `forge/execution-provenance@1`. A record binds a Forge Role, provider-independent Execution ID, Execution Context ID, capture time, revision identifier, and evidence source. Harness-specific run/thread/session/conversation identifiers may be retained as source references but do not become Core field names.

Review state remains in `forge/change@2` and is iteration-aware. Each passed Review Iteration references the subject provenance that produced its revision and the Reviewer provenance that evaluated the same revision. This correctly models:

Implementation → revision A → Review 1 → Findings → Resolution → revision B → Re-review 2.

Re-review 2 is compared with the Resolution provenance for B, not with one global Resolver identity.

## Decision 3 — Assurance is explicit

Provenance has three assurance levels:

- `claimed`: identity declaration only;
- `recorded`: durable repository-native execution provenance linked to a revision;
- `verified`: provenance additionally observed by a Harness, Adapter, operator, attestation mechanism, or equivalent source.

Protocol 2 `review_passed` requires at least `recorded` provenance. The Core validator checks reference existence, Role linkage, revision linkage, assurance level, and Execution/Context inequality. Pairwise-distinct strings without matching records fail.

This is deliberately not a claim of cryptographic truth. A malicious author could falsify a self-recorded repository record. Forge only claims stronger verification when the record actually carries `verified` observer-backed evidence. No hosted Forge backend is required.

## Decision 4 — Same quality across Flows

Protocol 2 applies the independence rule to FAST, STANDARD, and FULL. FAST reduces ceremony, not quality. Protocol 1 remains unaffected.

## Decision 5 — Resolution provenance and historical gaps

The original CHG-0008 Implementation and Strict Review Iteration 1 did not capture valid subject provenance. Those identifiers are not reconstructed. The current Resolution prospectively records `resolution-001` with `recorded` assurance. The subsequent Reviewer must create independent Reviewer provenance before Review Iteration 2 can pass.

## Consequences

The Protocol boundary is honest, repeated Review/Resolution cycles age correctly, forged unequal strings no longer satisfy deterministic validation, and provider independence/local operation are retained. The remaining trust limitation is explicit: repository-native recorded provenance improves auditable consistency but is not equivalent to external attestation.

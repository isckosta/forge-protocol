# Discovery — CHG-0008

## Protocol/versioning findings

The pre-Resolution branch strengthened C-026 and Strict Review under `Protocol version: 1` while relying on `forge/change@2` as the structural boundary. `protocol/compatibility.md`, C-045, and C-046 make that invalid because previously valid Protocol 1 instances would acquire new mandatory semantics. The correct boundary is integer Protocol 2.

Protocol 1 canonical Contract, Specification, Review Policy, and `forge/change@1` therefore remain authoritative for historical Protocol 1 semantics. Protocol 2 resources are versioned separately under `protocol/versions/2/`.

## Provenance findings

`review.reviewer_identity` incorrectly required Review to manufacture both Reviewer and Resolver identifiers after the fact. CHG-0008's original implementation did not capture suitable execution/context provenance, so that history cannot be truthfully reconstructed.

A separate repository-native provenance ledger is required. It must record Implementation, Resolution, and Review executions prospectively and bind them to revisions. Review state should reference those records rather than duplicate them.

## Trust boundary

String inequality is only a consistency condition. A durable record can still be self-asserted, so Core must distinguish `claimed`, `recorded`, and `verified` provenance. Core can prove that referenced repository records exist and are internally consistent; it cannot claim cryptographic/external truth unless an observer-backed source actually provides it.

## Flow consistency

C-031 means FAST cannot escape a quality invariant that is normative under its Protocol. Protocol 2 therefore applies the same Strict Review provenance boundary to FAST, STANDARD, and FULL. Protocol 1 remains unaffected.

## Re-review lifecycle

The durable model must support Implementation → revision A → Review → Resolution → revision B → Re-review. The Reviewer for revision B is compared against the Resolution execution that produced B, not against a global Resolver field.

## Distribution/Adapter constraints

Protocol resolution must work from source checkout and isolated wheel without network access. Codex projections must receive the selected Protocol explicitly so Protocol 2 semantics do not leak into Protocol 1. The Adapter may support both Protocols through its half-open compatibility interval.

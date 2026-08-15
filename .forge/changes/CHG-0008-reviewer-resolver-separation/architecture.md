---
forge:
  artifact: architecture
  schema: 1
change: CHG-0008
status: complete
---

# Architecture — Protocol 2 Review Provenance

## Version boundary

Protocol 1 remains rooted at `protocol/specification.md`, `protocol/contract/engineering.md`, and `protocol/policies/review.yml` with its historical conceptual Role-separation meaning. Protocol 2 canonical resources live under `protocol/versions/2/`. The CLI resolves `.forge/forge.yml -> forge.protocol` before selecting version-specific Contract semantics. Shared Flow definitions remain shared where their lifecycle shape did not change.

## Provenance ledger

Protocol 2 adds `.forge/changes/<change>/provenance.yml` using `forge/execution-provenance@1`. Records are provider-independent and contain Role, Execution ID, Context ID, capture time, revision binding, and source metadata. Harness-native identifiers are optional `source` references rather than Core field names.

Assurance is explicit: `claimed` is a declaration, `recorded` is durable repository-native provenance, and `verified` adds observation by a Harness/Adapter/operator or equivalent mechanism. `review_passed` requires at least `recorded`. The Core verifies consistency and linkage; it does not claim cryptographic truth for a self-recorded record.

## Review iterations

`forge/change@2` is the active Protocol 2 Change shape and records `review.iterations[]`. A passed iteration references `subject_provenance` and `reviewer_provenance` for the same revision. The subject is the Implementation or Resolution that produced that revision. This replaces the incorrect global Resolver fields and supports repeated Review → Resolution → Re-review cycles.

## Validation

Protocol 2 C-026 validation applies equally to FAST, STANDARD, and FULL. It rejects missing provenance, nonexistent references, insufficient assurance, wrong Roles, wrong revision linkage, shared Execution, shared Context, partial records, and active schema downgrade. Completed historical Protocol 1 `forge/change@1` records are explicitly preserved.

## Adapter boundary

Codex projection input now carries a Protocol identifier. Protocol 2 projects provenance/re-review instructions for every Flow; Protocol 1 does not receive those stronger semantics. The Adapter interval is widened to support Protocols 1 and 2 without redefining either.

## CHG-0008 historical gap

No provenance is fabricated for the original Implementation or Strict Review Iteration 1. This Resolution records a new `resolution-001` record prospectively. Review Iteration 2 references that subject record but remains pending until a distinct Reviewer Execution/Context records its own provenance.

# Changelog

All notable Forge changes will be documented here.

CLI releases will follow Semantic Versioning when releases begin. Protocol versions are tracked independently.

## Unreleased

### Protocol 2 — Verifiable Review Independence

Added:

- integer **Protocol 2** as the compatibility boundary for mandatory independent Strict Review Execution and Execution Context;
- version-specific Protocol 2 Contract, Specification, and Review Policy resources under `protocol/versions/2/`;
- `forge/execution-provenance@1`, a provider-independent repository-native ledger for Implementation, Resolution, and Review execution provenance;
- explicit provenance assurance levels: `claimed`, `recorded`, and `verified`, with at least `recorded` required for Protocol 2 `review_passed`;
- iteration-aware Protocol 2 Review state in `forge/change@2`, linking each passed Review to subject and Reviewer provenance for the revision under review;
- FAST, STANDARD, and FULL Protocol 2 validation for missing/forged provenance, wrong revision binding, shared Execution, shared Context, partial evidence, contaminated re-review, and active schema downgrade;
- Protocol-aware canonical Contract resolution in validation and Doctor;
- Protocol-aware Codex projection so Protocol 2 provenance semantics are projected for FAST/STANDARD/FULL without leaking into Protocol 1.

Changed:

- restored Protocol 1 C-026, Specification §25, Review Policy, and `forge/change@1` to their historical pre-CHG-0008 semantics instead of retroactively strengthening Protocol 1;
- Codex Adapter compatibility interval now covers integer Protocols 1 and 2;
- compatibility documentation now explicitly distinguishes Protocol version from artifact schema version and documents the Protocol 1 → 2 breaking boundary.

Security/trust boundary:

- pairwise-distinct execution/context strings are no longer treated as sufficient evidence of independence;
- Forge Core verifies durable provenance linkage and consistency but does not claim self-recorded provenance is cryptographic/external proof; `verified` provenance is reserved for observer-backed evidence.

Migration:

- completed historical Protocol 1 Changes remain unchanged and require no fabricated provenance;
- active Protocol 2 Changes use `forge/change@2` and may not downgrade to `forge/change@1` to bypass the Strict Review Gate.

### Protocol 1 Contract Freeze

Changed:

- stabilized the human-readable Protocol label as `1` while preserving integer Protocol compatibility;
- published Protocol 1 compatibility, breaking-change, and deprecation rules;
- added a portable schema catalog and offline contract coverage for canonical schemas and repository-native artifacts;
- migrated historical artifact structures to their canonical schemas without changing recorded engineering outcomes.

### Foundation

Added:

- Forge Manifesto and Core Architecture;
- Forge Core Protocol, Engineering Contract, FAST/STANDARD/FULL Flows, TDD-first development model, RED → GREEN → REFACTOR lifecycle, Verification, adversarial Strict Review, and canonical Policies/Schemas;
- official Python CLI with `version`, `init`, `validate`, and `doctor`;
- repository-native Change lifecycle, configuration resolution, offline packaged Protocol resources, Distribution Verification, Harness Adapter architecture, Codex Adapter, and deterministic Adapter planning/publication/drift detection.

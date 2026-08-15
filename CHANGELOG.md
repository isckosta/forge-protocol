# Changelog

All notable Forge changes will be documented here.

CLI releases will follow Semantic Versioning when releases begin. Protocol versions are tracked independently.

## Unreleased

### Verifiable Review Independence

Added:

- `forge/change@2` structurally requires `review.reviewer_identity` for FULL Changes with provider-independent `actor_type`, `execution_id`, `context_id`, `resolver_execution_id`, and `resolver_context_id`; `forge/change@1` remains backward compatible;
- Strict Review now requires an Execution and Execution Context independent from the implementation or resolution being reviewed; changing Role inside one conversation/context is explicitly self-review and does not satisfy Strict Review;
- `forge validate` rejects shared Reviewer/Resolver execution IDs and shared context IDs with C-026, including the case where executions differ but conversational/reasoning context is shared;
- Review Policy requires execution-context independence for FAST, STANDARD, and FULL, keeps self-review non-authoritative, and requires re-review independent from blocking-finding Resolution;
- Codex STANDARD/FULL projections instruct the harness to create a real execution/context boundary and record durable execution/context references;
- ADR-0008 documents context contamination, the human PR analogy, provider independence, and the limits of isolated same-model review.

### Protocol 1 Contract Freeze

Changed:

- stabilized the human-readable Protocol label as `1` while preserving integer
  Protocol compatibility;
- published Protocol 1 compatibility, breaking-change, and deprecation rules;
- added a portable schema catalog and offline contract coverage for canonical
  schemas and repository-native artifacts;
- migrated historical artifact structures to their canonical schemas without
  changing recorded engineering outcomes.

### Foundation

Added:

- Forge Manifesto;
- Core Architecture;
- Forge Core Protocol draft;
- Engineering Contract;
- FAST, STANDARD, and FULL Flows;
- TDD-first development model;
- RED -> GREEN -> REFACTOR lifecycle;
- RED Gate semantics;
- regression-first bugfix policy;
- adversarial Strict Review;
- baseline Testing, Review, Documentation, Architecture, and Security Policies;
- project and Change Schemas;
- configuration-resolution model;
- foundational RFC and ADRs;
- Forge dogfooding workspace;
- CHG-0001 Bootstrap Forge CLI Specification and Test Strategy;
- Python 3.12+ bootstrap CLI with `version`, `init`, `validate`, and `doctor`;
- Git repository root resolution;
- atomic staged workspace publication with exclusive initialization locking;
- canonical Project Schema validation and Protocol compatibility checks;
- canonical Flow and Engineering Contract resolution;
- structured validation findings and read-only Doctor diagnostics;
- packaged canonical Protocol resources for isolated wheel execution;
- offline distribution verification and runtime dependency audit;
- Harness Adapter manifest and installation-record Schemas;
- independent Adapter identity/versioning and half-open Protocol compatibility intervals;
- Harness capability requirement and explicit limitation model;
- immutable deterministic Adapter plans with ownership and operation vocabularies;
- deterministic shared-artifact merge provenance requirements;
- repository-native Adapter installation records with generated content digests;
- generated artifact drift detection and stale-state conflict protection;
- Harness-agnostic conformance validation for canonical Flow, TDD RED, Strict Review, and repository authority;
- deterministic Harness-agnostic Adapter planner;
- safe Adapter publisher with repository path confinement, symlink/traversal protection, update preconditions, rollback, and installation-record-last semantics;
- isolated-wheel regression coverage proving Adapter Schemas resolve without a source checkout;
- first concrete Codex Harness Adapter with packaged descriptor and dated capability evidence;
- deterministic Codex workflow and Engineering Contract projection resources derived from canonical Forge input;
- conservative Codex capability declarations and explicit invariant enforcement limitations;
- optional explicit/evidence-backed Codex publication targets without an invented vendor path;
- generic Core reuse for Codex planning, ownership, collision protection, installation state, and drift detection;
- isolated-wheel and offline Codex Adapter verification without a Codex/OpenAI SDK dependency.

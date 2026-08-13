# Changelog

All notable Forge changes will be documented here.

CLI releases will follow Semantic Versioning when releases begin. Protocol versions are tracked independently.

## Unreleased

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
- isolated-wheel regression coverage proving Adapter Schemas resolve without a source checkout.

The bootstrap CLI remains pre-release software. Harness Adapter Foundation defines the contract only; concrete Harness integrations are separate Changes.

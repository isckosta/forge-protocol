---
forge:
  artifact: specification
  schema: 1
change: CHG-0002
status: ready_for_review
---

# Specification — Harness Adapter Foundation

## 1. Adapter identity

### FR-001 — Stable Adapter identifier
Every Harness Adapter MUST expose a stable identifier.

### FR-002 — Adapter version
Every Adapter MUST expose its own version independently from Forge CLI and Protocol versions.

### FR-003 — Target Harness
Every Adapter MUST declare the Harness it targets.

## 2. Protocol compatibility

### FR-004 — Supported Protocol range
Every Adapter MUST declare the Forge Protocol versions it supports.

### FR-005 — Compatibility rejection
Forge MUST reject Adapter activation when the configured project Protocol is outside the Adapter's supported range.

## 3. Capability model

### FR-006 — Capability declaration
Every Adapter MUST declare the Forge-relevant Harness capabilities it supports.

### FR-007 — Initial capability vocabulary
The initial capability vocabulary MUST support at least:
- persistent_instructions;
- commands;
- skills;
- hooks;
- agent_roles;
- generated_files.

### FR-008 — Unsupported capability reporting
When a required Forge representation cannot be expressed by the target Harness, the Adapter MUST report the unsupported capability explicitly rather than silently omit it.

## 4. Input boundary

### FR-009 — Effective Configuration input
Adapters MUST consume resolved Effective Forge Configuration rather than raw project fragments as their semantic input.

### FR-010 — Read-only canonical semantics
Adapters MUST NOT mutate canonical Protocol resources while generating Harness representation.

### FR-011 — Repository state authority
Adapters MUST NOT treat Harness-native representation as the authoritative source of Change state, Contract, Flow, Policy, Review, or TDD evidence.

## 5. Output model

### FR-012 — Adapter plan
An Adapter MUST be able to produce a deterministic installation/update plan before filesystem mutation.

### FR-013 — Planned artifact metadata
Each planned artifact MUST declare:
- path;
- ownership mode;
- content or generation result;
- operation intent.

### FR-014 — Ownership modes
The initial ownership modes MUST be:
- forge_owned;
- user_owned;
- shared.

### FR-015 — Operation intents
The initial operation intents MUST be:
- create;
- update;
- preserve;
- conflict;
- delete_generated.

## 6. Safe mutation

### FR-016 — No silent overwrite
Adapter application MUST NOT silently overwrite user-owned artifacts.

### FR-017 — Forge-owned update
Forge-owned generated artifacts MAY be deterministically replaced by the same Adapter when ownership can be proven.

### FR-018 — Shared artifact conflict
Shared artifacts MUST require an explicit merge strategy defined by the Adapter. When no safe merge strategy exists, the result MUST be conflict.

### FR-019 — Atomic publication boundary
Adapter application SHOULD avoid leaving a state that appears successfully installed when publication fails partway through.

## 7. Installation record

### FR-020 — Adapter installation record
A Forge project using an Adapter MUST retain repository-native metadata identifying the installed Adapter, Adapter version, target Harness, and generated Forge-owned artifacts.

### FR-021 — Derived-state rule
The installation record MAY describe generated Harness representation but MUST NOT duplicate canonical Change state as an alternate source of truth.

## 8. Determinism and drift

### FR-022 — Deterministic planning
Given the same Effective Forge Configuration, Adapter version, Harness capability state, and repository inputs, the Adapter plan SHOULD be deterministic.

### FR-023 — Generated drift detection
Forge MUST be able to determine when a Forge-owned generated artifact differs from the content expected by the currently installed Adapter.

### FR-024 — User modification detection
When a Forge-owned artifact has been modified outside the expected generated content, Adapter update MUST NOT silently destroy the modification.

## 9. Conformance

### FR-025 — Canonical invariant preservation
An Adapter MUST NOT weaken canonical Engineering Contract requirements.

### FR-026 — Flow preservation
An Adapter MUST NOT remove required stages or Gates from the effective Flow semantics it represents.

### FR-027 — TDD preservation
An Adapter MUST NOT represent a TDD-applicable Flow in a way that authorizes production behavior before valid RED.

### FR-028 — Review preservation
An Adapter MUST NOT represent a canonical Flow in a way that bypasses required Strict Review.

### FR-029 — Explicit limitation
If the Harness cannot enforce a Forge invariant, the Adapter MUST represent the limitation explicitly and MUST NOT claim enforcement.

## 10. CLI boundary

### FR-030 — Infrastructure-only Adapter commands
The Forge CLI MAY support Adapter installation, configuration, validation, update, and diagnostics.

### FR-031 — No lifecycle execution
Adapter support in the CLI MUST NOT execute Specification, TDD Implementation, Verification, Review, Resolution, or Completion stages.

## 11. Adapter schema

### FR-032 — Machine-readable manifest
Forge MUST define a canonical machine-readable Adapter manifest schema.

### FR-033 — Validation
Forge MUST be able to validate Adapter manifests deterministically.

## 12. Non-functional requirements

### NFR-001 — Local-first
Core Adapter validation and planning MUST NOT require network access.

### NFR-002 — Harness-agnostic Core
Core Adapter models MUST NOT import or depend on a specific Harness SDK.

### NFR-003 — Human-reviewable plans
Adapter plans SHOULD be serializable into a human-reviewable representation.

### NFR-004 — Path safety
Generated artifact paths MUST remain confined to the intended repository or Harness configuration boundary.

### NFR-005 — Testability
Adapter planning and conflict detection MUST be testable independently from real Harness execution.

## 13. Invariants

### INV-001
The Adapter is a projection of Forge semantics, not a new semantic authority.

### INV-002
Repository-native Forge state remains authoritative.

### INV-003
Unsupported Harness capabilities are explicit.

### INV-004
User-owned files are never silently overwritten.

### INV-005
Adapter and Protocol versions remain independently versioned.

## 14. Acceptance scenarios

### AC-001 — Compatible Adapter
Given Protocol `1` and an Adapter declaring support for Protocol `1`, manifest validation succeeds.

### AC-002 — Incompatible Adapter
Given Protocol `1` and an Adapter that does not support Protocol `1`, activation fails explicitly.

### AC-003 — Unsupported capability
Given an Adapter unable to represent required Strict Review semantics, planning reports an explicit unsupported capability rather than producing a falsely compliant plan.

### AC-004 — User-owned collision
Given an existing user-owned Harness file at a planned path, Adapter planning marks conflict or preserve and application does not overwrite it.

### AC-005 — Forge-owned deterministic update
Given an artifact previously generated and still matching recorded generated state, a new deterministic Adapter version may replace it through an explicit update plan.

### AC-006 — Modified generated artifact
Given a Forge-owned artifact modified outside the recorded generated state, Adapter update reports drift/conflict and does not silently replace it.

### AC-007 — No semantic authority shift
Given Harness-native generated files are deleted, canonical Forge Contract, Flow, Policy, and Change state remain available from repository-native Forge sources.

### AC-008 — Deterministic plan
Given identical inputs, repeated Adapter planning produces semantically identical operations in stable order.

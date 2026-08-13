---
forge:
  artifact: specification
  schema: 1
change: CHG-0002
status: approved
review:
  iterations: 2
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

### FR-004 — Supported Protocol interval
Every Adapter MUST declare integer Protocol compatibility bounds:

```yaml
protocol:
  min: 1
  max_exclusive: 2
```

Compatibility is defined as `min <= project_protocol < max_exclusive`.

### FR-005 — Compatibility rejection
Forge MUST reject Adapter planning or application when the configured project Protocol is outside the declared interval.

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

### FR-008 — Required capability derivation
Forge-required representation capabilities MUST derive from Effective Forge Configuration and canonical Flow/Contract invariants. Adapter-internal implementation requirements MAY be declared separately but MUST NOT redefine Forge semantics.

### FR-009 — Unsupported capability reporting
When a Forge-required invariant cannot be faithfully represented by the target Harness, planning MUST report the limitation explicitly rather than silently omit it or claim enforcement.

## 4. Input boundary

### FR-010 — Effective Configuration input
Adapters MUST consume resolved Effective Forge Configuration rather than raw project fragments as their semantic input.

### FR-011 — Read-only canonical semantics
Adapters MUST NOT mutate canonical Protocol resources while generating Harness representation.

### FR-012 — Repository state authority
Adapters MUST NOT treat Harness-native representation as the authoritative source of Change state, Contract, Flow, Policy, Review, or TDD evidence.

## 5. Output model

### FR-013 — Adapter plan
An Adapter MUST be able to produce a deterministic installation/update plan before filesystem mutation.

### FR-014 — Planned artifact metadata
Each planned artifact MUST declare path, ownership mode, generation result/content, and operation intent.

### FR-015 — Ownership modes
Initial ownership modes MUST be `forge_owned`, `user_owned`, and `shared`.

### FR-016 — Operation intents
Initial operation intents MUST be `create`, `update`, `preserve`, `conflict`, and `delete_generated`.

## 6. Safe mutation

### FR-017 — No silent overwrite
Adapter application MUST NOT silently overwrite user-owned artifacts.

### FR-018 — Forge-owned update
Forge-owned generated artifacts MAY be replaced by the same Adapter only when ownership and expected generated state can be proven.

### FR-019 — Shared artifact conflict
Shared artifacts MUST use an Adapter-defined deterministic merge strategy. When no safe merge strategy exists, planning MUST report conflict.

### FR-020 — Atomic publication boundary
Adapter application SHOULD avoid leaving state that appears successfully installed when publication fails partway through.

## 7. Installation record

### FR-021 — Adapter installation record
A Forge project using an Adapter MUST retain repository-native metadata identifying Adapter id/version, target Harness, Protocol interval used, generated Forge-owned artifacts, expected content digests, and explicit limitations.

### FR-022 — Derived-state rule
The installation record MAY describe generated Harness representation but MUST NOT duplicate canonical Change lifecycle state as an alternate source of truth.

## 8. Determinism and drift

### FR-023 — Deterministic planning
Given the same Effective Forge Configuration, Adapter version, Harness capability state, and repository inputs, the Adapter plan SHOULD be deterministic and stably ordered.

### FR-024 — Generated drift detection
Forge MUST be able to determine when a Forge-owned generated artifact differs from the expected recorded generated content.

### FR-025 — User modification protection
When a Forge-owned artifact differs from expected generated state, Adapter update MUST report drift/conflict and MUST NOT silently replace it.

## 9. Conformance

### FR-026 — Canonical invariant preservation
An Adapter MUST NOT weaken canonical Engineering Contract requirements.

### FR-027 — Flow preservation
An Adapter MUST NOT remove required stages or Gates from effective Flow semantics.

### FR-028 — TDD preservation
An Adapter MUST NOT represent a TDD-applicable Flow in a way that authorizes production behavior before valid RED.

### FR-029 — Review preservation
An Adapter MUST NOT represent a canonical Flow in a way that bypasses required Strict Review.

### FR-030 — Explicit enforcement limitation
If the Harness cannot enforce a Forge invariant, the Adapter MUST expose that limitation and MUST NOT claim enforcement.

## 10. CLI boundary

### FR-031 — Infrastructure-only Adapter commands
The Forge CLI MAY support Adapter installation, configuration, validation, update, planning, and diagnostics.

### FR-032 — No lifecycle execution
Adapter support in the CLI MUST NOT execute Specification, TDD Implementation, Verification, Review, Resolution, or Completion stages.

### FR-033 — No activation state in v1
CHG-0002 MUST NOT introduce a separate Adapter activation lifecycle state. Compatibility is evaluated during manifest validation/planning/application.

## 11. Adapter schema

### FR-034 — Machine-readable manifest
Forge MUST define a canonical machine-readable Adapter manifest schema.

### FR-035 — Deterministic validation
Forge MUST validate Adapter manifests deterministically.

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
Adapter planning, compatibility, and conflict detection MUST be testable independently from real Harness execution.

## 13. Invariants

### INV-001
The Adapter is a projection of Forge semantics, not a semantic authority.

### INV-002
Repository-native Forge state remains authoritative.

### INV-003
Unsupported Harness capabilities are explicit.

### INV-004
User-owned files are never silently overwritten.

### INV-005
Adapter, Protocol, Schema, and CLI versions remain independently versioned.

## 14. Acceptance scenarios

### AC-001 — Compatible Adapter
Given project Protocol `1` and Adapter interval `min: 1, max_exclusive: 2`, manifest compatibility succeeds.

### AC-002 — Incompatible Adapter
Given project Protocol `1` and Adapter interval `min: 2, max_exclusive: 3`, planning fails explicitly before mutation.

### AC-003 — Unsupported required invariant
Given the Effective Flow requires Strict Review and the target Harness representation cannot preserve it, planning reports an explicit limitation and does not produce a falsely compliant result.

### AC-004 — User-owned collision
Given an existing user-owned Harness file at a planned path, planning reports preserve/conflict and application does not overwrite it.

### AC-005 — Forge-owned deterministic update
Given an artifact previously generated and still matching recorded state, a later plan may explicitly update it.

### AC-006 — Modified generated artifact
Given a Forge-owned artifact modified outside expected generated state, update reports drift/conflict and does not silently replace it.

### AC-007 — No semantic authority shift
Given generated Harness files are deleted, canonical Contract, Flow, Policy, and Change state remain available from Forge repository sources.

### AC-008 — Deterministic plan
Given identical inputs, repeated planning produces semantically identical operations in stable order.

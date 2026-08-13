---
forge:
  artifact: specification
  schema: 1
change: CHG-0004
status: proposed
review:
  iterations: 0
---

# Specification — Codex Harness Adapter

## 1. Scope and identity

### FR-001 — Concrete Adapter identity
The Codex Adapter MUST expose a stable Adapter identifier distinct from the generic Adapter Core and MUST declare Codex as its target Harness.

### FR-002 — Independent Adapter version
The Codex Adapter MUST version its projection independently from Forge CLI, Protocol, and schema versions.

### FR-003 — Protocol compatibility
The initial Codex Adapter MUST declare an explicit Protocol compatibility interval and MUST use the generic compatibility rules established by CHG-0002.

## 2. Capability declaration

### FR-004 — Evidence-backed capability manifest
The Codex Adapter MUST declare capabilities only when supported by authoritative current Codex documentation or an equivalent reproducible Harness contract.

### FR-005 — Confirmed skills capability
The initial Codex Adapter MUST declare `skills` as supported.

### FR-006 — Unverified capabilities are unsupported
Until independently proven, `persistent_instructions`, `commands`, `hooks`, and `agent_roles` MUST NOT be declared supported merely because an analogous concept exists in another Harness.

### FR-007 — Generated files
The Adapter MAY declare `generated_files` only for repository artifacts it can deterministically plan, publish, record, and validate through the generic Adapter Core.

### FR-008 — Capability evidence traceability
Each Codex-specific capability declaration MUST be traceable to a Discovery evidence entry or an explicit tested Harness contract.

## 3. Projection boundary

### FR-009 — Effective Forge Configuration input
The Codex Adapter MUST consume Effective Forge Configuration and canonical Forge semantics through the generic Adapter boundary; it MUST NOT reinterpret raw project fragments as an alternate configuration model.

### FR-010 — Codex-specific projection only
Codex-specific code MUST be limited to translating canonical Forge requirements into Codex-native representation and declaring Codex limitations.

### FR-011 — No Core duplication
The Codex Adapter MUST reuse generic compatibility, planning, ownership, installation-record, drift, path-safety, publication, and conformance mechanisms rather than fork equivalent Codex-specific implementations.

### FR-012 — Repository authority
Codex-native artifacts MUST remain derived representation. They MUST NOT become authoritative for Change state, Flow, Contract, Policy, Review, TDD evidence, or Completion.

## 4. Skills projection

### FR-013 — Forge workflow skill projection
Where a canonical Forge workflow can be faithfully represented using a Codex skill, the Adapter MUST generate a deterministic skill projection from canonical Forge semantics rather than maintain an independently authored semantic copy.

### FR-014 — No invented lifecycle authority
Generated Codex skills MAY instruct Codex how to participate in Forge workflows, but MUST NOT authorize lifecycle transitions that the canonical Forge state does not permit.

### FR-015 — Gate preservation in skills
A generated skill MUST preserve applicable canonical Gates, including Specification Review, TDD RED-before-production behavior, Verification, Strict Review, Resolution, and Completion when those Gates apply to the effective Flow.

### FR-016 — Explicit non-enforcement
When a Codex skill can communicate a Forge invariant but cannot technically enforce it, the Adapter MUST classify that invariant as represented-but-not-enforced and expose the limitation.

### FR-017 — No capability substitution
A skill MUST NOT be presented as a hook, command-registration primitive, agent-role primitive, or persistent-instruction primitive unless Codex explicitly defines that capability equivalence.

## 5. Planning and ownership

### FR-018 — Deterministic plan
Given identical Effective Forge Configuration, Adapter version, Codex capability evidence, and repository inputs, Codex Adapter planning MUST produce semantically identical operations in stable order.

### FR-019 — Planned artifact metadata
Every Codex artifact operation MUST use the generic planned-artifact model, including path, ownership, operation intent, and generated content or digest data required by the Core.

### FR-020 — Forge-owned generated skills
Codex skill artifacts generated entirely by Forge SHOULD be `forge_owned` and MUST be protected by installation-record digest and drift checks.

### FR-021 — Existing user artifact protection
If a planned Codex path collides with an unowned or user-owned artifact, the Adapter MUST preserve it or report conflict; it MUST NOT silently overwrite it.

### FR-022 — Shared representation requires deterministic merge
The Adapter MUST NOT classify a Codex artifact as `shared` unless it defines a deterministic, testable merge strategy. Otherwise the operation MUST be a conflict.

## 6. Limitations and conformance

### FR-023 — Explicit limitation set
The plan and installation record MUST include every Forge-required capability or invariant that the Codex projection cannot faithfully enforce.

### FR-024 — No false compliance
Conformance MUST fail or report a non-conformant limitation when required Forge semantics are neither faithfully represented nor explicitly acknowledged according to the generic conformance contract.

### FR-025 — Representation is not enforcement
Conformance output MUST distinguish at least: supported/enforced by available Adapter mechanics, represented but not technically enforced, and unsupported/unrepresented.

### FR-026 — Canonical semantics win
If Codex-native conventions conflict with canonical Forge semantics, the Adapter MUST preserve Forge semantics or report an explicit incompatibility; it MUST NOT silently weaken Forge.

## 7. Offline and distribution behavior

### FR-027 — Local planning
After Adapter code and its evidence-backed capability declaration are installed, normal manifest validation, planning, drift detection, and conformance MUST NOT require live Codex or OpenAI network access.

### FR-028 — Wheel completeness
The packaged Forge distribution MUST contain the Codex Adapter manifest, projection resources required for planning, and all runtime code required for isolated Adapter loading and validation.

### FR-029 — No Codex SDK dependency in Core
The generic Adapter Core MUST remain Harness-agnostic and MUST NOT acquire a Codex/OpenAI SDK dependency to support this Adapter.

## 8. Diagnostics

### FR-030 — Human-reviewable limitations
Adapter diagnostics MUST identify the Forge invariant/capability, Codex support classification, and reason for each limitation without implying enforcement that does not exist.

### FR-031 — Drift diagnostics
When a Forge-owned Codex artifact has been modified, diagnostics MUST identify drift and block silent replacement.

### FR-032 — Evidence staleness boundary
Capability evidence MUST be versioned or dated sufficiently for maintainers to identify when Codex capability assumptions require re-Discovery; runtime planning MUST remain deterministic and MUST NOT silently change based on live documentation.

## 9. Non-functional requirements

### NFR-001 — Harness isolation
Codex-specific modules MUST not leak Codex concepts into generic Adapter models unless a separate Architecture Decision explicitly generalizes the concept.

### NFR-002 — Testability
Projection, limitation classification, ownership behavior, determinism, and conformance MUST be testable without invoking a live Codex session.

### NFR-003 — Reviewability
Generated Codex artifacts and plans MUST be human-readable enough for Strict Review to determine which Forge semantics are represented and which remain limitations.

### NFR-004 — Conservative capability policy
False negatives in capability declaration are preferable to false claims of enforcement. Newly discovered Codex capabilities require explicit evidence and tests before support is advertised.

## 10. Invariants

### INV-001
Codex is a projection target, never Forge's semantic authority.

### INV-002
No Codex capability is claimed without evidence.

### INV-003
A Codex skill is not automatically equivalent to another capability class.

### INV-004
Generated representation cannot bypass canonical Gates.

### INV-005
User-authored Codex artifacts are never silently overwritten.

### INV-006
Generic Adapter Core remains free of Codex-specific dependencies and policy.

### INV-007
Offline planning behavior is stable; live vendor documentation cannot mutate runtime semantics implicitly.

## 11. Acceptance scenarios

### AC-001 — Adapter loads as Codex
Given the packaged Adapter registry/resources, loading the Codex Adapter returns its stable id, independent version, target `codex`, and Protocol compatibility interval.

### AC-002 — Skills supported, unverified primitives not claimed
Given the initial evidence set, capability inspection reports `skills` supported and does not report `hooks`, `commands`, `agent_roles`, or `persistent_instructions` as supported without additional evidence.

### AC-003 — Deterministic skill plan
Given identical Effective Forge Configuration and repository state, two Codex planning runs produce semantically identical, stably ordered skill operations.

### AC-004 — Gate-preserving projection
Given a FULL Flow requiring Specification Review, TDD, Verification, Strict Review, Resolution, and Completion, the generated Codex workflow representation does not instruct the Harness to skip or reorder those required Gates.

### AC-005 — Represented but unenforced invariant
Given an invariant expressible in skill instructions but lacking a technical Codex enforcement primitive, planning/conformance reports it as represented but not enforced rather than fully enforced.

### AC-006 — Unsupported capability limitation
Given a Forge requirement that requires an unverified Codex capability, planning records an explicit limitation and does not fabricate a Codex artifact that claims equivalent enforcement.

### AC-007 — User collision
Given a user-authored artifact already exists at a planned Codex path with no Forge ownership proof, planning preserves/reports conflict and application does not overwrite it.

### AC-008 — Generated drift
Given a Forge-owned Codex skill whose recorded digest no longer matches repository content, update reports drift/conflict and does not silently replace it.

### AC-009 — Offline conformance
Given an installed Forge distribution and repository fixture with no network access, Codex Adapter loading, manifest validation, planning, drift detection, and conformance complete without contacting OpenAI.

### AC-010 — Wheel isolation
Given only the built wheel installed into an isolated environment, the Codex Adapter manifest/resources load and the Adapter probe can execute without source-tree imports.

### AC-011 — Canonical state survives projection deletion
Given all generated Codex artifacts are removed, Forge Change state and canonical Flow/Contract/Policy semantics remain available from repository-native Forge sources.

### AC-012 — Evidence does not mutate runtime
Given vendor documentation changes after the installed Adapter release, repeated planning with the same installed Adapter and repository inputs remains unchanged until the Adapter capability evidence/version is deliberately updated.

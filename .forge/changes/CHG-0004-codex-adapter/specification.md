---
forge:
  artifact: specification
  schema: 1
change: CHG-0004
status: proposed
review:
  iterations: 1
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
The Codex Adapter MUST declare generic CHG-0002 capabilities as supported only when backed by authoritative current Codex documentation or an equivalent reproducible Harness contract.

### FR-005 — Confirmed skills capability
The initial Codex Adapter MUST declare the generic `skills` capability as supported.

### FR-006 — Unverified capabilities are unsupported
Until independently proven, generic capabilities `persistent_instructions`, `commands`, `hooks`, and `agent_roles` MUST NOT be declared supported merely because an analogous concept exists in another Harness.

### FR-007 — Generated files
The Adapter MAY declare `generated_files` only for repository artifacts it can deterministically plan, publish, record, and validate through the generic Adapter Core.

### FR-008 — Capability evidence traceability
Each Codex-specific capability declaration MUST have evidence metadata containing at least: capability identifier, support status, authoritative source identifier or URL, and observation date. Evidence MAY remain Codex-specific until separately generalized.

## 3. Projection boundary

### FR-009 — Effective Forge Configuration input
The Codex Adapter MUST consume Effective Forge Configuration and canonical Forge semantics through the generic Adapter boundary; it MUST NOT reinterpret raw project fragments as an alternate configuration model.

### FR-010 — Codex-specific projection only
Codex-specific code MUST be limited to translating canonical Forge requirements into Codex-oriented representation and declaring Codex limitations.

### FR-011 — No Core duplication
The Codex Adapter MUST reuse generic compatibility, planning, ownership, installation-record, drift, path-safety, publication, and conformance mechanisms rather than fork equivalent Codex-specific implementations.

### FR-012 — Repository authority
Codex-oriented artifacts MUST remain derived representation. They MUST NOT become authoritative for Change state, Flow, Contract, Policy, Review, TDD evidence, or Completion.

## 4. Skills projection

### FR-013 — Forge workflow skill projection
Where canonical Forge workflow semantics can be faithfully communicated using a Codex skill, the Adapter MUST generate deterministic skill content from canonical Forge semantics rather than maintain an independently authored semantic copy.

### FR-014 — No invented lifecycle authority
Generated skill content MAY instruct Codex how to participate in Forge workflows, but MUST NOT authorize lifecycle transitions that canonical Forge state does not permit.

### FR-015 — Gate preservation in skills
Generated skill content MUST preserve applicable canonical Gates, including Specification Review, TDD RED-before-production behavior, Verification, Strict Review, Resolution, and Completion when those Gates apply to the effective Flow.

### FR-016 — Explicit non-enforcement
When skill content can communicate a Forge invariant but no proven Codex technical enforcement primitive exists, conformance MUST classify that invariant as `represented` rather than `enforced` and expose the limitation through generic diagnostics/installation-record mechanisms.

### FR-017 — No capability substitution
The generic `skills` capability MUST NOT imply support for `hooks`, `commands`, `agent_roles`, or `persistent_instructions`. Invariant enforcement classification is separate from generic capability booleans.

### FR-018 — Projection bundle versus publication target
The Adapter MAY generate a Forge-owned Codex projection bundle/resource independently of a vendor installation path. Publication to a Codex-native filesystem/configuration path MUST occur only when that path is evidence-backed or explicitly configured by the user/project. CHG-0004 MUST NOT invent an undocumented default Codex path.

## 5. Planning and ownership

### FR-019 — Deterministic plan
Given identical Effective Forge Configuration, Adapter version, Codex capability evidence, configured/evidence-backed publication targets, and repository inputs, planning MUST produce semantically identical operations in stable order.

### FR-020 — Planned artifact metadata
Every published Codex artifact operation MUST use the generic planned-artifact model, including path, ownership, operation intent, and generated content or digest data required by the Core.

### FR-021 — Forge-owned generated projection
Codex projection resources generated entirely by Forge SHOULD be `forge_owned`; published Forge-owned artifacts MUST be protected by installation-record digest and drift checks.

### FR-022 — Existing user artifact protection
If a configured/evidence-backed publication path collides with an unowned or user-owned artifact, the Adapter MUST preserve it or report conflict; it MUST NOT silently overwrite it.

### FR-023 — Shared representation requires deterministic merge
The Adapter MUST NOT classify a Codex artifact as `shared` unless it defines a deterministic, testable merge strategy. Otherwise the operation MUST be a conflict.

## 6. Limitations and conformance

### FR-024 — Explicit limitation set
Every Forge-required capability or invariant the Codex projection cannot faithfully enforce MUST be emitted through the generic Adapter plan/conformance limitation mechanism and persisted in the generic installation-record limitation field when installed. No parallel Codex limitations store is permitted.

### FR-025 — No false compliance
Conformance MUST fail or report a non-conformant limitation when required Forge semantics are neither faithfully represented nor explicitly acknowledged according to the generic conformance contract.

### FR-026 — Enforcement classification does not redefine capabilities
For Forge invariants, Codex-specific conformance assessment MAY classify support as `enforced`, `represented`, or `unsupported`. This classification MUST remain separate from CHG-0002 generic capability declarations and MUST NOT change their schema or boolean/support semantics.

### FR-027 — Canonical semantics win
If Codex-native conventions conflict with canonical Forge semantics, the Adapter MUST preserve Forge semantics or report an explicit incompatibility; it MUST NOT silently weaken Forge.

## 7. Offline and distribution behavior

### FR-028 — Local planning
After Adapter code and its evidence-backed capability declaration are installed, normal manifest validation, projection generation, planning, drift detection, and conformance MUST NOT require live Codex or OpenAI network access.

### FR-029 — Wheel completeness
The packaged Forge distribution MUST contain the Codex Adapter manifest, capability evidence metadata, projection resources required for planning, and all runtime code required for isolated Adapter loading and validation.

### FR-030 — No Codex SDK dependency in Core
The generic Adapter Core MUST remain Harness-agnostic and MUST NOT acquire a Codex/OpenAI SDK dependency to support this Adapter.

## 8. Diagnostics

### FR-031 — Human-reviewable limitations
Adapter diagnostics MUST identify the Forge invariant/capability, generic capability status where relevant, invariant enforcement classification where relevant, and reason for each limitation without implying enforcement that does not exist.

### FR-032 — Drift diagnostics
When a Forge-owned published Codex artifact has been modified, diagnostics MUST identify drift and block silent replacement.

### FR-033 — Evidence staleness boundary
Capability evidence MUST include an observation date and source identifier so maintainers can identify when Codex assumptions require re-Discovery; runtime planning MUST remain deterministic and MUST NOT silently change based on live documentation.

## 9. Non-functional requirements

### NFR-001 — Harness isolation
Codex-specific modules MUST not leak Codex concepts into generic Adapter models unless a separate Architecture Decision explicitly generalizes the concept.

### NFR-002 — Testability
Projection, limitation classification, ownership behavior, determinism, and conformance MUST be testable without invoking a live Codex session.

### NFR-003 — Reviewability
Generated Codex projection resources and plans MUST be human-readable enough for Strict Review to determine which Forge semantics are represented and which remain limitations.

### NFR-004 — Conservative capability policy
False negatives in capability declaration are preferable to false claims of enforcement. Newly discovered Codex capabilities require explicit evidence and tests before support is advertised.

## 10. Invariants

### INV-001
Codex is a projection target, never Forge's semantic authority.

### INV-002
No generic Codex capability is claimed without evidence.

### INV-003
A Codex skill is not automatically equivalent to another generic capability class.

### INV-004
Generated representation cannot bypass canonical Gates.

### INV-005
User-authored Codex artifacts are never silently overwritten.

### INV-006
Generic Adapter Core remains free of Codex-specific dependencies and policy.

### INV-007
Offline planning behavior is stable; live vendor documentation cannot mutate runtime semantics implicitly.

### INV-008
Forge may generate Codex projection content without inventing an undocumented Codex publication path.

## 11. Acceptance scenarios

### AC-001 — Adapter loads as Codex
Given the packaged Adapter registry/resources, loading the Codex Adapter returns its stable id, independent version, target `codex`, and Protocol compatibility interval.

### AC-002 — Skills supported, unverified primitives not claimed
Given the initial evidence set, generic capability inspection reports `skills` supported and does not report `hooks`, `commands`, `agent_roles`, or `persistent_instructions` as supported without additional evidence.

### AC-003 — Evidence metadata is complete
Given each advertised Codex capability, evidence metadata includes capability, status, source identifier/URL, and observation date.

### AC-004 — Deterministic projection bundle
Given identical Effective Forge Configuration and repository state, two Codex projection-generation runs produce semantically identical, stably ordered Forge-owned projection resources.

### AC-005 — No undocumented publication path
Given no evidence-backed or explicitly configured Codex publication target, projection generation succeeds but planning does not invent a vendor-native destination path.

### AC-006 — Gate-preserving projection
Given a FULL Flow requiring Specification Review, TDD, Verification, Strict Review, Resolution, and Completion, generated Codex workflow content does not instruct the Harness to skip or reorder those required Gates.

### AC-007 — Represented but unenforced invariant
Given an invariant expressible in skill content but lacking a proven technical Codex enforcement primitive, conformance reports `represented` and records the generic limitation rather than reporting the invariant as `enforced`.

### AC-008 — Unsupported capability limitation
Given a Forge requirement that requires an unverified Codex capability, planning/conformance records an explicit generic limitation and does not fabricate equivalent enforcement.

### AC-009 — User collision
Given an explicitly configured/evidence-backed publication target already contains a user-authored artifact with no Forge ownership proof, planning preserves/reports conflict and application does not overwrite it.

### AC-010 — Generated drift
Given a Forge-owned published Codex artifact whose recorded digest no longer matches repository content, update reports drift/conflict and does not silently replace it.

### AC-011 — Offline conformance
Given an installed Forge distribution and repository fixture with no network access, Codex Adapter loading, evidence loading, projection generation, manifest validation, planning, drift detection, and conformance complete without contacting OpenAI.

### AC-012 — Wheel isolation
Given only the built wheel installed into an isolated environment, the Codex Adapter manifest/evidence/projection resources load and the Adapter probe can execute without source-tree imports.

### AC-013 — Canonical state survives projection deletion
Given all generated Codex projection/published artifacts are removed, Forge Change state and canonical Flow/Contract/Policy semantics remain available from repository-native Forge sources.

### AC-014 — Evidence does not mutate runtime
Given vendor documentation changes after the installed Adapter release, repeated planning with the same installed Adapter and repository inputs remains unchanged until Adapter evidence/version is deliberately updated.

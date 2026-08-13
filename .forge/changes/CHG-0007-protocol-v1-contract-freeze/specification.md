---
forge:
  artifact: specification
  schema: 1
change: CHG-0007
status: approved
review:
  iterations: 3
---

# Specification — Protocol v1 Contract Freeze

## Stable version identity

### FR-001 — Stable Protocol label
Forge MUST expose the integer Protocol identifier `1` with stable human label
`1`; `1-draft` MUST no longer describe current Protocol maturity.

### FR-002 — Independent version axes
Protocol, CLI, Schema, and Adapter versions MUST remain independently
versioned. Schema identifier `@1` MUST NOT be interpreted as the CLI version.

## Compatibility and evolution

### FR-003 — Protocol 1 compatibility guarantee
A change within Protocol 1 MUST preserve the meaning and minimum obligations
of existing valid Protocol 1 projects, Changes, Flows, and Adapters.

### FR-004 — Compatible evolution
Protocol 1 MAY add optional fields, optional artifacts, stronger diagnostics,
clarifications that do not change normative meaning, and new independently
versioned schemas that do not invalidate existing valid instances.

### FR-005 — Breaking evolution
A change that removes or weakens an invariant, changes an existing required
field or Gate meaning, invalidates a previously valid conforming instance, or
changes Adapter compatibility semantics MUST use a new integer Protocol
identifier.

### FR-006 — Deprecation policy
Deprecation MUST identify the affected construct, replacement, first deprecated
release or Protocol revision, compatibility period, and earliest removal
boundary. Removal MUST obey FR-005.

## Schema contract

### FR-007 — Supported-schema catalog
Forge MUST publish a portable machine-readable catalog mapping each supported
schema identifier to exactly one bundled JSON Schema file.

### FR-008 — Schema validity and identity
Every cataloged JSON Schema MUST be valid Draft 2020-12, and its root
`schema.const` identity MUST equal its catalog identifier.

### FR-009 — Canonical-instance validation
Canonical Protocol YAML and repository-native Forge artifacts governed by a
cataloged schema MUST validate against that schema in an offline contract test.

### FR-010 — Complete v1 schema surface
The catalog MUST cover project, project Flow, Change, traceability, TDD
evidence, Flow, Policy, Adapter, Adapter installation, and the schema catalog.

## Lifecycle contract

### FR-011 — Stable quality Gates
Protocol 1 MUST preserve applicable TDD/RED, Verification, Strict Review,
blocking external-review thread reconciliation, Documentation Impact, and
truthful Completion across canonical Flows.

### FR-012 — Flow proportionality
FULL, STANDARD, and FAST MAY differ in required planning artifacts, but MUST
NOT contradict or weaken the common quality Gates. FAST need not require a
formal Requirement identifier before behavioral implementation.

## Historical consistency

### FR-013 — Truth-preserving migration
Schema-invalid historical repository artifacts MUST be migrated to the stable
shape when the migration is mechanical. Existing outcomes, evidence commits,
test results, severity counts, and completion claims MUST NOT be changed merely
to satisfy schema validation. Existing acceptance mappings MAY remain an
optional top-level traceability map keyed by acceptance identifier.

## Non-functional requirement

### NFR-001 — Deterministic offline validation
Contract validation MUST run without network access and produce deterministic
results for identical repository content.

## Invariants

### INV-001 — Compatibility authority
Canonical Protocol documentation and schemas are authoritative; CLI display
metadata and Harness projections cannot redefine compatibility.

### INV-002 — Historical evidence integrity
Structural migration cannot manufacture or improve historical TDD,
Verification, Review, or Completion evidence.

## Acceptance scenarios

### AC-001 — Stable CLI identity
Given the installed current CLI, `forge version` reports `Forge Protocol 1`.

### AC-002 — Catalog closure
Given `protocol/schemas/catalog.yml`, every catalog entry resolves to a valid
bundled schema and no supported schema file is omitted.

### AC-003 — Repository contract audit
Given the repository's canonical YAML instances, every instance selected by
the contract suite validates against the schema for its identifier.

### AC-004 — Invalid Adapter interval
Given an Adapter manifest whose `min` is not lower than `max_exclusive`,
canonical Adapter validation rejects it. JSON Schema validates field types and
bounds; the existing semantic manifest validator enforces cross-field order.

### AC-005 — Common completion quality
Given each canonical Flow, its completion Gate requires Verification, Strict
Review, blocking-review-thread reconciliation, Documentation Impact, and
applicable TDD compliance or explicit exception.

### AC-006 — Historical migration
Given the pre-freeze CHG-0004 traceability facts, the migrated artifact retains
the same task and acceptance mappings while satisfying the stable schema.

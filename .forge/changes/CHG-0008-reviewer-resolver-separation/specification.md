---
forge:
  artifact: specification
  schema: 1
change: CHG-0008
status: complete
---

# Specification — Verifiable Review Independence

This specification incorporates both accepted drifts in `specification-drift.md`, including the Resolution of Strict Review Iteration 1 findings R001-R004.

## Functional requirements

### FR-001 — Protocol boundary
Independent Review Execution and Execution Context MUST be normative only under integer Protocol 2. Protocol 1 MUST preserve its historical conceptual Reviewer/Resolver separation semantics.

### FR-002 — Independent version axes
Protocol version and artifact schema version MUST remain independent. `forge/change@2` MUST NOT be presented as a substitute for the Protocol 2 boundary.

### FR-003 — Historical preservation
Completed Protocol 1 Changes and `forge/change@1` instances MUST remain valid without fabricated execution provenance.

### FR-004 — Protocol resolution
Core validation and diagnostics MUST resolve the configured Protocol before selecting Protocol-specific invariants and canonical Contract resources.

### FR-005 — Execution provenance artifact
Protocol 2 MUST provide provider-independent repository-native provenance for Implementation, Resolution, and Review executions, including Execution ID, Context ID, capture time, Role, revision binding, and evidence source.

### FR-006 — Assurance levels
Provenance MUST distinguish `claimed`, `recorded`, and `verified`. Core documentation MUST state what each level proves and MUST NOT describe arbitrary strings or self-recorded evidence as cryptographic/external proof.

### FR-007 — Minimum review assurance
`review_passed` under Protocol 2 MUST require at least `recorded` subject and Reviewer provenance. `claimed` identity alone MUST fail the Gate.

### FR-008 — Revision binding
Every passed Review Iteration MUST reference subject and Reviewer provenance bound to the same revision being reviewed.

### FR-009 — Execution independence
Reviewer and subject provenance MUST have distinct Execution IDs.

### FR-010 — Context independence
Reviewer and subject provenance MUST have distinct Execution Context IDs independently of Execution ID inequality.

### FR-011 — All-Flow enforcement
FR-007 through FR-010 MUST apply to FAST, STANDARD, and FULL under Protocol 2.

### FR-012 — Iteration-aware re-review
Review MUST be modeled as iterations. Re-review after blocking Resolution MUST target the resolved revision and compare Reviewer provenance against the Resolution provenance that produced that revision.

### FR-013 — Resolver boundary
A Resolver MUST NOT resolve blocking Findings in the Reviewer's Execution Context.

### FR-014 — Anti-forgery consistency check
A Review that references invented or nonexistent provenance identifiers MUST fail deterministic validation even when all identifier strings are pairwise distinct.

### FR-015 — Downgrade resistance
An active Protocol 2 Change MUST NOT use `forge/change@1` to bypass the Protocol 2 Strict Review Gate. Completed historical Protocol 1 Change artifacts MAY remain unchanged inside a Protocol 2 repository.

### FR-016 — Adapter projection boundary
Harness projections MUST project Protocol 2 provenance semantics only when Protocol 2 is selected; Protocol 1 projections MUST retain Protocol 1 semantics.

### FR-017 — Local/provider-independent operation
The Core provenance mechanism MUST NOT require a hosted Forge backend or provider-specific fields. Harness-native references MAY be recorded as source metadata.

### FR-018 — CHG-0008 Resolution boundary
The historical implementation provenance gap MUST be explicit and unfilled. This Resolution MUST capture its own provenance prospectively, leave Strict Re-review pending, and MUST NOT self-approve.

## Invariants

- **INV-001 — No fabricated history:** missing historical execution evidence is recorded as a gap, not reconstructed as fact.
- **INV-002 — No string-equality theater:** different strings without durable linked records are insufficient for `review_passed`.
- **INV-003 — No Protocol 1 reinterpretation:** Protocol 2 strengthening cannot change the meaning of existing Protocol 1 instances.
- **INV-004 — No self-certification:** this Resolver execution cannot satisfy Review Iteration 2.

## Acceptance criteria

- AC-001: Protocol 1 passed-review fixtures remain valid without Protocol 2 provenance.
- AC-002: Protocol 2 FAST, STANDARD, and FULL reject passed Review without provenance.
- AC-003: Protocol 2 FAST, STANDARD, and FULL accept revision-bound independent recorded provenance.
- AC-004: forged pairwise-distinct identifiers without records fail.
- AC-005: missing/partial provenance fails.
- AC-006: wrong-revision provenance fails.
- AC-007: shared Execution fails.
- AC-008: shared Context fails.
- AC-009: re-review sharing the Resolution Context fails.
- AC-010: active Protocol 2 schema downgrade fails while completed Protocol 1 history remains valid.
- AC-011: Protocol 1 Adapter projection does not receive Protocol 2 provenance semantics; Protocol 2 projection covers FAST/STANDARD/FULL.
- AC-012: canonical schemas/catalog and Protocol 2 resources package and validate offline.
- AC-013: `pytest -q`, `forge validate`, `forge doctor`, and Distribution Verification are green on the final Resolution HEAD.
- AC-014: Review Iteration 1 remains REQUEST CHANGES evidence and Review Iteration 2 remains pending for an independent Reviewer.

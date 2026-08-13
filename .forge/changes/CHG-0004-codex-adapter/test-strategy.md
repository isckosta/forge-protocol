---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0004
status: approved
---

# Test Strategy — Codex Harness Adapter

## Objective
Prove the Codex Adapter as a deterministic, offline, evidence-backed projection over the CHG-0002 Core without invoking a live Codex session.

## TDD rules
Every behavioral unit is introduced test-first. Invalid test harness/import failures do not count as RED. Production code follows only after an observed behavioral RED.

## Test levels

### Unit
- descriptor/manifest loading;
- capability evidence validation;
- invariant classification;
- projection rendering;
- publication-target resolution;
- deterministic ordering/digests.

### Integration
- Codex projection -> generic planner;
- user-owned collision and generated drift through generic Core;
- generic limitation/install-state reuse;
- canonical-state independence from generated projection deletion.

### Distribution
Build the wheel and prove descriptor, evidence, projection resources, planning and conformance load without source-tree access and with network disabled.

## Planned cycles

### TDD-001 — Descriptor and capability evidence
Cover FR-001..FR-008 and AC-001..AC-003.

### TDD-002 — Deterministic projection bundle
Cover FR-009..FR-18 and AC-004..AC-006.

### TDD-003 — Invariant assessment and limitations
Cover FR-016, FR-024..FR-027, FR-031 and AC-007..AC-008.

### TDD-004 — Publication target resolution
Cover FR-018..FR-023 and AC-005/AC-009. Prove no undocumented default path.

### TDD-005 — Generic planner/publisher integration
Cover ownership, collision, drift and generic installation-state reuse without Codex-specific filesystem mutation.

### TDD-006 — Offline and wheel isolation
Cover FR-028..FR-030, FR-033 and AC-011..AC-014.

## Safety-focused regressions
Tests must reject capability overclaim, capability-class substitution, path invention, user-owned overwrite, drift replacement, live-documentation runtime dependence and Codex-specific dependencies in generic Core.

## Verification
Final Verification requires full suite, isolated wheel, offline execution, dependency audit, deterministic repeated planning, acceptance-scenario traceability and Strict Review.
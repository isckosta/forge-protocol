---
forge:
  artifact: tasks
  schema: 1
change: CHG-0002
status: approved
---

# Tasks — Harness Adapter Foundation

## T-001 — TDD Adapter manifest schema
Requirements: FR-001..FR-007, FR-034, FR-035

Files:
- Create `protocol/schemas/adapter.schema.json`.
- Create `src/forge_cli/adapters/manifest.py`.
- Create `tests/unit/adapters/test_manifest.py`.

RED must prove missing manifest parsing/validation. GREEN adds only identity, independent Adapter version, target Harness, integer Protocol bounds, and capability vocabulary validation.

## T-002 — TDD Protocol compatibility
Requirements: FR-004, FR-005

Files:
- Modify `src/forge_cli/adapters/manifest.py`.
- Create `tests/unit/adapters/test_protocol_compatibility.py`.

Prove `min <= protocol < max_exclusive`, rejection outside the interval, and invalid manifest bounds where `min >= max_exclusive`.

## T-003 — TDD capability requirements and limitations
Requirements: FR-006..FR-009, FR-030

Files:
- Create `src/forge_cli/adapters/capabilities.py`.
- Create `tests/unit/adapters/test_capabilities.py`.

Model Adapter-declared capabilities, Forge-required representation requirements, and explicit limitations. No real Harness is involved.

## T-004 — TDD Adapter plan model
Requirements: FR-013..FR-016, FR-023, NFR-003

Files:
- Create `src/forge_cli/adapters/plan.py`.
- Create `tests/unit/adapters/test_plan.py`.

Define immutable plan/operation entities, stable ordering, ownership modes, operation intents, content digests, limitations, and conflicts.

## T-005 — TDD ownership and collision classification
Requirements: FR-017..FR-019, INV-004

Files:
- Create `src/forge_cli/adapters/ownership.py`.
- Create `tests/unit/adapters/test_ownership.py`.

Drive user-owned preserve/conflict, Forge-owned safe update only with matching expected state, and shared conflict absent an explicit deterministic merge result.

## T-006 — TDD installation record
Requirements: FR-021, FR-022, INV-002

Files:
- Create `src/forge_cli/adapters/state.py`.
- Create `protocol/schemas/adapter-installation.schema.json` if machine validation proves useful during RED.
- Create `tests/unit/adapters/test_installation_state.py`.

Serialize and load `.forge/adapters/<id>/installation.yml` deterministically without Change lifecycle duplication.

## T-007 — TDD generated drift detection
Requirements: FR-024, FR-025

Files:
- Modify `src/forge_cli/adapters/ownership.py` and/or `state.py` only where responsibility remains focused.
- Create `tests/unit/adapters/test_drift.py`.

Prove matching digests allow generated update classification and mismatched content forces drift/conflict.

## T-008 — TDD conformance checks
Requirements: FR-026..FR-030, INV-001..INV-003

Files:
- Create `src/forge_cli/adapters/validation.py`.
- Create `tests/unit/adapters/test_conformance.py`.

Prove canonical Contract/Flow authority, required stage/Gate preservation, TDD RED preservation, Strict Review preservation, and explicit limitation when enforcement is unavailable.

## T-009 — TDD deterministic Harness-agnostic planner
Requirements: FR-010..FR-013, FR-023, NFR-001, NFR-002, NFR-005

Files:
- Create `src/forge_cli/adapters/planner.py`.
- Create `tests/unit/adapters/test_planner.py`.

Planner consumes a resolved Effective Forge Configuration fixture plus repository state and returns a stable `AdapterPlan` without mutation or Harness SDK imports.

## T-010 — TDD safe Adapter publisher
Requirements: FR-017..FR-020, NFR-004

Files:
- Create `src/forge_cli/adapters/publisher.py`.
- Create `tests/integration/adapters/test_publisher.py`.

Prove repository-bound paths, no user-owned overwrite, conflict refusal, Forge-owned expected-state checks, and no successfully-installed appearance after publication failure. Include symlink/path-escape regression cases.

## T-011 — Package Adapter schemas/resources
Requirements: FR-034, FR-035, NFR-001

Files:
- Modify Protocol resource packaging only as required.
- Create/modify distribution tests.

Build an isolated wheel and prove Adapter schemas resolve without source-tree or network access.

## T-012 — Update canonical Protocol documentation
Requirements: all semantic requirements

Files:
- Modify `protocol/specification.md`.
- Modify `ARCHITECTURE.md`.
- Modify `README.md`.
- Modify `CHANGELOG.md`.
- Update `docs/rfcs/0002-harness-adapter-foundation.md` to Accepted only after implementation agrees with RFC semantics.

## T-013 — Execute complete Verification
Verify all Requirements and acceptance scenarios, deterministic repeated plans, installation-state roundtrip, path safety, wheel isolation, offline operation, and dependency audit.

## T-014 — Execute Strict Review
Review the implementation adversarially. Blocking Findings are resolved through regression-first TDD and then re-reviewed before Completion.

---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0008
status: approved
---

# Test Strategy — Adapter CLI and Codex Installation UX

## Objective

Prove the complete Adapter CLI as deterministic, offline, ownership-safe, and
usable from an installed wheel without invoking a live Codex session.

## TDD rule

Every behavioral task begins with a focused automated test that is executed and
fails for the intended missing behavior. Import, fixture, syntax, setup, and
environment failures do not count as RED. Production behavior follows only an
auditable valid RED; each cycle records requirement, command, failure reason,
GREEN revision, and result in `tdd-evidence.yml`.

## Test levels

### Unit

- immutable registry ordering, lookup, and duplicate rejection;
- configuration schema, atomic serialization, and target validation;
- target precedence and packaged Codex publication evidence;
- skill frontmatter, references, ordering, and deterministic digests;
- `UNCHANGED`, collision, update, drift, and obsolete-path planning;
- findings, stable error codes, and deterministic formatting.

### Integration

- effective project/Flow/Contract resolution through the driver boundary;
- service plan/install/update state machines;
- record completeness and version transitions;
- publisher mixed create/update/delete rollback;
- read-only validate/doctor behavior and remediation;
- Typer command behavior, output, exit codes, and dry-run parity.

### Distribution and acceptance

Build an isolated wheel, install it without source-tree imports, create a Git
fixture, execute the golden path, prove no-op timestamps/bytes, inject drift,
prove mutation refusal, restore recorded state, and prove a safe update. Runtime
Adapter operations execute with vendor network access disabled.

## Planned TDD cycles

### TDD-001 — Generic driver registry

Cover FR-002, FR-003, NFR-003, and AC-002.

### TDD-002 — Adapter configuration and target evidence

Cover FR-005 through FR-007, FR-023, and AC-009/AC-011.

### TDD-003 — Valid deterministic Codex skill

Cover FR-008 through FR-010, FR-022, NFR-001, and AC-010. Projection remains pure; canonical survival is verified at the publisher cleanup boundary in TDD-004.

### TDD-004 — Ownership-aware plan transitions

Cover FR-011 through FR-019, NFR-002, INV-002/INV-004, and
AC-003 through AC-008 plus AC-012, including a publisher cleanup test with separate canonical and generated trees.

### TDD-005 — Generic Adapter service

Cover FR-004, FR-008, FR-012 through FR-019, INV-001/INV-003, and
AC-001/AC-005/AC-006/AC-011.

### TDD-006 — Validation and doctor

Cover FR-020 through FR-023 and AC-007/AC-010/AC-011.

### TDD-007 — Public Adapter CLI

Cover FR-001 through FR-007, FR-011, FR-015/FR-016, FR-020/FR-021,
FR-023, NFR-004, and AC-001 through AC-003/AC-005/AC-009.

### Distribution Verification / conditional TDD-008 — Installed-wheel golden path

Cover FR-024, INV-005, and all acceptance scenarios at distribution level. The
first executable run is Verification when it passes against behavior already
implemented by earlier cycles. It is credited as TDD-008 only when it fails on
a genuine missing product or packaging behavior and precedes the corresponding
production/package fix. Environment, import, collection, and dependency setup
failures never count as RED.

## Safety regressions

Tests MUST reject silent adoption of equal unrecorded bytes, path traversal,
absolute/global targets, symlink traversal, malformed or identity-mismatched
records, partial publication, deletion after drift, limitation overclaim, live
vendor dependency, and mutation by plan/validate/doctor.

## Verification

Final Verification requires focused tests, the full suite, `git diff --check`,
schema/traceability closure, isolated-wheel golden path, deterministic repeated
planning, no-op timestamp/byte proof, mixed rollback proof, offline runtime,
and an explicit tracked/untracked file audit.

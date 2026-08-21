---
forge:
  artifact: tasks
  schema: 1
change: CHG-0021
status: in_progress
---

# Tasks — Adapter Reference Schema Projection

- [ ] T-001 `render_decision_rules_reference()` in `validation/__init__.py` (Plan 1)
- [ ] T-002 Sharpen `resolved_via` error message (Plan 2)
- [ ] T-003 `decision_rules_content` field on `AdapterProjectionContext` (Plan 3)
- [ ] T-004 Wire `render_decision_rules_reference()` in `adapters/service.py`, both sites (Plan 4)
- [ ] T-005 Thread `context.decision_rules_content` through both Adapters' `driver.py` (Plan 5)
- [ ] T-006 Claude Code `projection.py` plumbing (Plan 6)
- [ ] T-007 Codex `projection.py` plumbing (Plan 7)
- [ ] T-008 `tests/unit/test_decision_rules_reference.py` (Plan 8, TDD-001)
- [ ] T-009 Extend both Adapters' projection-bundle tests (Plan 9, TDD-002/003/005/006)
- [ ] T-010 Extend `test_unresolved_decisions.py` (Plan 10, TDD-004)
- [ ] T-011 Regression baseline before/after (Plan 11, TDD-007)
- [ ] T-012 Assemble `tdd-evidence.yml`, `traceability.yml`, `verification.md`, `manifest.yml` (Plan 12)

## Status

Not started. Plan just reached `tasks_ready`; per Plan's Implementation
Boundary, this is not yet authorization to begin — that authorization is
recorded separately in `provenance.yml`'s `implementation-001` record
once given.

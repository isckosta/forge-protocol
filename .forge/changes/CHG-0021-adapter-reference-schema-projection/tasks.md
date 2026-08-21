---
forge:
  artifact: tasks
  schema: 1
change: CHG-0021
status: complete
---

# Tasks — Adapter Reference Schema Projection

- [x] T-001 `render_decision_rules_reference()` in `validation/__init__.py` (Plan 1)
- [x] T-002 Sharpen `resolved_via` error message (Plan 2)
- [x] T-003 `decision_rules_content` field on `AdapterProjectionContext` (Plan 3)
- [x] T-004 Wire `render_decision_rules_reference()` in `adapters/service.py`, both sites (Plan 4)
- [x] T-005 Thread `context.decision_rules_content` through both Adapters' `driver.py` (Plan 5)
- [x] T-006 Claude Code `projection.py` plumbing (Plan 6)
- [x] T-007 Codex `projection.py` plumbing (Plan 7)
- [x] T-008 `tests/unit/test_decision_rules_reference.py` (Plan 8, TDD-001/TDD-006)
- [x] T-009 Extend both Adapters' projection-bundle tests (Plan 9, TDD-002/003/005)
- [x] T-010 Extend `test_unresolved_decisions.py` (Plan 10, TDD-004)
- [x] T-011 Regression baseline before/after (Plan 11, TDD-007)
- [x] T-012 Assemble `tdd-evidence.yml`, `traceability.yml`, `verification.md`, `manifest.yml` (Plan 12)

## Status

All twelve tasks complete. One unplanned correction surfaced during T-009
(`tests/integration/adapter_cli_wheel_probe.py`'s hardcoded reference-link
expectation) — see `tdd-evidence.yml` notes and `verification.md` "What
Required Correction During Implementation Itself". `verification.md`
records the regression baseline comparison; `tdd-evidence.yml` records
per-cycle RED/GREEN evidence.

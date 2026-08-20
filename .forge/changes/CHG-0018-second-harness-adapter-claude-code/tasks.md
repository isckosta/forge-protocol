---
forge:
  artifact: tasks
  schema: 1
change: CHG-0018
status: complete
---
# Tasks — CHG-0018

- [x] T-001 Relocate `assess_invariant`/`to_generic_limitation` to
      `adapters/assessment.py`; update `codex/driver.py`'s import.
- [x] T-002 Strip `.codex` from `adapters/configuration.py` and
      `adapter-configuration.schema.json`; update
      `test_adapter_configuration.py`; add the Codex-owned equivalent
      test.
- [x] T-003 New `claude_code/` package: resources
      (`adapter.yml`/`capabilities.yml`/`publication.yml`/skill template),
      `descriptor.py`, `evidence.py`, `targets.py`.
- [x] T-004 RED: write tests for `claude_code/projection.py` (Skill,
      CLAUDE.md pointer, hook) and `claude_code/driver.py` against the
      not-yet-existing implementation; execute; confirm failure for the
      expected reason.
- [x] T-005 GREEN: implement `projection.py`/`driver.py`.
- [x] T-006 Registration: `adapters/packaged.py`.
- [x] T-007 Shared/parametrized conformance test suite over both drivers.
- [x] T-008 Refactor as needed; all TDD cycles remain GREEN throughout
      (C-014).
- [x] T-009 `C-074` in both Contract files.
- [x] T-010 `pytest -q`, `forge validate`, `forge doctor`, plus a real
      `forge adapter install claude-code` against a fresh scratch
      repository — record exact results against the pre-Implementation
      baseline.
- [x] T-011 `docs/adr/0016-*.md` (number re-verified immediately before
      writing).
- [x] T-012 Dogfooded Golden Path: install into a scratch repository,
      carry a real Change through Intent through Strict Review as the
      live Harness, record evidence under
      `examples/golden-path-claude-code/`.
- [x] T-013 `CHANGELOG.md`, `ROADMAP.md` status flip, `knowledge-capture.md`,
      `traceability.yml`, `tdd-evidence.yml`.
- [x] T-014 Freeze Implementation subject, record provenance.
- [x] T-015 Independent Strict Review Iteration 1 (separate Execution/
      Context) — PASS, 1 non-blocking MINOR (R001).
- [x] T-016 Resolution of R001 + Resolution provenance.
- [x] T-017 Independent Resolution Verification (separate Execution/
      Context again) — PASS, 0 new material findings, 1 new non-blocking
      OBSERVATION (R002, an unrelated pre-existing Core freeze-check
      finding, confirmed at Completion to resolve the same way `CHG-0017`'s
      own instance of it did).
- [x] T-018 Completion: all FULL Gates satisfied.

## Status

All tasks complete. `manifest.yml` `state.current: complete`.

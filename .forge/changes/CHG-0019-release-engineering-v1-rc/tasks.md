---
forge:
  artifact: tasks
  schema: 1
change: CHG-0019
status: complete
---
# Tasks — CHG-0019

- [x] T-001 `pyproject.toml`: dynamic version sourcing +
      authors/urls/classifiers/keywords.
- [x] T-002 RED: write tests for `migration.py` against copied fixtures;
      execute; confirm failure for the expected reason.
- [x] T-003 GREEN: implement `migration.py`, `forge migrate`/`--check`
      commands, the `doctor.py` advisory check.
- [x] T-004 `C-075` in both Contract files.
- [x] T-005 `.github/workflows/publish.yml`; `verification.yml` cleanup
      (stale branch triggers removed, sdist check added).
- [x] T-006 `RELEASING.md`; `CHANGELOG.md` convention line; `ROADMAP.md`
      version-string correction.
- [x] T-007 Refactor as needed; all TDD cycles remain GREEN throughout
      (C-014).
- [x] T-008 `pytest -q`, `forge validate`, `forge doctor`, `forge migrate
      --check` (against this repo, real six-candidate report), `python -m
      build` (wheel + sdist) — record exact results against the
      pre-Implementation baseline.
- [x] T-009 `docs/adr/0017-*.md` (number re-verified immediately before
      writing).
- [x] T-010 `knowledge-capture.md`, `traceability.yml`, `tdd-evidence.yml`.
- [x] T-011 Freeze Implementation subject, record provenance.
- [x] T-012 Independent Strict Review Iteration 1 (separate Execution/
      Context) — PASS, 2 non-blocking MINOR (R001, R002), 1 OBSERVATION
      (O001).
- [x] T-013 Resolution of R001/R002/O001 + Resolution provenance.
- [x] T-014 Independent Resolution Verification (separate Execution/
      Context again) — PASS, 0 new material findings, 1 new non-blocking
      OBSERVATION (O002, the same pre-existing C-026 freeze-check
      mechanism `CHG-0017`/`CHG-0018` already encountered, confirmed at
      Completion to resolve the same way).
- [x] T-015 Completion: all FULL Gates satisfied.

## Status

All tasks complete. `manifest.yml` `state.current: complete`.

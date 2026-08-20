---
forge:
  artifact: tasks
  schema: 1
change: CHG-0019
status: ready
---
# Tasks — CHG-0019

- [ ] T-001 `pyproject.toml`: dynamic version sourcing +
      authors/urls/classifiers/keywords.
- [ ] T-002 RED: write tests for `migration.py` against copied fixtures;
      execute; confirm failure for the expected reason.
- [ ] T-003 GREEN: implement `migration.py`, `forge migrate`/`--check`
      commands, the `doctor.py` advisory check.
- [ ] T-004 `C-075` in both Contract files.
- [ ] T-005 `.github/workflows/publish.yml`; `verification.yml` cleanup
      (stale branch triggers removed, sdist check added).
- [ ] T-006 `RELEASING.md`; `CHANGELOG.md` convention line; `ROADMAP.md`
      version-string correction.
- [ ] T-007 Refactor as needed; all TDD cycles remain GREEN throughout
      (C-014).
- [ ] T-008 `pytest -q`, `forge validate`, `forge doctor`, `forge migrate
      --check` (against this repo, real six-candidate report), `python -m
      build` (wheel + sdist) — record exact results against the
      pre-Implementation baseline.
- [ ] T-009 `docs/adr/0017-*.md` (number re-verified immediately before
      writing).
- [ ] T-010 `knowledge-capture.md`, `traceability.yml`, `tdd-evidence.yml`.
- [ ] T-011 Freeze Implementation subject, record provenance.
- [ ] T-012 Independent Strict Review Iteration 1 (separate Execution/
      Context).
- [ ] T-013 Resolution (if any Findings require one) + Resolution
      provenance.
- [ ] T-014 Independent Resolution Verification (if T-013 ran) —
      separate Execution/Context again.
- [ ] T-015 Completion: all FULL Gates satisfied.

## Status

Ready. Implementation not started.

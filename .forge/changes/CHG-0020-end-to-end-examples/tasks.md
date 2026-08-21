---
forge:
  artifact: tasks
  schema: 1
change: CHG-0020
status: ready
---
# Tasks — CHG-0020

- [x] T-001 `examples/strict-review-remediation/README.md`.
- [x] T-002 `examples/full-feature/README.md`.
- [x] T-003 Addenda on both existing golden-path READMEs.
- [x] T-004 `examples/README.md` rewrite.
- [x] T-005 `ROADMAP.md` status line.
- [x] T-006 Verify every cited commit hash/excerpt against real `git
      show`/file content; `pytest -q`/`forge validate`/`forge doctor`
      unchanged.
- [x] T-007 `knowledge-capture.md`, `traceability.yml`.
- [x] T-008 Freeze Implementation subject, record provenance.
- [x] T-009 Independent Strict Review Iteration 1 (separate Execution/
      Context).
- [ ] ~~T-010~~ **Not performed, by design.** Iteration 1 (`36cabf2`)
      returned PASS with zero BLOCKER/MAJOR/MINOR/OBSERVATION Findings —
      there is nothing to resolve. Left unchecked with the reason
      recorded, matching `CHG-0017/tasks.md` T-013's own convention for a
      task not performed by design.
- [ ] ~~T-011~~ **Not performed, by design.** Resolution Verification is
      only meaningful once a Resolution exists; T-010 did not run.
- [x] T-012 Completion: all STANDARD Gates satisfied (Verification
      passed, Review passed with 0 Findings of any severity,
      Documentation Impact evaluated and updated, Knowledge Capture
      complete).

## Status

All tasks complete or explicitly not performed by design (T-010, T-011).
`manifest.yml` `state.current: complete`.

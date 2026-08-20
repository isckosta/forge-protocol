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
- [ ] T-009 Independent Strict Review Iteration 1 (separate Execution/
      Context).
- [ ] T-010 Resolution (if any Findings require one) + Resolution
      provenance.
- [ ] T-011 Independent Resolution Verification (if T-010 ran).
- [ ] T-012 Completion: all STANDARD Gates satisfied.

## Status

T-001..T-006 done: five READMEs written/edited, every cited commit hash
and quoted excerpt verified against real `git show`/file content,
`pytest -q` (524 passed), `forge validate`, and `forge doctor` all
confirmed unchanged from the pre-Implementation baseline. Proceeding to
T-007 (knowledge-capture.md, traceability.yml).

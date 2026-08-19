---
forge:
  artifact: tasks
  schema: 1
change: CHG-0015
status: ready
---
# Tasks — CHG-0015

- [ ] T-001 Add `protocol/schemas/execution-provenance-v2.schema.json`
      (`forge/execution-provenance@2`); register in `catalog.yml`.
- [ ] T-002 Add C-060–C-066 to `protocol/contract/engineering.md`.
- [ ] T-003 Append the identical C-060–C-066 to
      `protocol/versions/2/contract/engineering.md`.
- [ ] T-004 Add §40 ("Delegated Execution Authority") to
      `protocol/specification.md`.
- [ ] T-005 Add a compatibility subsection to `protocol/compatibility.md`.
- [ ] T-006 Add one sentence to `ARCHITECTURE.md` §27.
- [ ] T-007 RED: write TDD-001 through TDD-016 against the not-yet-existing
      `_delegated_execution_effect`/`_validate_delegated_authority`;
      execute; confirm failure for the expected reason (C-009/C-010/C-011),
      not an environment failure.
- [ ] T-008 GREEN: implement `_delegated_execution_effect` and
      `_validate_delegated_authority` in
      `src/forge_cli/validation/__init__.py`, wired into `validate_project`.
- [ ] T-009 Refactor as needed; all of TDD-001–TDD-016 remain GREEN
      throughout (C-014).
- [ ] T-010 `pytest -q`, `forge validate`, `forge doctor` — record exact
      counts against the pre-Implementation baseline `plan.md` recorded
      (`f41f45e`: "Forge project is valid").
- [ ] T-011 `docs/adr/0013-delegated-execution-authority-boundaries.md`;
      `knowledge-capture.md`; RFC requirement evaluated per F-008;
      `traceability.yml`; `tdd-evidence.yml` (all produced from real
      Implementation evidence, not drafted ahead of it — `plan.md` §7).
- [ ] T-012 Freeze Implementation subject; record `role: implementation`
      provenance (`assurance: recorded`).
- [ ] T-013 Independent Strict Review (`kind: initial_review`, separate
      Execution/Context from Implementation).
- [ ] T-014 Resolve any blocking Findings; independent Resolution
      Verification if needed (separate Execution/Context again).
- [ ] T-015 Completion: verify every FULL Gate satisfied (Verification
      passed, Review passed, Documentation Impact evaluated and updated,
      Knowledge Capture complete, no unresolved BLOCKER Findings).

## Status

No task above is started. Per `plan.md`'s Explicit boundary, T-007 onward
(Implementation) requires a separate, explicit human go-ahead — distinct
from the go-ahead that reached this Plan/Tasks stage. `manifest.yml`
`state.current: tasks`, `artifacts.tasks: ready` (not `complete`):
`tasks_ready` describes this checklist being ready to execute, not having
been executed.

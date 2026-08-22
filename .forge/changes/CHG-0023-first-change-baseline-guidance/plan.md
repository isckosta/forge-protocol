---
forge:
  artifact: plan
  schema: 1
change: CHG-0023
status: active
---

# Plan — First-Change Baseline Guidance

1. Apply any accepted Specification Review corrections and record the
   approved Specification before implementation.
2. Add identical C-076 semantics to `protocol/contract/engineering.md` and
   `protocol/versions/2/contract/engineering.md`, after RFC-0003 already
   exists, without changing any schema or Flow file.
3. Write focused workflow-resource tests for the Codex and Claude Code
   templates, run their RED states, and record exact failures.
4. Add identical explicit baseline guidance to both packaged
   `resources/skills/workflow.md` templates.
5. Create the clearly labeled illustrative
   `examples/first-change-baseline/README.md` and add its mapping to
   `examples/README.md` while preserving the existing five category rows.
6. Run focused GREEN tests, then assemble `specification-review.md`,
   `test-strategy.md`, `tasks.md`, `tdd-evidence.yml`, `traceability.yml`,
   `verification.md`, and `manifest.yml` from actual evidence.
7. Freeze the Implementation subject, record repository-native provenance,
   and obtain independent cold Strict Review. Resolve any blocking finding
   in a separate Resolution commit and independently re-review the concrete
   Resolution revision.
8. Update `ROADMAP-REMEDIATION.md` item #3, `knowledge-capture.md`, and any
   required documentation status, then run final validation and prepare the
   PR.

## Implementation Boundary

Reaching `tasks_ready` is not authorization to begin Implementation.
Implementation-time discoveries belong in Verification, a Decision record,
or a documented re-Plan, not in a silent edit to this approved Plan.

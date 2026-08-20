---
forge:
  artifact: plan
  schema: 1
change: CHG-0020
status: approved
---
# Plan — CHG-0020

1. `examples/strict-review-remediation/README.md` (new) — FR-001.
2. `examples/full-feature/README.md` (new) — FR-002.
3. `examples/golden-path-standard/README.md`,
   `examples/golden-path-claude-code/README.md` — addenda (FR-003).
4. `examples/README.md` — rewrite (FR-004).
5. `ROADMAP.md` — status line (FR-005).
6. Verification: every cited commit hash/Finding excerpt checked against
   real `git show`/file content.
7. Documentation: `knowledge-capture.md`, `traceability.yml` (no
   `tdd-evidence.yml` — TDD is not applicable, no executable behavior).
8. Strict Review: adversarial, evaluating in particular CON-001 (every
   citation genuinely accurate, not paraphrased into inaccuracy).

## Validation Strategy

`pytest -q`, `forge validate`, `forge doctor` — confirm unchanged before
and after (no code touched). Every citation spot-checked against `git
show`/file content.

## Compatibility Impact

None: documentation only.

## Implementation Boundary

This Plan's own approval (this session's plan-mode approval) is the
explicit go-ahead for Implementation. `tasks.md` below has every task
unchecked; none has been started as of this Plan's own approval.

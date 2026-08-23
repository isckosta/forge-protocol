---
forge:
  artifact: test_design
  schema: 1
change: CHG-0026
status: complete
---

# Test Design — Skill Propagation Diagnostics

## Objective

Prove that a successful Adapter installation gives an actionable skill
discovery fallback and that both projected workflow templates disclose the
same Harness-runtime limitation.

## Regression Cases

- Invoke `forge adapter install codex` in an initialized temporary project and
  assert the success output warns about possible catalog delay and names
  `.agents/skills/forge/SKILL.md`.
- Read the packaged Codex workflow template and assert the limitation and its
  non-enforcement boundary are present.
- Project the Claude Code skill from its packaged template and assert the same
  limitation is present in the generated `SKILL.md`.

The three expectations were created and executed before the production edit;
the unmodified implementation produced three expected assertion failures.

## Compatibility Guard

Existing install success, dry-run, idempotence, conflict, and Adapter
projection tests remain in the applicable suites. The change must not alter
publication operations or installation state.

## Completion Criteria

The three focused cases pass, the Adapter command/projection tests remain
green, `forge validate` passes, and the full suite's environment-only wheel
limitation is recorded honestly if it remains present.

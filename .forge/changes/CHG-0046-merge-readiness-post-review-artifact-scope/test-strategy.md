---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0046
status: complete
---

# Test Strategy — CHG-0046 Merge Readiness Post Review Artifact Scope

## Objective

Prove FR-001 and FR-002 behaviorally, at the same `tests/cli/test_merge_check.py`
level as the existing merge-readiness suite (CLI-level, real Git fixture
repos, no mocking of `evaluator.py` internals) — consistent with this
repository's own existing test style for this module — and prove AC-001
through AC-005 as five independent, individually-failing-without-the-fix
test cases.

## Strategy

Extend `tests/cli/test_merge_check.py` using its existing `_manifest()`/
`_commit()` fixture helpers (already TDD-001/002-shaped: build a disposable
`tmp_path` Git repo, write `.forge/forge.yml` + `.forge/flows/standard.yml`,
freeze a Change directory, commit, invoke `forge change merge-check` via
`CliRunner`, assert on stdout/exit code). No new test infrastructure is
needed. Each TDD cycle below runs RED against the unmodified evaluator/
policy first (confirmed to fail for the *expected* reason: MR-015 or
MR-017 firing where it must not, or passing where it must fail).

## TDD-001 — MR-015 tolerates Change-local artifacts once complete (AC-001)

Freeze a Change (subject commit `S`, `state.current: complete`,
`manifest.yml`/`provenance.yml`/`review.md` recorded, matching the existing
`test_merge_check_accepts_complete_change_without_material_runtime_diff`
fixture shape). Commit a further Change-local file
(`knowledge-capture.md`) after `S`, still within `change_root`, with no
other change. Assert `forge change merge-check` reports `MERGE READY` and
`MR-015` does not appear in stdout.

RED (today): `MR-015` fires — this is CHG-0045/PR-#36's exact failure
mode, reproduced as a minimal fixture.

## TDD-002 — MR-015 still fires before Completion (AC-003)

Same freeze, but `state.current` is `review` (or any non-`complete` value)
at `head_revision` when the same kind of Change-local file is added after
`S`. Assert `MR-015` still fires and exit code is `1`.

RED (before the fix, this already passes — this cycle instead guards that
implementing TDD-001 does not silently drop the non-complete case; write
it to fail if the fix is implemented as an unconditional `change_root`
allowance instead of a state-conditioned one).

## TDD-003 — AC-002's narrower guarantee: this Change does not touch `change_root`-external handling

Same freeze scenario as TDD-001 (`state.current: complete`), but the
post-`S` commit modifies a file outside the Change's own directory (e.g.
`src/probe.py`, a throwaway fixture module) instead of a Change-local one.
Assert `forge change merge-check`'s outcome for that specific file is
identical before and after this Change's diff is applied (this is a
characterization test, not a behavior-change test — it documents, and
guards against regressing further, the pre-existing gap Discovery and
Specification's Out of Scope name explicitly; it must not start passing
for a different reason than it does today).

## TDD-004 — MR-017 resolves the ten Adapter-generated paths (AC-004)

Parametrized over the ten paths Discovery identified
(`.claude/CLAUDE.md`, `.claude/skills/forge/SKILL.md`,
`.claude/skills/forge/hooks/check-manifest-edit.sh`,
`.claude/skills/forge/references/artifact-structure.md`,
`.claude/skills/forge/references/engineering-contract.md`,
`.agents/skills/forge/SKILL.md`,
`.agents/skills/forge/references/artifact-structure.md`,
`.agents/skills/forge/references/engineering-contract.md`,
`.forge/adapters/claude-code/installation.yml`,
`.forge/adapters/codex/installation.yml`). For each, assert
`classify_path(path, load_materiality_policy())` returns `material` (per
Architecture's resolution — none resolve to `non_material`).

RED (today): each currently returns `ambiguous`.

## TDD-005 — MR-017's fallback stays `ambiguous` for everything else (AC-005)

Reuse the existing `test_ambiguous_unclassified_diff_is_blocked` case
(`unclassified.data`, an arbitrary top-level path matching none of the ten
added rules and none of the pre-existing rules) unmodified as a regression
guard. It must still pass unmodified after this Change — its presence in
the untouched suite already proves AC-005; no new test is required beyond
confirming it is not broken.

## Completion Criteria

- TDD-001 through TDD-004 are new tests, each RED-before-GREEN against the
  unmodified `evaluator.py`/`merge-readiness.yml`, each GREEN after
  Architecture's changes, recorded in `tdd-evidence.yml`.
- TDD-005 (pre-existing `test_ambiguous_unclassified_diff_is_blocked`) and
  every other pre-existing test in `tests/cli/test_merge_check.py` and the
  wider suite pass unmodified — no existing assertion is loosened,
  deleted, or rewritten to accommodate this Change.
- `forge validate`/`forge doctor` remain clean against this repository's
  own real state throughout.

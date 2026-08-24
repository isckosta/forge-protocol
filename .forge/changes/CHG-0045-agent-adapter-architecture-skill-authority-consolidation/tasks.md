---
forge:
  artifact: tasks
  schema: 1
change: CHG-0045
status: ready
---
# Tasks — CHG-0045

- [ ] T-001 RED: write TDD-001/TDD-003/TDD-004 against the not-yet-created
      shared `review_independence.py` (Plan item 1).
- [ ] T-002 GREEN: create `src/forge_cli/adapters/review_independence.py`;
      update `claude_code/projection.py` and `codex/projection.py` to
      import it, removing both local constants (Plan items 1-3).
- [ ] T-003 RED: write TDD-002/TDD-005 against the current
      per-Flow-duplicated `_gate_instructions()` (Plan item 2).
- [ ] T-004 GREEN: rework `_gate_instructions()` so the independence block
      renders once with per-Flow pointers, and the CHG-0025/C-077 sentence
      is not re-embedded (Plan item 2).
- [ ] T-005 RED: write TDD-006 against the current generator/installed-file
      mismatch (Plan item 2; expected to fail for the exact reason
      Discovery documented).
- [ ] T-006 RED: write TDD-007/TDD-013 against the current `workflow.md`
      (missing Bootstrap drift-check and boundary-reporting instructions)
      (Plan item 4).
- [ ] T-007 GREEN: update `workflow.md` with the Bootstrap drift-check and
      boundary-reporting paragraphs, reorganized per FR-005 (Plan item 4).
- [ ] T-008 RED: write TDD-009/TDD-010/TDD-011 against the current
      Bash-only hook frontmatter/script (Plan item 5).
- [ ] T-009 GREEN: extend `_hook_frontmatter_lines()` and
      `_hook_script_content()` for `Edit`/`Write`; update the disclosure
      prose (Plan item 5).
- [ ] T-010 Confirm TDD-012 (existing Bash guard regression suite) still
      passes unchanged against the extended script.
- [ ] T-011 Write TDD-008/TDD-014 once T-004/T-007/T-009's concrete output
      shape exists (Plan item 6).
- [ ] T-012 Write TDD-015 (Codex regression) (Plan item 7).
- [ ] T-013 `git add` the existing, currently-untracked
      `.forge/adapters/*/installation.yml` as a baseline-only commit,
      before any Adapter republish in this Change (Plan item 10, DEC-004).
- [ ] T-014 Write and run TDD-016 (real `git worktree add` fixture,
      `resolve_project_root` resolution) (Plan item 9).
- [ ] T-015 Write and run TDD-017 (installation record visible in a second
      worktree post-commit) (Plan item 11; depends on T-013).
- [ ] T-016 Run `forge adapter update claude-code` and `forge adapter
      update codex` against this repository; confirm `forge validate`/
      `forge doctor` clean (Plan items 12-13).
- [ ] T-017 Evaluate Documentation Impact; update `CHANGELOG.md` and, if
      DEC-002 meets the F-008 Material-Architecture-Change threshold, add
      an ADR (Plan item 14).
- [ ] T-018 Write `verification.md`, `knowledge-capture.md`,
      `traceability.yml` from real Implementation evidence (Plan item 15).
- [ ] T-019 Strict Review, independent Execution/Context (Plan item 16).

## Status

Not started. No task above has begun as of this Plan's own authorship.
T-001 (first RED) is blocked on the Plan/Implementation boundary stated
in `plan.md`'s Implementation Boundary section: an explicit, recorded
human Plan Decision under C-077, not yet obtained.

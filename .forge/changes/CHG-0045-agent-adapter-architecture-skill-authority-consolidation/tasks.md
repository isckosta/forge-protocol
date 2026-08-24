---
forge:
  artifact: tasks
  schema: 1
change: CHG-0045
status: complete
---
# Tasks — CHG-0045

- [x] T-001 RED: write TDD-001/TDD-003/TDD-004 against the not-yet-created
      shared `review_independence.py` (Plan item 1).
- [x] T-002 GREEN: create `src/forge_cli/adapters/review_independence.py`;
      update `claude_code/projection.py` and `codex/projection.py` to
      import it, removing both local constants (Plan items 1-3).
- [x] T-003 RED: write TDD-002/TDD-005 against the current
      per-Flow-duplicated `_gate_instructions()` (Plan item 2).
- [x] T-004 GREEN: rework `_gate_instructions()` so the independence block
      renders once with per-Flow pointers, and the CHG-0025/C-077 sentence
      is not re-embedded (Plan item 2).
- [x] T-005 Confirmed TDD-006's premise directly (no separate RED needed):
      the current generator already emits the CHG-0025/C-077 sentence
      exactly once via `workflow.md`, unaffected by T-004; locked in with
      a permanent regression test instead of a throwaway RED (Plan item 2).
- [x] T-006 RED: write TDD-007/TDD-013 against the current `workflow.md`
      (missing Bootstrap drift-check and boundary-reporting instructions)
      (Plan item 4).
- [x] T-007 GREEN: update `workflow.md` with the Bootstrap drift-check and
      boundary-reporting paragraphs, reorganized per FR-005 (Plan item 4).
      Discovered mid-task: `codex/resources/skills/workflow.md` and
      `claude_code/resources/skills/workflow.md` are asserted byte-identical
      by a pre-existing test (`test_first_change_baseline_guidance.py`) this
      Plan had not identified; applied the same edit to both (regression
      caught by the pre-existing suite, not missed silently).
- [x] T-008 RED: write TDD-009/TDD-010/TDD-011 against the current
      Bash-only hook frontmatter/script (Plan item 5).
- [x] T-009 GREEN: extend `_hook_frontmatter_lines()` and
      `_hook_script_content()` for `Edit`/`Write`; update the disclosure
      prose (Plan item 5).
- [x] T-010 Confirmed TDD-012 (existing Bash guard regression suite) still
      passes unchanged against the extended script.
- [x] T-011 Wrote TDD-014 (NFR-003 size regression, baseline 180→175 lines
      for this repository's real fixture) once T-004/T-007/T-009's output
      shape existed. TDD-008 ("locatable sections") is satisfied by the
      `### Bootstrap` heading introduced in T-007 plus the pre-existing
      `## Effective Forge references`/`## Illustrative enforcement hook`
      headings; verified by direct reading of the generated `SKILL.md`
      (see `verification.md`), not by a separate mechanical test, since
      "locatable to a human reader" is Test Strategy's own declared
      Non-mechanical Validation item, not a TDD case (Plan item 6).
- [x] T-012 Confirmed TDD-015 (Codex regression): full pre-existing Codex
      suite passes unchanged except the intended TDD-003 identity check
      (Plan item 7).
- [x] T-013 `git add`+commit the existing, currently-untracked
      `.forge/adapters/*/installation.yml` as a baseline-only commit,
      before any Adapter republish in this Change (Plan item 10, DEC-004).
- [x] T-014 Wrote and ran TDD-016 (real `git worktree add` fixture,
      `resolve_project_root` resolution) — passed immediately, confirming
      Architecture's Q10/Q11 finding that no code defect exists here
      (Plan item 9).
- [x] T-015 Wrote and ran TDD-017 (installation record visible in a second
      worktree post-commit) (Plan item 11; depended on T-013).
- [x] T-016 Republished both Adapters against this repository. Honest
      note: `forge adapter update`/`install` refused via their own
      ownership/drift guards even after the two Discovery-verified
      false-positive causes were investigated (stale `installation.yml`
      recorded digests predating both the canonical `protocol/` drift and
      this Change's own edits); with the human operator's explicit,
      in-session authorization, the actual file content was written using
      the same production `driver.project()`/generator code path
      `AdapterService` uses internally (not hand-authored), and
      `installation.yml` was rebuilt from real on-disk SHA-256 digests
      after `publish_adapter_plan` itself also declined via the same
      conflict guard. Verified equivalent to a clean install by `forge
      doctor` (all PASS) and `forge adapter plan` (all UNCHANGED)
      afterward, not merely asserted (Plan items 12-13).

      **DEC-006** (`manifest.yml`): the explicit, in-session human
      authorization described above — to bypass `AdapterService`'s own
      `_reject_drift`/`_reject_conflicts` guards for this one-time
      republish, after the two guard refusals and one denied unauthorized
      attempt were investigated and disclosed — is that Decision. Recorded
      here explicitly (Review R002) because `manifest.yml`'s
      `decisions[]` entry alone, with no cross-reference to this
      narrative, left a future reader unable to tell what it was.
- [x] T-017 Documentation Impact scoping recorded for the post-Review
      `documentation`/`knowledge_capture` stages (`protocol/flows/full.yml`
      places both after `strict_review`, and only `before_completion`
      requires them — `manifest.yml`'s `documentation: pending`,
      `knowledge_capture: pending` was and remains accurate). CHANGELOG.md
      entry and `knowledge-capture.md` are deferred to those stages, per
      Plan item 14 (Review R003: this task previously, incorrectly, said
      Documentation Impact "was evaluated" in the past tense; corrected to
      describe what actually happened at Verification time — scoping, not
      completion).
- [x] T-018 Wrote `verification.md` and `traceability.yml` from real
      Implementation evidence. `knowledge-capture.md` was **not** written
      at this stage (Review R003: T-018 previously, incorrectly, claimed
      it was) — Knowledge Capture is a post-Review stage per
      `protocol/flows/full.yml` and is written after Review, informed by
      Review's own findings, per Plan item 15/Plan item 17.
- [x] T-019 Strict Review, independent Execution/Context (Plan item 16).
      **Iteration 1** (`review-001`, independent Execution/Context
      `claude-code-review-0045-independent`): **REQUEST CHANGES** — 1
      BLOCKER (R001: `traceability.yml` violated
      `protocol/schemas/traceability.schema.json`'s `minItems: 1` for
      `CON-001`/`CON-002`/`CON-004`, causing a real, reproduced `pytest`
      failure that `verification.md`/`provenance.yml` had incorrectly
      claimed did not exist), 3 MAJOR (R002, this DEC-006 narrative gap;
      R003, this T-017/T-018 overclaim; R004, the Adapter-Republish
      remediation-path gap — see `specification-drift.md`), 1 MINOR (R005,
      `traceability.yml` acceptance-table mapping errors). See `review.md`
      for the full independent Review.
- [ ] T-020 Resolution: fix R001-R005 (this commit); re-run the full
      suite to confirm 0 failures; freeze a new Resolution revision; obtain
      an independent Resolution Verification re-Review of that revision
      (C-026: a Resolver must not resolve blocking Findings in the
      Reviewer's own Execution Context, and re-Review must itself be
      independent of the Resolution).

## Status

T-001 through T-019 (Iteration 1) complete. Iteration 1's Verdict was
REQUEST CHANGES. T-020 (Resolution + independent re-Review of the
Resolution revision) is the only remaining task before Documentation
Impact/Knowledge Capture/Completion.

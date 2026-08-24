---
forge:
  artifact: plan
  schema: 1
change: CHG-0045
status: pending
---

# Plan — CHG-0045 Agent Adapter Architecture Skill Authority Consolidation

1. `src/forge_cli/adapters/review_independence.py` (new, harness-agnostic
   shared module): move `_REVIEWER_RESOLVER_INDEPENDENCE_LINES` here as
   the single source; expose it as a plain tuple of lines plus a small
   helper that renders it under a given heading. TDD: TDD-001, TDD-003,
   TDD-004 (RED first: assert the shared source doesn't yet exist /
   Claude Code and Codex still diverge).
2. `src/forge_cli/adapters/claude_code/projection.py`: remove the local
   `_REVIEWER_RESOLVER_INDEPENDENCE_LINES` constant; import from (1).
   Change `_gate_instructions()` so the independence block is appended
   once, after the per-Flow loop, with each per-Flow section emitting a
   short pointer line instead of the full block. Remove any residual
   per-Flow CHG-0025/C-077 sentence handling (confirmed absent from the
   current function body in Discovery, so this is a defensive check, not
   an expected diff). TDD: TDD-001, TDD-002, TDD-005.
3. `src/forge_cli/adapters/codex/projection.py`: same removal/import as
   (2), adapted to Codex's own `_gate_instructions()` shape. TDD: TDD-003,
   TDD-015.
4. `src/forge_cli/adapters/claude_code/resources/skills/workflow.md`: add
   the Bootstrap drift-check paragraph (FR-004) and the boundary-reporting
   instruction (FR-007), placed so they read as Bootstrap/Operating-Model/
   Human-Authority content rather than appended miscellany — reorganize
   existing paragraphs into identifiable groups per FR-005 without
   deleting any existing obligation (branch/PR workflow, first-commit
   baseline, chat-cadence, artifact-publication, FER guidance all remain,
   grouped). TDD: TDD-007, TDD-008, TDD-013.
5. `src/forge_cli/adapters/claude_code/projection.py`:
   `_hook_frontmatter_lines()` — add `Edit` and `Write` matcher entries
   pointing at the same generated hook script path. `_hook_script_content()`
   — extend the script to branch on `tool_name`, extracting
   `tool_input.command` for `Bash` (unchanged logic) and
   `tool_input.file_path` for `Edit`/`Write`, denying when the extracted
   path matches one of the three protected paths exactly (no proximity-
   window heuristic needed for `Edit`/`Write` — the payload already
   carries a discrete path, not a shell command line to pattern-match).
   Update the "Illustrative enforcement hook" disclosure prose in
   `_skill_content()` to name all three matched tools and explicitly name
   the remaining uncovered surface (MCP filesystem tools, `NotebookEdit`,
   unverified subagent coverage — Specification Review SR-003). TDD:
   TDD-009, TDD-010, TDD-011, TDD-012.
6. `tests/unit/test_claude_code_projection_bundle.py` (or the file the
   existing `_REVIEWER_RESOLVER_INDEPENDENCE_LINES`/gate-instruction tests
   already live in): add TDD-001, TDD-002, TDD-005, TDD-006, TDD-008,
   TDD-009, TDD-014. Add TDD-010/TDD-011/TDD-012 alongside the existing
   Bash golden-hook test, following its actual-subprocess methodology.
7. `tests/unit/test_codex_projection_bundle.py` (or equivalent): add
   TDD-003 (shared-source identity), TDD-015 (regression).
8. New shared-module test file (e.g.
   `tests/unit/test_adapter_review_independence.py`): TDD-004 (agreement
   with the effective C-026 paragraph — reads `protocol/contract/
   engineering.md` directly, not a copy).
9. New repository-fixture test file (e.g.
   `tests/integration/test_worktree_resolution.py` or the existing
   integration-test location for `git`-backed fixtures): TDD-016 (real
   `git worktree add` fixture; `resolve_project_root` resolution).
10. `.forge/adapters/claude-code/installation.yml`,
    `.forge/adapters/codex/installation.yml`: `git add` (DEC-004) — commit
    the existing, currently-untracked installation records as-is first
    (baseline), then let Implementation's own `forge adapter update`
    produce the post-Change commit naturally, so the diff between
    "pre-existing uncommitted state" and "this Change's actual delta" stays
    inspectable in Review (Architecture Risk: don't overclaim credit for
    pre-existing drift).
11. New repository-fixture test file continued: TDD-017 (installation
    record visible in a second worktree post-commit — depends on task 10).
12. Run `forge adapter update claude-code` and `forge adapter update
    codex` against this repository itself once (1)–(9) are GREEN,
    republishing `SKILL.md`/`references/*`/`hooks/*` for both Adapters —
    this is the dogfooded, real Adapter republish Discovery's live
    `CONFLICT` finding requires to actually resolve, not a separate
    hand-patch of the installed files.
13. `forge validate` and `forge doctor` (both Adapters) — must report
    clean (no `FAIL`, no `CONFLICT`) after (10).
14. Documentation Impact evaluation: `CHANGELOG.md` entry; `docs/adr/`
    new ADR only if Architecture's DEC-002 (guard-policy-location
    decision) rises to F-008's "Material Architecture Change" threshold —
    recorded as a Documentation Impact finding during Verification, not
    pre-decided here; `knowledge-capture.md` per this Change's own
    structural-core requirements once Implementation evidence exists.
15. `verification.md`: real evidence for every TDD-xxx, `forge validate`/
    `forge doctor` output, and the byte-identical-generator claim
    (TDD-006), following this repository's own `## Result`-first
    convention (`artifact-structure.md` §4 Verification).
16. Strict Review: independent Execution/Context per this Change's own
    Specification "Self-Hosting Boundary" section — evaluated against the
    Forge state effective at this Change's `intent` stage, per that same
    section, regardless of what `SKILL.md` shape (10)–(12) install
    mid-Change.

## Validation Strategy

`pytest -q` (existing suite plus TDD-001–017), `forge validate`, `forge
doctor`, `forge adapter plan claude-code`/`forge adapter plan codex` (must
show no `CONFLICT` after task 12) — run before Implementation begins to
capture the true pre-Change baseline (including today's live `CONFLICT`
state, so Verification can show the delta honestly), and again after every
numbered item completes.

## Compatibility Impact

No new Protocol identifier (CON-001). `installation.yml` schema
unchanged. Other Forge-governed repositories with this Adapter already
installed require an ordinary `forge adapter update` to adopt the new
projection shape — `ownership.classify_artifact()`'s existing CONFLICT
semantics continue to protect any repository-local customization from
silent overwrite, unchanged by this Change (F-009).

## Implementation Boundary

Reaching `tasks_ready` is not, by itself, authorization to begin
Implementation. For an active Change adopted from CHG-0025 onward — CHG-0045
is — C-077 additionally requires a recorded human-authority Plan Decision:
a material technical Decision owned by `plan` with `authority: human`,
`status: resolved`, `resolved_via: human_decision`, plus the Plan and
provenance recording the explicit human confirmation observed by the
operator. `status: approved` alone is not authorization, and this Plan's
`forge:plan-approval-confirmation`/`forge:plan-approval-record` markers
below remain empty until that confirmation is actually received in this
session. No Implementation or TDD GREEN work may begin before then.

<!-- forge:plan-approval-confirmation -->

This Plan is explicitly authorized by the human maintainer to proceed to
Implementation.

<!-- forge:plan-approval-record -->

**Approval record.** Explicit human approval was received from the user,
selecting "Aprovar e prosseguir" in response to a direct AskUserQuestion
Plan Decision prompt in the active session on 2026-08-24. This
confirmation authorizes the recorded Plan decision (DEC-005) and
continuation under C-077.

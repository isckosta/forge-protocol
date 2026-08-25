# ADR-0018 — Agent Adapter Skill Authority Consolidation

Status: Accepted, CHG-0045, Strict Review passed (Iteration 3, `review-003`, PASS).

## Decision

Reviewer/Resolver-independence projection text (C-026's English rendering)
now has exactly one shared source,
`src/forge_cli/adapters/review_independence.py`, imported by both the
Claude Code and Codex drivers, instead of two independently
hand-maintained copies (one per Adapter) each re-emitted once per
effective Flow. The generated `SKILL.md`'s per-Flow gate-obligation
sections now carry a one-line pointer to a single, once-rendered
independence section rather than repeating the full block.

The generated `PreToolUse` guard's tool coverage widens from `Bash`-only
to `Bash`+`Edit`+`Write`, still matched against the same three review-
control paths, still generated inline in the same shell script
(`_hook_script_content()`) rather than moved to a centralized `forge
internal guard-check` CLI entry point.

## Rejected/deferred alternatives

**Centralized guard policy entry point** (Architecture DEC-002): route
the generated hook script through a new `forge internal guard-check`
subcommand so multiple Adapters' hooks could share one policy
implementation. Rejected for now — only the Claude Code Adapter
currently generates a hook artifact at all (Codex's bundle has none), so
the stated benefit (shared logic across multiple hook-generating
Adapters) has no second consumer yet; building it now would be exactly
the kind of premature plugin surface F-010 disfavors. Recorded here so a
future Change adding a second hook-generating Adapter does not have to
rediscover this tradeoff.

**Further per-Flow lazy-loaded reference splitting** (Architecture
DEC-003): splitting each Flow's gate-obligation bullets into its own
generated reference file. Rejected as disproportionate (C-039) — the
content involved, once de-duplicated, is a handful of lines per Flow; the
real "don't inline the normative bulk" goal is already achieved at the
Contract/Flow/Artifact-Structure/Decision-Rules reference-file
granularity, which predates this Change.

## Consequences

- A Contract wording change to C-026, or a third Harness Adapter's
  Reviewer/Resolver-independence text, now requires editing one file
  (`review_independence.py`), not one file per Adapter.
- `tests/unit/test_adapter_review_independence.py` guards against the two
  drivers' texts silently diverging again (identity check, not just
  equality) and against the shared text silently drifting from C-026's
  actual current wording (keyword-agreement check against
  `resolve_effective_contract(protocol_id=2)`'s live text, not a frozen
  copy).
- The widened guard still does not cover MCP filesystem tools,
  `NotebookEdit`, or verified subagent-issued tool calls — disclosed
  explicitly in the generated `SKILL.md` itself, not silently implied as
  complete coverage.
- `.forge/adapters/*/installation.yml` is now committed to this
  repository (previously untracked in this repository's entire history),
  so a fresh Git worktree checkout inherits the correct Adapter drift
  baseline without a separate `forge adapter install` there.
- Republishing an Adapter whose `installation.yml` predates real,
  accumulated canonical `protocol/` drift is **not** currently an
  "ordinary `forge adapter update`" experience — this Change's own
  dogfooded Implementation required a one-time, human-authorized bypass
  of `AdapterService`'s own ownership/drift guards (see
  `specification-drift.md` under `.forge/changes/CHG-0045-.../`). A
  supported CLI recovery path for other adopters in the same position is
  explicit, recorded follow-up work, not built by this Change.

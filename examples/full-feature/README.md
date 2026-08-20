# Example — FULL-Flow Feature

This is a guided tour of a real FULL-flow Change already recorded in
this repository's own history: **`CHG-0018`** ("Second Harness Adapter —
Claude Code"), the largest Change in this repository's history and the
first whose own dogfooded verification produced genuinely independent,
live-executed evidence rather than only unit tests.

Full primary source: `.forge/changes/CHG-0018-second-harness-adapter-claude-code/`
(`discovery.md`, `architecture.md`, `verification.md`, `review.md`,
`knowledge-capture.md`). This README is a map into that record, not a
replacement for it.

## The commit sequence

```text
723efd9  docs(chg-0018): T-001..T-005 -- Intent, Discovery, Specification, Specification Review, Architecture, Plan/Tasks, Test Strategy
35fbb48  fix(chg-0018): T-001..T-002 -- relocate generic invariant assessment, generalize the .codex reserved-path rule
4f676b9  fix(chg-0018): T-001..T-002 continued -- stage the remaining Core-fix files
4531b8f  feat(chg-0018): T-003..T-007 -- Claude Code Adapter package, registration, shared conformance suite
9b23c41  docs(chg-0018): T-009..T-011 -- Contract C-074, ADR-0016
e5579ec  test(chg-0018): T-012a -- Golden Path (STANDARD, Claude Code) Layer A/B
6214390  docs(chg-0018): T-012b..T-013 -- freeze Implementation subject (verification, manifest, knowledge capture, evidence)
b192824  docs(chg-0018): record role: implementation provenance (6214390)
3d954dd  review(chg-0018): Iteration 1 -- Independent Strict Review, PASS
7385799  fix(chg-0018): resolve Strict Review Iteration 1 finding (R001)
75e3678  docs(chg-0018): record role: resolution provenance (Resolution Scope/targets, 7385799)
511f901  review(chg-0018): Iteration 2 -- Resolution Verification, PASS
d489f1b  docs(chg-0018): Completion
```

## Why this Change is FULL, not STANDARD

Per `protocol/contract/engineering.md` C-003, Flow classification uses
semantic impact, not size alone. `CHG-0018` touches: the generic Adapter
Core (two real pre-existing leaks fixed — see below), a Protocol schema
(`adapter-configuration.schema.json`), both Contract files (new `C-074`),
and a large new executable package with its own test suite. That
combination — Core + Contract + schema + executable surface — is exactly
what classified this repository's other FULL Changes
(`CHG-0013`, `0015`, `0016`, `0017`) the same way.

## What actually happened, in order

1. **Two real, pre-existing Core leaks found and fixed** — not
   hypothetical cleanup. A `.codex` reserved-path rule was hardcoded in
   the *generic* `adapters/configuration.py` (with a latent regex bug
   that also matched `Xcodex`); genuinely-generic invariant-assessment
   logic was misfiled under the Codex-specific package. Both fixed as
   part of proving the generic Core needed no vendor-specific concept to
   support a second Adapter.
2. **A second concrete Harness Adapter built** (`src/forge_cli/adapters/claude_code/`),
   with a materially richer, dated capability profile than the existing
   Codex Adapter, projecting through three real mechanisms (a Skill, a
   CLAUDE.md pointer, and an illustrative enforcement hook) — verified
   end to end against real scratch Git repositories, not only unit tests.
3. **The centerpiece: a genuinely independent, live-executed Golden
   Path.** A real, non-interactive `claude -p` process — not a narrated
   description of what one should do — opened a scratch repository with
   the new Adapter installed and, unprompted, recognized Forge
   governance, classified a Flow, ran a real RED→GREEN TDD cycle,
   produced repository-native Change artifacts, and then **spawned its
   own independent subagent for Strict Review** — which found and
   required fixing a real bug (`greet(None)` silently regressing from
   `ValueError` to `AttributeError`) before that session's own Change
   could pass. See `verification.md`'s "Layer C" section for the full,
   independently-corroborated account (including a first, failed attempt
   that used the wrong subagent mechanism, recorded honestly rather than
   concealed — `knowledge-capture.md`'s first entry).
4. **Independent Strict Review of `CHG-0018` itself**: `3d954dd`, PASS
   with one non-blocking MINOR (a hook pattern-matching false positive on
   compound Git commands), resolved in `7385799`, confirmed by a second
   independent Resolution Verification (`511f901`).

## What this demonstrates

- FULL classification is earned by touching the Core/Contract/schema
  surface, not merely by "being a big feature."
- A Change can find and fix real, pre-existing defects in already-shipped
  code as part of its own Discovery, not only add new code.
- Genuine end-to-end verification — a real independent process behaving
  correctly, including catching its own real bug through genuinely
  independent self-review — is possible and was actually done here, not
  merely claimed.

See `.forge/changes/CHG-0018-second-harness-adapter-claude-code/verification.md`
and `review.md` for the complete record.

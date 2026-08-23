# Forge Examples

This directory contains reference Forge Changes, each with real
repository-native evidence rather than explanatory prose alone
(`ROADMAP.md`'s "End-to-End Examples & External Project Validation"
milestone). Where a scenario already exists in this repository's own
real history, these examples curate and annotate that real evidence
rather than fabricate a fresh one.

`ROADMAP.md`'s named categories, mapped to real or explicitly labeled
illustrative evidence:

| Category | Directory | Evidence |
| --- | --- | --- |
| `fast-bugfix` | `golden-path-claude-code/` | a live, independent Claude Code session classified its own work FAST, unprompted |
| `standard-feature` | `golden-path-standard/` | a real STANDARD Change, install through Verification, against the Codex Adapter |
| `full-feature` | `full-feature/` | `CHG-0018` — two Core fixes, a new Harness Adapter, a genuinely independent dogfooded bug-catch |
| `strict-review-remediation` | `strict-review-remediation/` | `CHG-0016` — a real `REQUEST CHANGES` cycle (1 BLOCKER, 2 MAJOR), fully remediated |
| `codex-adapter-project` | `golden-path-standard/` | the same STANDARD scenario, specifically against the Codex Adapter |
| `first-change-baseline` | `first-change-baseline/` | an explicitly illustrative first-commit fixture demonstrating the complete baseline before Implementation (C-076) |

## Directories

- `golden-path-standard/` — the canonical STANDARD-Flow, Codex-Harness
  Golden Path: install Forge, initialize a repository, install the Codex
  Adapter, confirm readiness, and carry one small behavioral Change
  through TDD, Verification, and (pending independent execution by a
  human operating Codex) Strict Review. Disposable starter fixture,
  deterministic Layer A/B automated tests (`tests/golden_path/`), and a
  behaviorally-specified manual acceptance procedure for the parts a
  live Codex session must prove.
- `golden-path-claude-code/` — the same scenario for the Claude Code
  Adapter, whose Layer C (a live Harness session actually behaving
  correctly) is genuinely, non-interactively executed rather than
  requiring a human — a real, dated transcript classified the work FAST
  on its own.
- `full-feature/` — a guided tour of `CHG-0018`'s real FULL-flow
  evidence.
- `strict-review-remediation/` — a guided tour of `CHG-0016`'s real
  Strict Review `REQUEST CHANGES` → Resolution → PASS cycle.
- `first-change-baseline/` — an explicitly illustrative, realistic fixture
  showing the complete pre-existing state committed before a first Change's
  Implementation; it is not presented as a real external history.
- `canonical-artifacts/` — illustrative examples for Intent, Verification,
  and Review artifact structure (`protocol/artifact-structure.md`).

## Still open

The External validation matrix (Laravel/PHP, Node.js/TypeScript, Python,
a monorepo, a legacy repository) remains unattempted — no real target
repository exists in any ecosystem other than this one. Not fabricated
here; see `ROADMAP.md`.

Examples must reflect canonical Protocol semantics.

# Discovery — End-to-End Examples (Curated Real Evidence)

## Executive Summary

Verified the exact real evidence each curated README will cite, directly
against `git log`/`git show`/file content — not from memory of this
conversation.

## `strict-review-remediation` → `CHG-0016`, verified

Commit sequence (`git log --oneline | grep chg-0016`): `bf69393`
(planning) → `70478ae` (RED/GREEN) → `e50d3c5` (planning artifacts,
freeze prep) → `f7829d9` (freeze, provenance) → `6d6e2c7` (**Iteration
1, `REQUEST CHANGES`**) → `848adc9` (resolution, R001–R012) → `67766d3`
(resolution provenance) → `856e6a4` (**Iteration 2, PASS**) → `85c8ce0`
(Completion).

`review.md`'s own Summary table, read directly: **1 BLOCKER, 2 MAJOR, 6
MINOR, 3 OBSERVATION** in Iteration 1 — `blocking: [blocker, major]`
(`protocol/policies/review.yml`), so the BLOCKER and both MAJORs were
genuinely blocking. All three resolved by Iteration 2.

- **R012 (BLOCKER)**: `src/forge_cli/validation/__init__.py:320` (at the
  time) accepted only `forge/execution-provenance@1`, so the moment
  `CHG-0016`'s own Review Iteration bound to its `@2` provenance ledger,
  `forge validate` failed — a real, self-referential defect the Change's
  own Review process triggered on itself.
- **R001 (MAJOR)**: `traceability.yml` recorded evidence asserting
  NFR-002 (Harness independence — no Codex-specific content in the
  canonical guidance) held, when the shipped file actually violated it.
- **R002 (MAJOR)**: the new guidance omitted this repository's own most
  consistent real Artifact convention (the `forge:` frontmatter block).

## `full-feature` → `CHG-0018`, verified

Commit sequence confirmed via `git log --oneline | grep chg-0018`:
planning (`723efd9`) → Core fixes (`35fbb48`, `4f676b9`) → Adapter package
(`4531b8f`) → Contract/ADR (`9b23c41`) → Golden Path Layer A/B (`e5579ec`)
→ freeze (`6214390`) → implementation provenance (`b192824`) → Iteration
1 PASS (`3d954dd`) → resolution (`7385799`) → resolution provenance
(`75e3678`) → Iteration 2 PASS (`511f901`) → Completion (`d489f1b`).

This Change's own `verification.md` and `review.md` (already read in full
during `CHG-0018`'s own execution, re-confirmed present and unchanged at
`d489f1b`) document: two pre-existing Core leaks found and fixed, a
second concrete Harness Adapter built and installed against real scratch
repositories, and — the centerpiece — a genuinely independent, live
Claude Code session that recognized Forge governance unprompted, ran a
real RED→GREEN cycle, spawned its own independent review subagent, which
found and required fixing a real bug (`greet(None)` regressing from
`ValueError` to `AttributeError`).

## `fast-bugfix` / `standard-feature` / `codex-adapter-project`

`examples/golden-path-claude-code/README.md`'s own recorded transcript
(re-read directly): the live session "recognized the repository as
Forge-governed and classified **FAST** (with a stated reason: a small,
self-contained fix)" — an unprompted, real classification, not asserted
by this repository's own authors. `examples/golden-path-standard/README.md`
covers STANDARD flow against the Codex Adapter end to end (install
through Verification) — satisfies both `standard-feature` and
`codex-adapter-project`.

## Flow Classification Finding

No Protocol, Contract, schema, or executable-code change — pure
documentation curation. Per `protocol/contract/engineering.md` C-003
(semantic classification), this is **STANDARD**: a real, meaningful
addition, but none of FULL's distinguishing surface (Contract, schema,
executable Core code) is touched. `tdd_applicable`/`behavioral_change`
are both false for this Change (`protocol/flows/standard.yml`), so TDD
stages are not required — matches Protocol §19's precedent for prose-only
deliverables in every prior Change.

## Documentation Impact Signal (preliminary)

`ROADMAP.md`'s status line for this milestone. No ADR — this Change adds
no architectural decision (F-008's RFC/ADR threshold is Material
Architecture/Protocol Changes; this Change curates references to
existing, already-ADR'd decisions).

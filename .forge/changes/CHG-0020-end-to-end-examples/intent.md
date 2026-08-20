# Intent — End-to-End Examples (Curated Real Evidence)

## Summary

`ROADMAP.md`'s "End-to-End Examples & External Project Validation"
milestone wants five `examples/` directories, each containing "real
repository-native Change evidence rather than explanatory prose alone."
Three of the five categories are already satisfied by existing
directories (`golden-path-standard/`, `golden-path-claude-code/`); two —
`full-feature` and `strict-review-remediation` — have nothing yet. This
Change fills that gap by curating evidence that already exists in this
repository's own history, rather than fabricating new toy scenarios.

## Problem

Building a fresh toy scenario for `full-feature` and
`strict-review-remediation` (mirroring `golden-path-standard`'s pattern)
would take a Change on the scale of `CHG-0017`–`0019` to do well, and
would be *less* authentic than what already exists: this repository's own
history already contains a real, dramatic Strict Review `REQUEST CHANGES`
cycle (`CHG-0016`: 1 BLOCKER, 2 MAJOR, 6 MINOR, 3 OBSERVATION in
Iteration 1, fully remediated to a passing Iteration 2) and a real,
large, genuinely-dogfooded FULL Change (`CHG-0018`: two Core fixes, a new
Harness Adapter, and an independently-executed Golden Path that caught
and fixed a real bug through its own spawned independent review). Neither
needs to be re-created — both need to be made legible to a reader who has
not followed this repository's own commit history.

## Desired Outcome

A developer unfamiliar with this repository can open
`examples/strict-review-remediation/` or `examples/full-feature/` and
understand, without reading `.forge/changes/CHG-0016-.../review.md` or
`CHG-0018`'s full artifact set cold, what a genuine Strict Review
remediation cycle and a genuine FULL-flow Change actually look like in
this Protocol — with every claim traceable to a real commit or file.

## Scope

- `examples/strict-review-remediation/README.md` (new): a guided tour of
  `CHG-0016`'s real Iteration 1 → Resolution → Iteration 2 cycle.
- `examples/full-feature/README.md` (new): a guided tour of `CHG-0018`'s
  real FULL-flow evidence, including its dogfooded Golden Path's own
  real bug-catch.
- `examples/golden-path-standard/README.md` and
  `examples/golden-path-claude-code/README.md`: each gains a short
  addendum naming which additional ROADMAP categories they also satisfy.
- `examples/README.md`: rewritten to map all five ROADMAP-named
  categories to real evidence.
- `ROADMAP.md`: status line for this milestone.

## Out of Scope

- The External validation matrix (Laravel/PHP, Node.js/TypeScript,
  Python, a monorepo, a legacy repository) — still blocked on a real
  target repository in each ecosystem; not attempted here.
- Any new fixture, fabricated scenario, code, Contract, or schema change.

## Success Criteria

See `specification.md`. At Intent stage, success means: every one of the
five ROADMAP-named categories maps to real, cited, independently-
verifiable evidence, and no claim in any new or updated README misstates
what the cited commit/file actually contains.

---
forge:
  artifact: intent
  schema: 1
change: CHG-0023
status: active
---

# Intent — First-Change Baseline Guidance

## Summary

Define and project an explicit Forge rule for Changes conducted in a
repository whose first commit has not yet been made: the complete
pre-existing state MUST be committed, with no file excluded, before
Implementation begins.

## Problem

`CHG-0001-sanctum-authentication`, the first external Change conducted in
`crud-produtos`, had no prior Git history to represent the Change's
before-state. The agent chose a separate baseline commit ad hoc and its
first attempt excluded pre-existing files that the Change itself later
touched. Those files therefore appeared as 100% new in the Change diff.
The defect was found only by that Change's Strict Review. Neither the
Engineering Contract nor the projected Adapter workflow currently tells an
agent how to establish a complete baseline in a repository with no prior
commit.

## Desired Outcome

An agent conducting the first Change in a repository can establish a
reviewable before-state deterministically: every pre-existing file is in one
baseline commit before Implementation, and the resulting Change diff does
not misrepresent pre-existing files as newly created merely because the
baseline was incomplete.

## Scope

- add the rule at the canonical layer selected by Discovery, including its
  relationship to the existing baseline and TDD gates;
- create the required RFC before changing the Engineering Contract;
- ensure the rule reaches both Adapter-projected workflow guidance;
- add at least one curated `examples/` demonstration of the complete
  pre-existing-state baseline before Implementation;
- update this Change's repository-native evidence and roadmap status.

## Out of Scope

- `src/forge_cli/app.py` and `src/forge_cli/adapter_cli.py`;
- the `change-scaffolding-cli` implementation or any new `forge change`
  command;
- changes to `protocol/schemas/*.json`;
- roadmap items #2 and #4–#10;
- automated Git baseline creation or a new CLI command for it;
- changing Strict Review, reviewer independence, or diff computation
  semantics beyond stating the first-commit prerequisite.

## Success Criteria

- Discovery records evidence for both Contract and Adapter-only placement,
  with a recommendation and Confidence rating.
- An accepted RFC precedes the Contract change if Option A remains selected.
- The final canonical guidance states the complete-state/no-exclusion rule
  in concrete terms and both Adapters project it without claiming technical
  enforcement.
- An `examples/` entry demonstrates the baseline commit and identifies the
  exact state that existed before Implementation; it is curated from real
  evidence or clearly labeled as a realistic fixture according to
  `examples/README.md`.
- `tdd: {status: not_applicable, reason: ...}` is recorded honestly if the
  final Change contains no executable behavior; otherwise any new projection
  behavior follows real RED before GREEN.
- Verification, independent Specification Review, independent Strict
  Review, Documentation Impact, and repository validation all pass.

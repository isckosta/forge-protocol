---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0023
status: complete
---

# Knowledge Capture — First-Change Baseline Guidance

## What Changed

Forge now states C-076 in both effective Contract representations and
projects the same first-commit baseline reminder through the Codex and Claude
Code workflow templates. A labeled illustrative example demonstrates the
complete pre-existing state, baseline commit, and later Change delta.

## Durable Knowledge

When a repository has no prior Git commit, the baseline is part of the
Change's evidence. It must represent the complete state that existed before
the Change began, within a declared scope, with no in-scope file excluded.
Change artifacts created after that baseline are not pre-existing state. The
first Implementation commit must be reviewable as a delta from the baseline;
otherwise modified pre-existing files can be misrepresented as 100% new.

The Contract is the semantic source of truth. Adapter workflow resources make
the rule discoverable but cannot technically enforce Git behavior. Protocol 2
projects in this repository resolve a versioned Contract, so shared Contract
rules must be kept identical in both the canonical and effective versioned
Contract files when compatibility requires it.

## Consequences for Future Changes

- A first-commit Change should declare its intended repository scope before
  committing the baseline.
- Reviewers should inspect the baseline commit and confirm every in-scope
  pre-existing file is present before trusting the Change diff.
- Any future baseline automation or diagnostic needs its own safety analysis;
  C-076 does not authorize a new CLI command or claim prevention.

## References

- `docs/rfcs/0003-first-change-baseline-guidance.md`
- `protocol/contract/engineering.md` C-076
- `protocol/versions/2/contract/engineering.md` C-076
- `examples/first-change-baseline/README.md`

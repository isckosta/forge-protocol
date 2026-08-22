---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0023
status: active
---

# Test Strategy — First-Change Baseline Guidance

## Objective

Prove the new projected workflow guidance and the illustrative example while
recognizing that C-076 itself is normative prose and has no executable Git
enforcement in this Change.

## Strategy

Use focused tests against the two existing packaged-workflow authority
paths. The tests will be written and run RED before editing either workflow
resource, then the smallest resource-only change will make them GREEN. Use
text and repository checks for the Contract and example, followed by the
full suite, `forge validate`, and `forge doctor` in Verification.

## TDD-001 — Codex workflow projects first-commit guidance (FR-002)

**RED:** assert the packaged Codex workflow template contains the exact
complete-state/no-exclusion and non-enforcement guidance; this fails because
the current template has no baseline guidance.

**GREEN:** add the canonical reminder to the Codex resource and observe the
focused test pass.

## TDD-002 — Claude Code workflow projects first-commit guidance (FR-002)

**RED:** the equivalent assertion against the Claude Code packaged template
fails for the same absent-guidance reason.

**GREEN:** add the same reminder to the Claude Code resource and observe the
focused test pass.

## TDD-003 — Template parity (NFR-002)

**RED:** assert the baseline-guidance block extracted from both templates is
identical; this is a compatibility/parity guard whose pre-change RED may be
reported as not applicable if the test cannot distinguish two absent blocks.

**GREEN:** both resources carry byte-identical guidance.

## TDD-004 — Contract and example evidence (FR-001, FR-003)

**RED:** not applicable. C-076 and the example are normative/documentary
content, not executable behavior; content review and repository-native
artifact validation provide the appropriate evidence. This is recorded as
`tdd: not_applicable` for this content portion, not fabricated as a test.

## Non-mechanical Validation

- confirm RFC-0003 precedes the Contract edit in Git history;
- inspect C-076 for complete-state/no-exclusion wording and the
  before-Implementation boundary;
- inspect the example's explicit illustrative label, inventory, baseline
  commit, and later Implementation diff;
- confirm no prohibited paths or schemas changed.

## Completion Criteria

- TDD-001 and TDD-002 are valid RED/GREEN cycles;
- TDD-003 is GREEN with an honest RED applicability record;
- TDD-004 is recorded as not applicable for prose-only content;
- all Acceptance Criteria pass and full Forge verification is green;
- independent Specification Review and Strict Review have no blocking
  findings.

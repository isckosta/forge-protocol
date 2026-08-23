---
forge:
  artifact: test_design
  schema: 1
change: CHG-0037
status: complete
---

# Test Design — CHG-0037 Specification Layout User Story Traceability

## Objective

Prove the new generated Specification layout and its optional-Story guidance without introducing a Markdown parser or changing historical validation.

## Strategy

## TDD-001 — Specification scaffold layout

RED was executed against the old scaffold and failed because it emitted `# Specification — ...`, `Acceptance Criteria`, and no User Story/traceability guidance. GREEN updates only the renderer and passes the focused scaffold suite.

Assertions cover front matter preservation, canonical headings, no default fictitious `US-001`, nearby Requirement/Acceptance sections, and valid technical Specifications without Stories.

## TDD-002 — Compatibility and repository contract

Run the full scaffold unit suite, protocol contract tests, `forge validate`, and the relevant adapter/golden-path tests. Assert no schema files changed and historical canonical YAML remains valid.

## Completion Criteria

List completion criteria.

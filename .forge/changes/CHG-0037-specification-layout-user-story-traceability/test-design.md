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

## Completion Criteria

- Focused scaffold tests pass with assertions for the new headings and optional Story guidance.
- Protocol contract tests and `forge validate` pass.
- The full test suite is run against the implementation subject; environmental failures are reported separately from product failures.
- No Schema file, Protocol integer, Gate, Adapter semantic, or historical Specification changes are introduced.

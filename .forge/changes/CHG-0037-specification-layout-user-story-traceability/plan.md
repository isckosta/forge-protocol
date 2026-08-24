---
forge:
  artifact: plan
  schema: 1
change: CHG-0037
status: approved
---

# Plan — CHG-0037 Specification Layout User Story Traceability

1. Update `src/forge_cli/change_scaffolding.py` to render the new Specification contract layout while preserving front matter and avoiding fictitious User Stories.
2. Add focused TDD assertions in `tests/unit/test_change_scaffolding.py` for headings, optional Stories, nearby Acceptance, and technical Requirements without Stories.
3. Update `protocol/artifact-structure.md` and affected canonical documentation to describe User Story, Requirement, Acceptance Scenario, and Traceability semantics as non-binding guidance.
4. Run focused tests, full repository tests, `forge validate`, and inspect the final diff for schema/protocol/adapter compatibility.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

## Human Plan Authorization

This Plan is explicitly authorized by the human maintainer to proceed to
Implementation under C-077.

<!-- forge:plan-approval-confirmation -->

The user approved continuation in the active session on 2026-08-23 after
reviewing the repository audit, compatibility boundary, affected files, and
test strategy.

<!-- forge:plan-approval-record -->

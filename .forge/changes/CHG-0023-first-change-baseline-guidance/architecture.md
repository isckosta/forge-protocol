---
forge:
  artifact: architecture
  schema: 1
change: CHG-0023
status: active
---

# Architecture — First-Change Baseline Guidance

## Solution Summary

Adopt RFC-0003 as C-076 in the canonical Engineering Contract, then place a
short operational reminder in both packaged Adapter workflow templates.
The Contract remains the semantic source of truth; the templates tell an
agent where the rule applies and disclose that Adapter projection is not
technical Git enforcement. A new illustrative example documents the
baseline-to-Implementation commit sequence.

## Architectural Goals

- keep the rule provider-independent and repository-native;
- define one canonical meaning and project identical guidance to both
  Adapters;
- avoid introducing a CLI, schema, Flow, Adapter lifecycle state, or
  enforcement claim;
- make the before-state boundary and complete-file-scope requirement
  unambiguous to a cold agent.

## Design

Both `protocol/contract/engineering.md` and
`protocol/versions/2/contract/engineering.md` receive identical C-076 text
after the existing Contract rules, because Protocol 2 is the active project's
effective Contract. Its wording uses MUST for the repository state and
explicitly separates the baseline commit from Implementation. The rule does not define
how a Harness performs `git add`; that remains Harness/runtime capability.

Both `resources/skills/workflow.md` files receive the same two-line reminder:
when no prior commit exists, commit the complete pre-existing state in scope,
with no file excluded, before Implementation; the Adapter projects this
requirement but cannot technically enforce Git behavior. The existing
projection functions already load these packaged templates, so no Python
plumbing or new Adapter abstraction is needed.

`examples/first-change-baseline/README.md` provides a realistic, explicitly
illustrative fixture. It lists the pre-existing files, shows `git add -A`
and a baseline commit before any Implementation command, then shows a later
Implementation commit and the diff boundary. It does not claim to be a real
external repository history.

## Compatibility

This is additive Contract guidance. Existing repositories and Change
identifiers remain valid; the new condition applies only where the repository
has no prior commit. Both current Adapter projections gain the same reminder
through their existing packaged-resource path. No schemas, generated
resource names, CLI entry points, or concurrent Change files are changed.

## Risks and mitigations

- **Ambiguous scope:** C-076 says “intended repository scope”; the example
  and guidance require the agent to identify that scope before committing.
- **False prevention claim:** wording explicitly says projection is not
  technical enforcement.
- **Checklist substitution:** the example demonstrates the complete
  inventory and commit boundary, while Strict Review remains mandatory.
- **Contract/RFC drift:** RFC-0003 is cited by the Specification and this
  Change's traceability, and C-076 uses the RFC's exact decision.

---
forge:
  artifact: test_design
  schema: 1
change: CHG-0040
status: complete
---

# CHG-0040 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0040 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Test Strategy

`render_scaffold`/`_markdown` are pure string renderers (`src/forge_cli/change_scaffolding.py`) with no I/O, so a single automated Layer over their return value is sufficient — no Manual Acceptance applies to this Change.

| Layer | Scope | Method |
|---|---|---|
| Layer A — Scaffold Rendering | `_markdown("verification", ...)` output via `render_scaffold` | Automated |

## Coverage Map

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001 | Automated |
| FR-002 | TD-002 | Automated |
| FR-003 | TD-003 | Automated |
| FR-004 | TD-004 | Automated |
| FR-005 | TD-005 | Automated |
| FR-006 | TD-006 | Automated |
| FR-007 | TD-007 | Automated |
| FR-008 | TD-008 | Automated |

## Layer A — Scaffold Rendering

### TD-001 · Verification scaffold structural core and identity heading
Requirements: FR-001
Type: Unit

#### Purpose
A generated `verification.md` that lacks a traceable structural core forces a reader to reconstruct coverage by hand — the exact motivating gap this Change closes.

#### Scenario
Given a FAST, STANDARD, or FULL behavioral scaffold, When `verification.md` is rendered, Then it starts with the `# CHG-XXXX · Verification` identity heading and contains `## Result`, `## Summary`, `## Acceptance Coverage`, `## Test Evidence`, `## Forge Evidence`, `## Compatibility and Limitations`, and `## Conclusion`, in that order, and the prior minimal template text is absent.

#### Evidence
Test result: heading order assertions against the rendered string.

#### Failure Condition
A false positive if the assertion only checks substring presence without order — a renderer that emits the same headings shuffled would still satisfy a presence-only check but not the structural core.

### TD-002 · Result placeholder is distinct from the four recognized states
Requirements: FR-002
Type: Unit

#### Purpose
Proves the scaffold's "not yet run" placeholder cannot be mistaken for a real recognized Result, and that no fifth state is silently introduced.

#### Scenario
Given the rendered `verification.md`, When the `Result` section is inspected, Then it renders `**PENDING**` as plain bold text (not a nested heading), and none of `PASS`, `FAIL`, `SKIPPED`, `NOT APPLICABLE`, or `INCONCLUSIVE` appear as the placeholder value.

#### Evidence
Test result: string assertions on the `Result` section content.

#### Failure Condition
A false positive if the test only checks that `PENDING` is present without also asserting the four real states are absent from the placeholder — a template that leaked one of them as example text would pass a presence-only check.

### TD-003 · Acceptance Coverage table is compact and id-referencing
Requirements: FR-003
Type: Unit

#### Purpose
Proves the scaffold offers the traceable `AC-xxx → Requirement → Result → Evidence` shape rather than free text, matching the canonical example already established by `CHG-0016`.

#### Scenario
Given the rendered `verification.md`, When the `Acceptance Coverage` section is inspected, Then it contains a Markdown table with `Acceptance`, `Requirement`, `Result`, and `Evidence` column headers, and guidance text stating that Acceptance Criterion text must not be reproduced in full.

#### Evidence
Test result: substring assertions for the table header row and the guidance sentence.

### TD-004 · Requirement Coverage is present as conditional guidance
Requirements: FR-004
Type: Unit

#### Purpose
Proves the scaffold documents Requirement Coverage as conditional — omissible when it would duplicate Acceptance Coverage — rather than forcing a second, redundant table on every Change.

#### Scenario
Given the rendered `verification.md`, When the `Requirement Coverage` section is inspected, Then it contains guidance text stating the section may be omitted when Acceptance Coverage already expresses per-Requirement coverage.

#### Evidence
Test result: substring assertion for the conditionality guidance sentence.

#### Boundary
This scenario does not prove that a real, filled-in Change correctly omits or keeps the section — that is Verification's own responsibility on a real Change, not this scaffold-rendering test's.

### TD-005 · Manual Evidence guidance keeps manual and automated results distinct
Requirements: FR-005
Type: Unit

#### Purpose
Proves the scaffold documents `Manual Evidence` as a section distinct from `Test Evidence`/`Forge Evidence`, consistent with Test Design's existing `Type: Manual Acceptance` distinction on the other side of the Implementation boundary.

#### Scenario
Given the rendered `verification.md`, When the `Manual Evidence` section is inspected, Then it exists as a heading distinct from `Test Evidence` and `Forge Evidence`, with guidance text stating it is present only when a real manual verification occurred.

#### Evidence
Test result: substring assertions for heading presence and the conditionality guidance sentence.

### TD-006 · Test Evidence guidance references TDD-xxx by id
Requirements: FR-006
Type: Unit

#### Purpose
Proves the scaffold points Test Evidence authors at the existing structured TDD authority (`tdd-evidence.yml`, `red`/`green` per `TDD-xxx`) instead of inviting a hand-renarrated RED→GREEN story that could diverge from the real recorded evidence.

#### Scenario
Given the rendered `verification.md`, When the `Test Evidence` section is inspected, Then it contains guidance text instructing authors to reference the corresponding `TDD-xxx` cycle by id when `tdd-evidence.yml` already records RED and GREEN for it.

#### Evidence
Test result: substring assertion for the `TDD-xxx` reference guidance sentence.

### TD-007 · Conclusion guidance does not imply Completion under FAIL
Requirements: FR-007
Type: Unit

#### Purpose
Proves the scaffold's own Conclusion guidance explicitly warns against implying Completion when Result is not a clean PASS — closing the exact risk the Discovery identified (a positive-sounding Conclusion masking a FAIL).

#### Scenario
Given the rendered `verification.md`, When the `Conclusion` section is inspected, Then it contains guidance text instructing authors not to imply Completion when Result is FAIL, SKIPPED, or when Review remains pending.

#### Evidence
Test result: substring assertion for the Conclusion guidance sentence.

#### Boundary
This scenario does not prove a real Change's Conclusion prose is honest — that is a human/Review judgment call this scaffold-rendering test cannot make.

### TD-008 · Unrelated scaffold templates remain unchanged
Requirements: FR-008
Type: Unit

#### Purpose
Proves the redesign is scoped to the `verification` template only — the same regression-protection pattern `CHG-0038`/`CHG-0039` used for `test-strategy.md`/`plan.md`.

#### Scenario
Given a rendered scaffold for a Flow that includes `review.md`/`plan.md`/`test-strategy.md`, When those files are compared to their content before this Change, Then they are byte-identical.

#### Evidence
Test result: full-string equality assertions against the pre-Change template text.

#### Failure Condition
A false positive if the comparison only checks a substring rather than full equality — a template that gained unrelated extra text would still contain the old substring.

## Valid RED

RED is valid only when `tests/unit/test_change_scaffolding.py` fails because the current minimal `verification` template (`## Result\n\n**PENDING**\n\n## Summary\n\n...\n\n## Test Evidence\n\n## Forge Evidence\n\n## Conclusion\n\n`) lacks the new structural core — not because of an import error, a fixture problem, or unrelated test infrastructure failure.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001 | — | Covered |
| FR-002 | TD-002 | — | Covered |
| FR-003 | TD-003 | — | Covered |
| FR-004 | TD-004 | — | Covered |
| FR-005 | TD-005 | — | Covered |
| FR-006 | TD-006 | — | Covered |
| FR-007 | TD-007 | — | Covered |
| FR-008 | TD-008 | — | Covered |

## Coverage Gaps

None. NFR-001 (plain-text readability) and CON-001 (scope boundary) are verified by inspection during Verification (no HTML/emoji present, no file outside the declared scope touched), not by a dedicated `TD-xxx` — consistent with Test Design's own guidance that not every NFR/Constraint needs a distinct automated scenario when direct inspection is proportional.

## Test Design Gate

Every FR-001–FR-008 has an automated `TD-xxx` scenario with a clear Purpose and Evidence; no manual acceptance applies (pure string rendering); Valid RED is defined above; no Requirement remains without known coverage.

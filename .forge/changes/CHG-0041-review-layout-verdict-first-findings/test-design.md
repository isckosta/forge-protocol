---
forge:
  artifact: test_design
  schema: 1
change: CHG-0041
status: complete
---

# CHG-0041 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0041 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Test Strategy

`render_scaffold`/`_markdown` are pure string renderers (`src/forge_cli/change_scaffolding.py`) with no I/O, so a single automated Layer over their return value is sufficient — no Manual Acceptance applies to this Change.

| Layer | Scope | Method |
|---|---|---|
| Layer A — Scaffold Rendering | `_markdown("review", ...)` output via `render_scaffold` | Automated |

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
| FR-009 | TD-009 | Automated |

## Layer A — Scaffold Rendering

### TD-001 · Review structural core and identity heading
Requirements: FR-001
Type: Unit

#### Purpose
A generated `review.md` that lacks Review Summary/Current Subject/Open Findings forces a reader to reconstruct the current state by hand — the exact motivating gap this Change closes.

#### Scenario
Given a FAST, STANDARD, or FULL scaffold, When `review.md` is rendered, Then it starts with the `# CHG-XXXX · Review` identity heading and contains `## Verdict`, `## Review Summary`, `## Current Subject`, `## Reviewer Independence`, `## Open Findings`, in that order, all appearing before the first `## Iteration` heading, and the prior minimal template text is absent.

#### Evidence
Test result: heading order assertions against the rendered string.

#### Failure Condition
A false positive if the assertion only checks substring presence without order — a renderer that emitted the same headings after `## Iteration 1` would still satisfy a presence-only check but defeat the Change's purpose.

### TD-002 · Verdict placeholder is distinct from the two recognized states
Requirements: FR-002
Type: Unit

#### Purpose
Proves the scaffold's "not yet run" placeholder cannot be mistaken for a real recognized Verdict.

#### Scenario
Given the rendered `review.md`, When the `Verdict` section is inspected, Then it renders `**PENDING**` as plain bold text (not a nested heading), and neither `PASS` nor `REQUEST CHANGES` appear as the placeholder value.

#### Evidence
Test result: string assertions on the `Verdict` section content, sliced between `## Verdict` and the next `##`.

### TD-003 · Review Summary guidance points at manifest.yml as authority
Requirements: FR-003
Type: Unit

#### Purpose
Proves the scaffold does not invite a hand-maintained, divergence-prone count.

#### Scenario
Given the rendered `review.md`, When the `Review Summary` section is inspected, Then it contains guidance text naming `manifest.yml` as the source of truth for the iteration/blocker/major/minor counts.

#### Evidence
Test result: substring assertion for the guidance sentence.

### TD-004 · Current Subject references provenance.yml by id
Requirements: FR-004
Type: Unit

#### Purpose
Proves the scaffold points at the existing structured freeze authority instead of inventing a new one.

#### Scenario
Given the rendered `review.md`, When the `Current Subject` section is inspected, Then it contains a table with `Subject SHA`, `Frozen`, `Iteration` rows and guidance referencing `provenance.yml`.

#### Evidence
Test result: substring assertions for the table rows and the guidance sentence.

### TD-005 · Open Findings guidance covers both the populated and empty case
Requirements: FR-005
Type: Unit

#### Purpose
Proves the scaffold explicitly avoids an empty table when there are no open findings, matching the proportionality principle.

#### Scenario
Given the rendered `review.md`, When the `Open Findings` section is inspected, Then it contains the `Finding | Severity | Status | Iteration` table header guidance and the explicit `No open findings.` fallback instruction.

#### Evidence
Test result: substring assertions for both the table header and the fallback sentence.

### TD-006 · Finding guidance uses Rxxx and states a property, not an implementation
Requirements: FR-006
Type: Unit

#### Purpose
Proves the scaffold's finding guidance matches the real `Rxxx` convention (no Change-id prefix) and steers authors toward a verifiable property rather than a specific fix.

#### Scenario
Given the rendered `review.md`, When the finding guidance is inspected, Then it references the `Rxxx` id pattern (not `CHG-XXXX-Rxxx`), names the four recognized severities, and contains guidance against prescribing a specific implementation.

#### Evidence
Test result: substring assertions for the `Rxxx` pattern text, the severity list, and the non-prescription guidance sentence.

### TD-007 · Iteration heading convention is byte-identical to the prior template
Requirements: FR-007
Type: Unit

#### Purpose
Proves the one deliberately preserved element of the prior template — the real, stable `## Iteration N — <verdict>` convention — is untouched, and no `## Iteration History` wrapper was introduced.

#### Scenario
Given the rendered `review.md`, When the document is inspected, Then it contains the exact, verbatim substring `## Iteration 1 — PENDING\n\nRecord Strict Review findings.\n\n` (same heading level, same em dash separator as the prior template), positioned after `## Open Findings` and before `## Conclusion`, and `## Iteration History` does not appear anywhere in the document.

#### Evidence
Test result: exact-substring assertion for the verbatim iteration text, an ordering assertion (`Open Findings` index < `Iteration 1` index < `Conclusion` index), plus a negative assertion for the wrapper heading.

#### Failure Condition
A false positive if only a loose substring check is used — a renderer that reworded the surrounding guidance while keeping a fragment of the iteration text would still pass a weak check.

### TD-008 · Reviewer Independence guidance references provenance
Requirements: FR-008
Type: Unit

#### Purpose
Proves the independence declaration is guided toward the existing provenance mechanism rather than being presented as a bare, unverifiable assertion.

#### Scenario
Given the rendered `review.md`, When the `Reviewer Independence` section is inspected, Then it contains guidance instructing authors to reference a `provenance.yml` record by id as evidence.

#### Evidence
Test result: substring assertion for the guidance sentence.

### TD-009 · Unrelated scaffold templates remain unchanged
Requirements: FR-009
Type: Unit

#### Purpose
Proves the redesign is scoped to the `review` template only.

#### Scenario
Given a rendered scaffold for a Flow that includes `specification-review.md`/`plan.md`/`test-strategy.md`/`tasks.md`, When those files are compared to their content before this Change, Then they are byte-identical.

#### Evidence
Test result: full-string equality assertions against the pre-Change template text.

#### Failure Condition
A false positive if the comparison only checks a substring rather than full equality.

## Valid RED

RED is valid only when `tests/unit/test_change_scaffolding.py` fails because the current minimal `review` template (`## Verdict\n\n**PENDING**\n\n## Iteration 1 — PENDING\n\nRecord Strict Review findings.\n`) lacks the new structural core — not because of an import error, a fixture problem, or unrelated test infrastructure failure. Note this scenario also intentionally breaks the existing `test_render_scaffold_review_plan_test_strategy_tasks_templates_are_unchanged` protection test's assertion about `review.md`, which is updated as part of this Change's own GREEN (the `review` template is no longer unchanged; `specification-review.md`/`plan.md`/`test-strategy.md`/`tasks.md` remain protected).

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
| FR-009 | TD-009 | — | Covered |

## Coverage Gaps

None. NFR-001 (plain-text readability) and CON-001 (scope boundary) are verified by inspection during Verification (no HTML/emoji present, no file outside the declared scope touched), not by a dedicated `TD-xxx` — consistent with Test Design's own guidance that not every NFR/Constraint needs a distinct automated scenario when direct inspection is proportional.

## Test Design Gate

Every FR-001–FR-009 has an automated `TD-xxx` scenario with a clear Purpose and Evidence; no manual acceptance applies (pure string rendering); Valid RED is defined above; no Requirement remains without known coverage.

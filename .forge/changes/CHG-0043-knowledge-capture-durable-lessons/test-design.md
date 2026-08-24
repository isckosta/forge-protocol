---
forge:
  artifact: test_design
  schema: 1
change: CHG-0043
status: complete
---

# CHG-0043 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0043 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Test Strategy

`render_scaffold`/`_markdown` are pure string renderers (`src/forge_cli/change_scaffolding.py`) with no I/O, so a single automated Layer over their return value is sufficient — no Manual Acceptance applies to this Change.

| Layer | Scope | Method |
|---|---|---|
| Layer A — Scaffold Rendering | `_markdown("knowledge_capture", ...)` output via `render_scaffold` (Flow FULL only) | Automated |

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

## Layer A — Scaffold Rendering

### TD-001 · Structural core preserved with identity heading
Requirements: FR-001
Type: Unit

#### Purpose
Proves the four stable real-precedent headings survive unchanged in order, and the new identity heading matches the convention every other redesigned Artifact this session already adopted.

#### Scenario
Given a FULL-flow scaffold, When `knowledge-capture.md` is rendered, Then it starts with `# CHG-XXXX · Knowledge Capture`, and `## What Changed`, `## Durable Knowledge`, `## Consequences for Future Changes`, `## References` appear in that exact order, each followed by non-empty guidance text.

#### Evidence
Test result: heading order assertion plus a non-empty-guidance assertion per section.

#### Failure Condition
A false positive if the assertion only checks heading presence without order or without checking guidance text exists — a renderer that reordered the sections or left one bare would still pass a presence-only check.

### TD-002 · Durable Knowledge guides optional K-xxx items without mandating them
Requirements: FR-002
Type: Unit

#### Purpose
Proves the guidance offers the real, precedent-backed multi-lesson structure without inventing a mandatory namespace no consumer exists for.

#### Scenario
Given the rendered `knowledge-capture.md`, When the `Durable Knowledge` section is inspected, Then it contains guidance mentioning `### K-xxx` for multiple independent lessons and an explicit statement that ids are not required.

#### Evidence
Test result: substring assertions for the `K-xxx` mention and the "not required" guidance sentence.

### TD-003 · Distinction from adjacent Artifacts is explicit
Requirements: FR-003
Type: Unit

#### Purpose
Proves the scaffold steers authors away from duplicating Decision, Architecture, Specification, Review, or Specification Drift content.

#### Scenario
Given the rendered `knowledge-capture.md`, When the `Durable Knowledge` guidance is inspected, Then it names Decision, Architecture, Specification, Review, and Specification Drift as artifacts not to duplicate.

#### Evidence
Test result: substring assertions for each of the five artifact names.

### TD-004 · Relationship with the Forge Experience Report is stated
Requirements: FR-004
Type: Unit

#### Purpose
Proves the real, previously-undocumented distinction between FER (raw execution observation) and Knowledge Capture (distilled durable knowledge) is now discoverable from the scaffold itself.

#### Scenario
Given the rendered `knowledge-capture.md`, When the guidance is inspected, Then it references the Forge Experience Report and distinguishes it from Knowledge Capture.

#### Evidence
Test result: substring assertion for the FER distinction sentence.

### TD-005 · References guidance reflects real F-008 practice
Requirements: FR-005
Type: Unit

#### Purpose
Proves the guidance points at the real ADR/RFC mechanism instead of inventing a "promotion" workflow with no precedent.

#### Scenario
Given the rendered `knowledge-capture.md`, When the `References` section is inspected, Then it mentions `docs/adr/` for materially architectural work.

#### Evidence
Test result: substring assertion for the `docs/adr/` guidance sentence.

### TD-006 · Empty Knowledge Capture guidance is explicit
Requirements: FR-006
Type: Unit

#### Purpose
Proves the scaffold does not implicitly pressure authors to fabricate content when no durable lesson exists.

#### Scenario
Given the rendered `knowledge-capture.md`, When the `Durable Knowledge` guidance is inspected, Then it states explicitly that no additional knowledge is a valid, complete answer.

#### Evidence
Test result: substring assertion for the explicit validity statement.

### TD-007 · Unrelated scaffold templates remain unchanged
Requirements: FR-007
Type: Unit

#### Purpose
Proves the redesign is scoped to the `knowledge_capture` template only.

#### Scenario
Given a rendered FULL-flow scaffold, When `review.md`, `specification-review.md`, `plan.md`, `test-strategy.md`, and `tasks.md` are compared to their content before this Change, Then they are byte-identical.

#### Evidence
Test result: full-string equality assertions against the pre-Change template text.

#### Failure Condition
A false positive if the comparison only checks a substring rather than full equality.

## Valid RED

RED is valid only when `tests/unit/test_change_scaffolding.py` fails because the current minimal `knowledge_capture` template (`## What Changed\n\nRecord the durable change.\n\n## Durable Knowledge\n\n## Consequences for Future Changes\n\n## References\n\n`) lacks the new identity heading and section guidance — not because of an import error, a fixture problem, or unrelated test infrastructure failure.

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

## Coverage Gaps

None. NFR-001 (plain-text readability) and CON-001 (scope boundary) are verified by inspection during Verification, not by a dedicated `TD-xxx` — consistent with proportionality when direct inspection is sufficient.

## Test Design Gate

Every FR-001–FR-007 has an automated `TD-xxx` scenario with a clear Purpose and Evidence; no manual acceptance applies (pure string rendering); Valid RED is defined above; no Requirement remains without known coverage.

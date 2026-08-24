---
forge:
  artifact: test_design
  schema: 1
change: CHG-0044
status: complete
---

# CHG-0044 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0044 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Test Strategy

`render_scaffold`/`_markdown`/`_frontmatter` are pure string renderers
(`src/forge_cli/change_scaffolding.py`) with no I/O, so a single automated
Layer over their return value is sufficient — no Manual Acceptance
applies to this Change. A second, non-code Layer verifies the elaborated
prose in `protocol/artifact-structure.md` directly, by inspection.

| Layer | Scope | Method |
|---|---|---|
| Layer A — Scaffold Rendering | `_markdown("inspection", ...)` / `_frontmatter("inspection", ...)` output via `render_scaffold` (Flow FAST only) | Automated |
| Layer B — Canonical Guidance Prose | `protocol/artifact-structure.md` §4 "Inspection" | Manual Acceptance |

## Coverage Map

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001 | Automated |
| FR-002 | TD-002 | Automated |
| FR-003 | TD-003 | Manual Acceptance |
| FR-004 | TD-004 | Manual Acceptance |
| FR-005 | TD-005 | Manual Acceptance |
| FR-006 | TD-006 | Manual Acceptance |
| FR-007 | TD-007 | Manual Acceptance |
| FR-008 | TD-008 | Automated |

## Layer A — Scaffold Rendering

### TD-001 · No mandatory section heading is emitted
Requirements: FR-001
Type: Unit

#### Purpose
Proves the scaffold body itself never emits a fixed `##` section heading, which is the concrete, checkable form of "proportionality is not relaxed" — a template that quietly added one mandatory heading would violate this Requirement even if the surrounding prose still said "optional."

#### Scenario
Given a FAST-flow scaffold, When `inspection.md` is rendered, Then no line in the file starts with `## `.

#### Evidence
Test result: assertion that `[l for l in content.splitlines() if l.startswith("## ")] == []`.

#### Failure Condition
A false positive if the assertion only checks for the absence of one specific heading name rather than any `## ` line — a renderer that dropped `## Inspection` but added a different mandatory heading would still incorrectly pass a name-specific check.

### TD-002 · Identity heading matches the elaborated convention
Requirements: FR-002
Type: Unit

#### Purpose
Proves the fallback generic heading (`# Inspection — CHG-XXXX <Title>`) is replaced by the same `# CHG-XXXX · <Type>` convention already adopted by every other elaborated Artifact, and that front matter is byte-identical to before.

#### Scenario
Given a FAST-flow scaffold, When `inspection.md` is rendered, Then it starts with `---\nforge:\n  artifact: inspection\n  schema: 1\nchange: CHG-XXXX\nstatus: pending\n---\n\n# CHG-XXXX · Inspection\n\n` (with the real `change_id` substituted).

#### Evidence
Test result: full-prefix equality assertion (`.startswith(...)`), not a substring check.

#### Failure Condition
A false positive if only the heading line is checked in isolation — the front matter block must also be proven unchanged in the same assertion, since a corrupted front matter with a correct heading would otherwise pass.

## Layer B — Canonical Guidance Prose

### TD-003 · Optional structural vocabulary is documented and marked non-exhaustive
Requirements: FR-003
Type: Manual Acceptance

#### Preconditions
`protocol/artifact-structure.md` §4 "Inspection" is open for review.

#### Scenario
Given the elaborated "Inspection" section, When read, Then it lists `Observation`, `Evidence`, `Root Cause`, `Impact`, `Fix Boundary`, `Open Question`, `Conclusion`, states explicitly that this vocabulary is optional and not exhaustive, and cites at least one real occurrence (`CHG-0012`, `CHG-0024`, `CHG-0026`, `CHG-0028`, or `CHG-0029`) using an equivalent concept.

#### Evidence
Direct reading of the merged section text; reviewer confirms all seven terms and the explicit optionality statement are present.

#### Failure Condition
A false positive if the section lists the vocabulary but omits the explicit "not obligatory" statement — a reader could then reasonably treat it as a required checklist, which is exactly what this Change must not produce.

### TD-004 · Root Cause confidence is distinguished from Observed behavior
Requirements: FR-004
Type: Manual Acceptance

#### Scenario
Given the elaborated section, When read, Then it distinguishes `Observed behavior` from confirmed `Root Cause`, and names an explicit lower-confidence phrasing (e.g. "Likely cause") for the case where cause is not yet confirmed — without introducing a numeric or multi-level confidence scale.

#### Evidence
Direct reading; reviewer confirms both concepts are named and no confidence scale beyond the two-state distinction exists.

### TD-005 · Evidence quality model is named with a compact example
Requirements: FR-005
Type: Manual Acceptance

#### Scenario
Given the elaborated section, When read, Then it names the `Symptom → Reproduction → Cause` model, includes a compact example (not a large log dump), and instructs that claims be backed by a concrete reference (code, test, command, log, runtime behavior, or normative documentation).

#### Evidence
Direct reading; reviewer confirms the three-step model and the concrete-reference instruction are both present.

### TD-006 · Distinction from Discovery, Specification, Plan, Verification, and FER; Flow escalation named
Requirements: FR-006
Type: Manual Acceptance

#### Scenario
Given the elaborated section, When read, Then it distinguishes Inspection from Discovery, Specification, Plan, Verification, and the Forge Experience Report in one sentence each, and names the existing Flow escalation mechanism (`fast.yml`'s `escalation.enabled`, `automatic_downgrade: false`; `protocol/specification.md` §11) for the case where an Inspection reveals complexity incompatible with FAST.

#### Evidence
Direct reading; reviewer confirms all five distinctions and the escalation-mechanism reference are present, and that no new escalation mechanism is invented.

### TD-007 · CHG-0005 characterization is corrected
Requirements: FR-007
Type: Manual Acceptance

#### Scenario
Given the elaborated section, When the citation to `CHG-0005/inspection.md` is read, Then it no longer states "title only" (or an equivalent overclaim) and instead accurately describes the file's real two-sentence content, while preserving it as the repository's real minimal-Inspection precedent.

#### Evidence
Direct reading against `.forge/changes/CHG-0005-review-completion-gate/inspection.md`'s actual content.

#### Failure Condition
A false positive if the correction changes the citation's point (that a minimal Inspection is fully conforming) rather than only its factual description of the file's content.

## Layer A — Compatibility

### TD-008 · Unrelated scaffold templates and historical Inspection files remain unchanged
Requirements: FR-008
Type: Unit

#### Purpose
Proves the redesign is scoped to the `inspection` template and its own frontmatter branch only, and that no historical `inspection.md` is touched by this Change.

#### Scenario
Given a rendered FAST-flow scaffold, When `intent.md`, `test-design.md`, `tdd-evidence.yml`, `verification.md`, and `review.md` are compared to their content before this Change, Then they are byte-identical; Given the six real historical `inspection.md` files, When their Git history is checked after this Change, Then none of them appear in the diff.

#### Evidence
Test result: full-string equality assertions against the pre-Change template text for Layer A; `git diff` scoped to `.forge/changes/CHG-0*/inspection.md` for the historical-file claim, checked during Verification.

#### Failure Condition
A false positive if the comparison only checks a substring rather than full equality for the unaffected templates.

## Valid RED

RED is valid only when `tests/unit/test_change_scaffolding.py` fails
because the current minimal `inspection` template
(`"## Inspection\n\nRecord the relevant inspection findings.\n"`) and its
generic fallback heading lack the new identity heading and
no-mandatory-section behavior — not because of an import error, a
fixture problem, or unrelated test infrastructure failure.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001 | — | Covered |
| FR-002 | TD-002 | — | Covered |
| FR-003 | — | TD-003 | Covered |
| FR-004 | — | TD-004 | Covered |
| FR-005 | — | TD-005 | Covered |
| FR-006 | — | TD-006 | Covered |
| FR-007 | — | TD-007 | Covered |
| FR-008 | TD-008 | — | Covered |

## Coverage Gaps

None. NFR-001 (plain-text readability) and CON-001 (scope boundary) are
verified by inspection during Verification, not by a dedicated `TD-xxx`
— consistent with proportionality when direct inspection is sufficient.

## Test Design Gate

Every FR-001–FR-008 has a `TD-xxx` scenario with a clear Purpose (or
directly stated Scenario for the Manual Acceptance cases) and Evidence;
automated and Manual Acceptance scenarios are separated explicitly; Valid
RED is defined above; no Requirement remains without known coverage.

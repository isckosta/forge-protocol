---
forge:
  artifact: specification
  schema: 1
change: CHG-0033
status: pending
---

# Specification — CHG-0033 Forge Experience Report Markdown

## Summary

Introduce a deterministic, human-readable Markdown projection of the existing
canonical FER YAML without changing FER semantics or its contributor-only
boundary.

## Classification

This is a **FULL** Change. It crosses pure rendering, persistence, CLI
regeneration, historical migration, failure handling, and documentation, but
does not change Protocol or Change lifecycle semantics.

## Functional Requirements

### FR-001 — Canonical authority

The implementation MUST treat `dogfooding/reports/FER-####.yml` with schema
`forge/experience-report@1` as the sole canonical FER representation.
`report.md` MUST never be read as input to Forge tooling or parsed back.

### FR-002 — Pure deterministic renderer

A reusable renderer MUST accept the validated canonical report and return
Markdown without reading environment state, filesystem content, logs, prompts,
secrets, external references, timestamps, or random values. Identical input
MUST produce byte-identical output.

### FR-003 — Human-readable structure

The projection MUST include the report ID, available source context, a derived
summary when useful, observations, positive evidence, and follow-up
candidates. It MUST use headings, labels, lists, stable whitespace, and a
final newline. Empty optional sections MUST be omitted.

### FR-004 — Complete canonical evidence

Each observation MUST preserve exact ID and render area, classification,
expected, observed, evidence, impact, and available workaround/follow-up.
Positive evidence MUST preserve ID, area, and observed text. Follow-up
candidates MUST preserve their canonical observation, type, and summary.

### FR-005 — Safe text handling

Canonical text MUST be escaped as plain text. User-provided text MUST not
introduce generated headings, links, or list structure. Line breaks MUST stay
readable, and IDs/reference/path values MUST remain exact.

### FR-006 — Creation and update synchronization

Every successful official FER record operation MUST generate/update the sibling
Markdown. Existing lazy report creation MUST remain unchanged.

### FR-007 — Explicit regeneration and historical reports

An explicit command MUST regenerate one report and all reports from canonical
YAML. Existing YAML-only reports MUST remain valid and renderable without
manual editing.

### FR-008 — Drift behavior

Explicit rendering MUST correct missing or manually edited projection.
Explicit validation MAY report drift, but normal `forge validate`, normal
Forge commands, and disabled FER workflows MUST ignore it.

### FR-009 — Failure isolation

If canonical persistence succeeds but Markdown persistence fails, the command
MUST return a non-zero FER error stating that canonical YAML remains
authoritative and the projection is incomplete. Later render MUST repair it.

### FR-010 — Documentation

Contributor documentation MUST state the dual representation, canonical source
of truth, generated-file warning, regeneration command, and Git review use.

## Acceptance Criteria

### AC-001 — Basic rendering

A fixture with context, complete observation, positive evidence, and follow-up
candidate produces expected headings, labels, exact IDs, values, and no dump.

### AC-002 — Optional and empty data

Absent optional fields and empty collections produce no invented values or
unnecessary empty sections.

### AC-003 — Determinism and ordering

Two renders are byte-identical; arrays follow canonical order; repeated file
rendering produces no diff.

### AC-004 — Integration

First record creates YAML and Markdown; append updates both; explicit render
handles historical reports and drift.

### AC-005 — Isolation

Markdown failure leaves canonical YAML valid and disabled FER has no new
normal-workflow requirement or failure.

## Out of Scope

No Markdown editing, reverse parsing, custom templates, HTML/PDF, dashboard,
telemetry, new FER taxonomy/provenance, Protocol schema, Flow, Gate, Harness
behavior, or change to contributor opt-in semantics.

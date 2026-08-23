---
forge:
  artifact: discovery
  schema: 1
change: CHG-0033
status: pending
---

# Discovery — CHG-0033 Forge Experience Report Markdown

## Executive Summary

The existing FER implementation already provides the required canonical
boundary: one YAML report per ID under `dogfooding/reports/`, validated by
`ExperienceStorage._valid_document` and explicitly checked by
`forge experience validate`. The least disruptive design is a pure renderer
module called by `ExperienceStorage` after every successful canonical update,
plus an explicit `forge experience render` command for historical and manual
recovery.

The applicable Flow is **FULL**. This adds a derived artifact, modifies
creation/update failure semantics, adds a CLI operation, defines migration of
existing reports, and crosses FER model, storage, CLI, documentation, and
tracked examples.

## Investigation

### Repository truth

- Canonical path: `dogfooding/reports/FER-####.yml`.
- Canonical schema: `forge/experience-report@1`.
- Required top-level fields: `schema`, `report`, `source`, `observations`,
  `positive_evidence`, and `follow_up_candidates`.
- Observation and positive-evidence arrays preserve append order; IDs are
  canonical and must be preserved exactly.
- `source` is a mapping of safely known context, not a fixed title schema.
  Absent values must be omitted rather than invented.
- Reports are created lazily by `ExperienceStorage.record`.
- Existing official write paths are `ExperienceStorage.record` and the
  explicit `forge experience` CLI. Normal validation, doctor, Change, Flow,
  and Adapter paths do not read FER.
- Tracked data includes `dogfooding/reports/FER-0001.yml`; the fixture
  `examples/experience-report/FER-0001.yml` is also historical FER data.

### Existing patterns and selected approach

Adapter projections already use pure deterministic renderer functions and
stable-output tests. FER has no generated-artifact registry, so drift is best
handled explicitly by comparing `render(canonical)` with the sibling file;
normal validation must ignore it.

Add `experience/markdown.py` with a pure `render_markdown(document)`
function. Storage renders the post-update mapping and writes the canonical
YAML and projection under the existing report lock. Canonical replacement is
performed first; if the Markdown replacement fails, canonical YAML remains
valid and authoritative, the command fails truthfully, and explicit render
repairs the projection.

Add `forge experience render FER-####` and `forge experience render --all`.
The explicit command can run while FER is disabled so historical reports can
be migrated without affecting normal disabled workflows.

### Rendering decisions

- Header is `# <report-id>` because schema @1 has no title field.
- Context is a stable source list with readable labels for known keys.
- Summary is derived only from list lengths and omitted when empty.
- Arrays preserve canonical order; optional fields and empty sections are
  omitted.
- Text is escaped as plain text, not interpreted as author Markdown; line
  breaks remain readable without creating headings, links, or lists.
- IDs and paths/links are shown exactly as stored.
- A quiet generated-file comment appears at the beginning.

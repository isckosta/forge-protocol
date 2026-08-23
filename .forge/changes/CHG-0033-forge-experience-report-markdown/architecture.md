---
forge:
  artifact: architecture
  schema: 1
change: CHG-0033
status: complete
---

# Architecture — CHG-0033 Forge Experience Report Markdown

## Solution Summary

Add `src/forge_cli/experience/markdown.py` as a pure projection boundary. Its
renderer accepts the already validated canonical report mapping and returns
deterministic Markdown. It performs no I/O and does not construct or infer FER
data.

Keep `ExperienceStorage` responsible for canonical validation, locking, and
persistence. After appending an entry, storage renders the candidate document
and prepares canonical YAML plus Markdown sibling outputs. It flushes/fsyncs
temporary files and replaces YAML first, Markdown second. If the second
replacement fails, YAML remains valid and authoritative; the command reports
an incomplete projection rather than claiming success.

Add an explicit render operation to `experience_cli.py`. It reads only
canonical `FER-*.yml`, validates with the existing validator, calls the pure
renderer, and writes the sibling projection. It supports one report ID and
`--all`; it is usable while FER is disabled for historical/recovery work.

## Components and Interfaces

- `experience/markdown.py`: `render_markdown(document: Mapping[str, Any]) -> str`.
- `experience/storage.py`: render candidate mappings and persist derived output
  while preserving locks, IDs, symlink checks, and existing errors.
- `experience_cli.py`: explicit render command and shared canonical loading.
- Renderer unit tests plus FER/CLI integration tests.
- FER documentation and generated example Markdown.

## Data Flow

```text
canonical FER YAML -> existing semantic validator -> in-memory mapping
                                      |                 |
                               YAML serializer    pure Markdown renderer
                                      |                 |
                               canonical file       sibling .md
```

The renderer never consumes Markdown. If files diverge, canonical YAML wins
and explicit render regenerates the projection.

## Rendering Contract

- Begin with `<!-- Generated from the canonical Forge Experience Report. Do not edit manually. -->`.
- Use `# <report>`; do not invent a title because schema @1 has none.
- Render `source` under `## Context` in stable mapping order with readable
  labels and exact values.
- Render a count-only `## Summary` when evidence lists are non-empty.
- Render ordered observations under `## Observations`, then optional positive
  evidence and follow-up candidates.
- Escape Markdown control characters in canonical text while preserving line
  breaks; do not interpret user text as Markdown.
- End with exactly one newline; never include current time or file order.

## Failure Handling

Rendering and serialization failures occur before canonical replacement where
possible. A failure during the second replacement can leave valid canonical
YAML with missing/stale Markdown; this recoverable partial state is reported
with a non-zero error. No Change state, normal validation, or disabled
workflow is modified.

## Compatibility

Missing Markdown is backward-compatible. Existing YAML is not rewritten by
normal commands. Explicit `forge experience render --all` is the migration
path for historical reports.

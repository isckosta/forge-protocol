---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0033
status: complete
---

# Knowledge Capture — CHG-0033 Forge Experience Report Markdown

## What Changed

FER now has a pure Markdown projection generated from canonical YAML. The
existing flat shared report directory uses `FER-####.md` siblings to avoid a
shared `report.md` collision. The renderer is deterministic, escapes
contributor text as plain text, and explicit render repairs missing/drifted
projections.

## Durable Knowledge

The current FER layout is a shared directory of canonical `FER-####.yml`
files, not one directory per report. A derived Markdown filename must avoid a
shared `report.md` collision. Canonical persistence can succeed while derived
write fails; this is recoverable by explicit render and does not invalidate
the YAML source of truth.

## Consequences for Future Changes

Future FER projections must remain one-way transformations. Markdown must not
become a second schema or an input to tooling, and normal Forge validation
must remain independent of missing or drifted projections.

## References

- `.forge/changes/CHG-0030-forge-experience-reporting/architecture.md`
- `docs/experience-reporting.md`
- `src/forge_cli/experience/storage.py`

---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0035
status: pending
---

# Knowledge Capture — CHG-0035 Automatic Material Observation Capture

## What Changed

FER now has a conservative policy/recorder boundary for mechanically
observable Adapter conformance facts. Automatic observations remain uncertain,
bounded, deduplicated, opt-in, and non-normative.

## Durable Knowledge

The repository does not currently own a lifecycle execution engine. Approval,
lifecycle, review-authority, workaround, and root-cause observations cannot be
honestly auto-detected here and must remain manual or assisted.

## Consequences for Future Changes

Future detectors must be added only when Forge owns a structured boundary that
can establish the fact. New detectors must not use exceptions, test failures,
or exit codes as generic FER triggers.

## References

- `docs/experience-reporting.md`
- `src/forge_cli/experience/capture.py`
- `src/forge_cli/experience/recorder.py`

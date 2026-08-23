---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0030
status: complete
---

# Knowledge Capture — Forge Experience Reporting

## What Changed

Forge now has optional contributor-only FER configuration and Git-native
reports, with structured observations, positive evidence, safe context,
atomic persistence, explicit validation, and non-binding Adapter guidance.

## Durable Knowledge

Contributor tooling is deliberately stored outside `.forge/changes/` so
experience evidence cannot be mistaken for normative Change state. Lazy
creation avoids empty reports; the first report path is reused explicitly with
`--report` for additional entries from one execution. Unknown provenance is
left unknown, and report failures remain isolated from Change state.

## Consequences for Future Changes

Maintainers can triage `dogfooding/reports/` manually and decide whether an
observation warrants an Issue, RFC, or Change. FER does not prioritize or
automate that decision. Future tooling must preserve the default-off,
local-only, non-normative boundary.

The repository contains one historical provenance record with an abbreviated
Git subject SHA. The validator now treats that exact legacy shape as a
migration marker only when a later complete record has the abbreviated value
as an exact prefix; unrelated malformed or non-matching history still fails
closed. This preserves immutable subject identity while allowing old local
metadata to converge.

## References

- `docs/experience-reporting.md`
- `dogfooding/reports/FER-0001.yml`
- `src/forge_cli/experience/`

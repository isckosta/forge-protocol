---
forge:
  artifact: specification_review
  schema: 1
change: CHG-0030
status: complete
---

# Specification Review — Forge Experience Reporting

## Verdict

**PASS — repository-grounded adversarial review completed before Architecture.**

## Review focus

The reviewer must challenge default-off behavior, accidental Protocol coupling,
privacy/data minimization, lazy creation, report/observation ID collision,
concurrency, failure isolation, unknown provenance, and whether CLI surface is
proportional.

## Findings and resolutions

- **SR-001 (resolved):** The design did not specify how a report is created
  without becoming generic CRUD. Resolution: `record` accepts one structured
  document from a path/stdin and lazy creation is tied to the first accepted
  observation or positive evidence.
- **SR-002 (resolved):** Provenance could be confused with Change review
  provenance. Resolution: FER uses a separate safe context model and never
  mutates or reuses Change `provenance.yml` authority.
- **SR-003 (resolved):** Invalid configuration could affect normal validation.
  Resolution: only explicit `experience` commands resolve
  `.forge/contributor.yml`; normal `forge validate` ignores it.
- **SR-004 (resolved):** Concurrent writes could lose observations. Resolution:
  exclusive ID reservation, per-report lock, atomic replacement, and
  injected failure tests are required.

## Claims to verify

- No existing project is required to configure or validate FER.
- `.forge/contributor.yml` is read only by FER commands and is absent unless a
  contributor opts in.
- A report contains observations rather than execution logs or Review findings.
- Human triage remains the only path from evidence to Issue, RFC, or Change.

## Conclusion

The Specification is internally consistent, preserves the Protocol boundary,
and is ready for Architecture and Test Strategy. Implementation remains
blocked by the human Plan approval boundary.
